"""Local-only sample showing how original GRAIDS relay-copy records are used.

The transport here is intentionally invented for the demonstration: it sends
nothing to Discord, has no authentication or network code, and generates
fabricated message identifiers. This is not the production relay worker.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from graids_db.relay_message_copies import (
    delete_relay_message_copies,
    get_relay_message_copies,
    replace_relay_message_copies,
)
from .formatting import edited_destination_content, split_text

SURFACE = "raid_thread_demo"
CHUNK_LIMIT = 45  # Short on purpose, so the demo visibly splits text.


@dataclass(frozen=True)
class Destination:
    guild_id: int
    channel_id: int


@dataclass
class FakeTransport:
    """In-memory stand-in for a network; contains synthetic messages only."""
    next_message_id: int = 90_000
    messages: dict[int, str] = field(default_factory=dict)

    def send(self, destination: Destination, text: str) -> int:
        self.next_message_id += 1
        self.messages[self.next_message_id] = text
        return self.next_message_id

    def edit(self, message_id: int, text: str) -> None:
        self.messages[message_id] = text

    def delete(self, message_id: int) -> None:
        self.messages.pop(message_id, None)


async def relay_initial(
    transport: FakeTransport,
    *,
    source_guild_id: int,
    source_channel_id: int,
    source_message_id: int,
    text: str,
    destinations: list[Destination],
) -> None:
    """Fan out a synthetic message and store actual model mappings."""
    mapping_rows = []
    for destination in destinations:
        ids = tuple(
            transport.send(destination, chunk)
            for chunk in split_text(text, CHUNK_LIMIT)
        )
        mapping_rows.append((destination.guild_id, destination.channel_id, ids))

    await replace_relay_message_copies(
        surface=SURFACE,
        source_guild_id=source_guild_id,
        source_channel_id=source_channel_id,
        source_message_id=source_message_id,
        destinations=mapping_rows,
    )


async def relay_edit(
    transport: FakeTransport,
    *,
    source_message_id: int,
    new_content: str,
    raid_labels: tuple[str, ...] = (),
) -> None:
    """Use stored mappings to update synthetic destination messages.

    This is a minimal illustration, *not* a production edit/retry strategy.
    It supports changed chunk counts for the offline demo.
    """
    existing = await get_relay_message_copies(SURFACE, source_message_id)
    if not existing:
        return
    text = edited_destination_content(new_content, raid_labels)
    new_chunks = split_text(text, CHUNK_LIMIT) if text else []

    grouped = defaultdict(list)
    for row in existing:
        grouped[(row.destination_guild_id, row.destination_channel_id)].append(row)

    updated_destinations = []
    for (guild_id, channel_id), rows in grouped.items():
        rows = sorted(rows, key=lambda row: row.chunk_index)
        current_ids = [row.destination_message_id for row in rows]
        retained_ids = []
        for i, chunk in enumerate(new_chunks):
            if i < len(current_ids):
                transport.edit(current_ids[i], chunk)
                retained_ids.append(current_ids[i])
            else:
                retained_ids.append(transport.send(Destination(guild_id, channel_id), chunk))
        for leftover_id in current_ids[len(new_chunks):]:
            transport.delete(leftover_id)
        updated_destinations.append((guild_id, channel_id, tuple(retained_ids)))

    first = existing[0]
    await replace_relay_message_copies(
        surface=SURFACE,
        source_guild_id=first.source_guild_id,
        source_channel_id=first.source_channel_id,
        source_message_id=source_message_id,
        destinations=updated_destinations,
    )


async def relay_delete(
    transport: FakeTransport,
    *,
    source_message_id: int,
) -> int:
    """Remove synthetic copies and clear their persistent mapping."""
    copies = await get_relay_message_copies(SURFACE, source_message_id)
    for copy in copies:
        transport.delete(copy.destination_message_id)
    return await delete_relay_message_copies(SURFACE, source_message_id)
