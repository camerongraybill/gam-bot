from discord.ext.commands import Bot
from . import settings


def build_bot() -> Bot:
    b = Bot(command_prefix=settings.COMMAND_PREFIX)
    for cog_cls in settings.COGS:
        b.add_cog(cog_cls(b))
    return b
