from discord import Intents, Game
from discord.ext.commands import Bot
from pkg_resources import get_distribution

from . import settings
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord.ext.commands import Context


def build_bot() -> "Bot[Context]":
    b = Bot(
        command_prefix=settings.COMMAND_PREFIX,
        intents=Intents.all(),
        activity=Game(name=f"{settings.COMMAND_PREFIX}help v{get_distribution('gam_bot').version}"),
    )
    for cog_cls in settings.COGS:
        b.add_cog(cog_cls(b))
    return b
