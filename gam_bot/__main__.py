from asyncio import create_task
from logging import getLogger

from aiohttp import web
from aiohttp.web import run_app

from .db import init_db, close_db
from .settings import DISCORD_KEY, PORT, HOST
from .logs import setup_logging

setup_logging()

from .bot import Bot
from .webserver import get_app

logger = getLogger(__name__)


async def startup(app: web.Application):
    await init_db()
    app["discord_bot"] = Bot()
    app["bot_task"] = create_task(app["discord_bot"].start(DISCORD_KEY))


async def shutdown(app: web.Application):
    await close_db()
    await app["discord_bot"].close()
    app["bot_task"].cancel()
    await app["bot_task"]


def main() -> None:
    app = get_app()
    app.on_startup.append(startup)
    app.on_cleanup.append(shutdown)
    try:
        run_app(app, host=HOST, port=PORT)
    except RuntimeError as e:
        if "Event loop is closed" not in str(e):
            raise


if __name__ == "__main__":
    main()
