"""Run with: python -m graids_demo"""
import asyncio

from graids_db import engine
from graids_db.relay_message_copies import get_relay_message_copies
from .offline_relay import (
    SURFACE,
    Destination,
    FakeTransport,
    relay_delete,
    relay_edit,
    relay_initial,
)


async def main() -> None:
    await engine.connect_demo()
    try:
        transport = FakeTransport()
        destinations = [Destination(2001, 3001), Destination(2002, 3002)]
        message_id = 1001

        print("1. Initial fan-out to TWO synthetic destination channels")
        await relay_initial(
            transport,
            source_guild_id=2000,
            source_channel_id=3000,
            source_message_id=message_id,
            text="Looking for a raid group. Can anyone join this evening?",
            destinations=destinations,
        )
        copies = await get_relay_message_copies(SURFACE, message_id)
        print(f"   Persisted {len(copies)} destination chunk mappings")
        print(f"   Synthetic messages: {transport.messages}")

        print("2. Synchronize a source edit with non-pinging raid labels")
        await relay_edit(
            transport,
            source_message_id=message_id,
            new_content="Group is now full. Thanks!",
            raid_labels=("example_raid",),
        )
        print(f"   Updated synthetic messages: {transport.messages}")

        print("3. Synchronize the source deletion")
        removed = await relay_delete(transport, source_message_id=message_id)
        print(f"   Removed {removed} stored mappings")
        print(f"   Remaining synthetic messages: {transport.messages}")
    finally:
        await engine.close_demo()


if __name__ == "__main__":
    asyncio.run(main())
