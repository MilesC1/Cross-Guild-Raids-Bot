from __future__ import annotations

import time
from collections.abc import Iterable, Sequence

from sqlalchemy import Index, UniqueConstraint, delete, select
from sqlalchemy.orm import Mapped, mapped_column

from . import engine
from .models import Base


class RelayMessageCopy(Base):
    """One webhook copy of a source Discord bridge message."""

    __tablename__ = "relay_message_copies"
    __table_args__ = (
        Index(
            "ix_relay_message_copies_source",
            "surface",
            "source_message_id",
        ),
        UniqueConstraint(
            "destination_message_id",
            name="uq_relay_message_copy_destination_message",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    surface: Mapped[str] = mapped_column(nullable=False)
    source_guild_id: Mapped[int] = mapped_column(nullable=False)
    source_channel_id: Mapped[int] = mapped_column(nullable=False)
    source_message_id: Mapped[int] = mapped_column(nullable=False)
    destination_guild_id: Mapped[int] = mapped_column(nullable=False)
    destination_channel_id: Mapped[int] = mapped_column(nullable=False)
    destination_message_id: Mapped[int] = mapped_column(nullable=False)
    chunk_index: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[int] = mapped_column(nullable=False)


async def get_relay_message_copies(
    surface: str,
    source_message_id: int,
) -> list[RelayMessageCopy]:
    """Return all known webhook copies for one bridged source message."""

    async with engine.transaction() as session:
        result = await session.execute(
            select(RelayMessageCopy)
            .where(
                RelayMessageCopy.surface == surface,
                RelayMessageCopy.source_message_id == source_message_id,
            )
            .order_by(
                RelayMessageCopy.destination_guild_id,
                RelayMessageCopy.destination_channel_id,
                RelayMessageCopy.chunk_index,
            )
        )
        return list(result.scalars().all())


async def delete_relay_message_copies(
    surface: str,
    source_message_id: int,
) -> int:
    """Delete every destination mapping for one original bridge message."""

    async with engine.transaction() as session:
        result = await session.execute(
            delete(RelayMessageCopy).where(
                RelayMessageCopy.surface == surface,
                RelayMessageCopy.source_message_id == source_message_id,
            )
        )
        return int(result.rowcount or 0)


async def replace_relay_message_copies(
    *,
    surface: str,
    source_guild_id: int,
    source_channel_id: int,
    source_message_id: int,
    destinations: Iterable[tuple[int, int, Sequence[int]]],
) -> None:
    """Replace the destination-message mapping for one source message.

    ``destinations`` contains ``(guild_id, channel_or_thread_id, message_ids)``.
    One source message may be split into multiple webhook messages, so each
    destination stores a stable chunk index as well as the Discord message ID.
    """

    now = int(time.time())
    rows: list[RelayMessageCopy] = []

    for destination_guild_id, destination_channel_id, message_ids in destinations:
        for chunk_index, destination_message_id in enumerate(message_ids):
            rows.append(
                RelayMessageCopy(
                    surface=surface,
                    source_guild_id=source_guild_id,
                    source_channel_id=source_channel_id,
                    source_message_id=source_message_id,
                    destination_guild_id=destination_guild_id,
                    destination_channel_id=destination_channel_id,
                    destination_message_id=destination_message_id,
                    chunk_index=chunk_index,
                    created_at=now,
                )
            )

    async with engine.transaction() as session:
        await session.execute(
            delete(RelayMessageCopy).where(
                RelayMessageCopy.surface == surface,
                RelayMessageCopy.source_message_id == source_message_id,
            )
        )
        session.add_all(rows)
