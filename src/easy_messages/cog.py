from typing import Optional, Sequence, TYPE_CHECKING

from discord.ext import commands
from discord.ext.commands import Context

from discord_bot.cog import BaseCog
from discord_bot.checks import is_in_channel
from . import settings

if TYPE_CHECKING:
    from discord.ext.commands import Command


class EasyCog(BaseCog):
    def __new__(cls, *args, **kwargs):
        for cmd in settings.COMMANDS:
            cls.__cog_commands__.append(build_command(*cmd))
        return super().__new__(cls, *args, **kwargs)


def build_command(
    name: str, channels: Optional[set[str]], response: Sequence[str]
) -> "Command[Context]":

    # pylint: disable=unused-argument
    async def _(self: EasyCog, ctx: Context) -> None:
        for resp in response:
            await ctx.send(resp)

    f = _
    f.__name__ = name
    if channels:
        f = is_in_channel(channels)(f)

    return commands.command(name=name)(f)
