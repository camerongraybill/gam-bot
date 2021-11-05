from discord.ext.commands import Bot
from . import settings
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord.ext.commands import Context


def build_bot() -> "Bot[Context]":
    b = Bot(command_prefix=settings.COMMAND_PREFIX)
    for cog_cls in settings.COGS:
        b.add_cog(cog_cls(b))
    return b
