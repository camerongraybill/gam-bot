from tortoise import Tortoise

from gam_bot.settings import TORTOISE_ORM


async def init_db() -> None:
    await Tortoise.init(TORTOISE_ORM)
    await Tortoise.generate_schemas()


async def close_db() -> None:
    await Tortoise.close_connections()
