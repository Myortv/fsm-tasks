import asyncio


import pyrogram
from pyrogram import Client


from core.configs import settings
from repository.db import init_asyncpg, stop_asyncpg

from bot import (
    user,
    user_login,
    all_tasks,
    new_task,
    system,
)


async def main():
    try:
        await init_database()
        app = await init_pyrogram()

        all_tasks.init(app)
        new_task.init(app)
        user_login.init(app)
        user.init(app)
        system.init(app)

        await pyrogram.idle()
    except Exception as e:
        await stop_asyncpg()
        if app:
            await app.stop()
        raise e


async def init_database():
    await init_asyncpg(
        settings.POSTGRES_DB,
        settings.POSTGRES_HOST,
        settings.POSTGRES_USER,
        settings.POSTGRES_PASSWORD,
    )


async def init_pyrogram(

):
    app = Client(
        "bot",
        settings.PYROGRAM_API_ID,
        settings.PYROGRAM_API_HASH,
        bot_token=settings.PYROGRAM_BOT_TOKEN,
    )
    await app.start()
    return app


asyncio.run(main())
