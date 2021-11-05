from typing import Optional, Sequence, TYPE_CHECKING

from discord.ext import commands
from discord.ext.commands import Context

from discord_bot.cog import BaseCog
from discord_bot.checks import is_in_channel
from . import settings

if TYPE_CHECKING:
    from discord.ext.commands import Bot, Command


class EasyCog(BaseCog):
    def __init__(self, bot: "Bot[Context]") -> None:
        for cmd in settings.COMMANDS:
            setattr(self, cmd[0], build_command(*cmd))

        super().__init__(bot)


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
