from importlib.metadata import version

from discord import Intents, Activity, ActivityType
from discord.ext.commands import Bot

from easy_messages.add_commands import add_easy_commands
from . import settings


async def build_bot() -> Bot:
    b = Bot(
        command_prefix=settings.COMMAND_PREFIX,
        intents=Intents.all(),
        activity=Activity(
            type=ActivityType.watching,
            name=f"{settings.COMMAND_PREFIX}help - v{version('gam_bot')}",
        ),
    )
    for cog_cls in settings.COGS:
        await b.add_cog(cog_cls(b))
    add_easy_commands(b)
    return b
