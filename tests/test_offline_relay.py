import asyncio
from graids_db import engine
from graids_db.relay_message_copies import get_relay_message_copies
from graids_demo.offline_relay import (
    SURFACE, Destination, FakeTransport, relay_initial, relay_edit, relay_delete
)


def test_synthetic_fanout_edit_delete():
    async def scenario():
        await engine.connect_demo()
        try:
            transport = FakeTransport()
            await relay_initial(
                transport,
                source_guild_id=1,
                source_channel_id=10,
                source_message_id=100,
                text="A moderately long synthetic relay message for two destinations.",
                destinations=[Destination(2, 20), Destination(3, 30)],
            )
            rows = await get_relay_message_copies(SURFACE, 100)
            assert len(rows) >= 2
            assert len({r.destination_guild_id for r in rows}) == 2

            await relay_edit(
                transport,
                source_message_id=100,
                new_content="Edited synthetic message",
                raid_labels=("Demo",),
            )
            assert transport.messages
            assert all("<@&" not in value for value in transport.messages.values())

            removed = await relay_delete(transport, source_message_id=100)
            assert removed > 0
            assert transport.messages == {}
            assert await get_relay_message_copies(SURFACE, 100) == []
        finally:
            await engine.close_demo()

    asyncio.run(scenario())
