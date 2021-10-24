from asyncio import ensure_future

from aiohttp.abc import Application
from aiohttp.web import run_app

from .db import init_db
from .settings import DISCORD_KEY, PORT, HOST
from .logs import setup_logging


setup_logging()

from .bot import Bot
from .webserver import get_app


async def app_factory() -> Application:
    await init_db()
    ensure_future(Bot().start(DISCORD_KEY))

    return get_app()


def main() -> None:
    run_app(app_factory(), host=HOST, port=PORT)


if __name__ == "__main__":
    main()
