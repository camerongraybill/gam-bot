from tortoise import Tortoise

from gam_bot.settings import DB_CONN_STR


async def init_db() -> None:
    await Tortoise.init(db_url=DB_CONN_STR, modules={"models": ["gam_bot.models"]})
    await Tortoise.generate_schemas()
