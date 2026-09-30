import asyncio
from graids_db import engine
from graids_db.relay_message_copies import (
    delete_relay_message_copies,
    get_relay_message_copies,
    replace_relay_message_copies,
)


def test_replace_get_delete_mapping_lifecycle():
    async def scenario():
        await engine.connect_demo()
        try:
            await replace_relay_message_copies(
                surface="test",
                source_guild_id=1,
                source_channel_id=10,
                source_message_id=100,
                destinations=[
                    (2, 20, (201, 202)),
                    (3, 30, (301,)),
                ],
            )
            rows = await get_relay_message_copies("test", 100)
            assert [(r.destination_guild_id, r.chunk_index) for r in rows] == [
                (2, 0), (2, 1), (3, 0)
            ]

            await replace_relay_message_copies(
                surface="test",
                source_guild_id=1,
                source_channel_id=10,
                source_message_id=100,
                destinations=[(2, 20, (203,))],
            )
            rows = await get_relay_message_copies("test", 100)
            assert [r.destination_message_id for r in rows] == [203]

            deleted = await delete_relay_message_copies("test", 100)
            assert deleted == 1
            assert await get_relay_message_copies("test", 100) == []
        finally:
            await engine.close_demo()

    asyncio.run(scenario())
