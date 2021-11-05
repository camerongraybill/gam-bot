from typing import Optional, Sequence

from discord.ext import commands
from discord.ext.commands import Context, Bot, Command

from discord_bot.cog import BaseCog
from discord_bot.checks import is_in_channel
from . import settings


def build_command(
    name: str,
    channels: Optional[set[str]],
    response: Sequence[str]
) -> Command[Context]:

    async def _(self: EasyCog, ctx: Context) -> None:
        for resp in response:
            await ctx.send(resp)

    f = _
    f.__name__ = name
    if channels:
        f = is_in_channel(channels)(f)

    return commands.command(name=name)(f)


class EasyCog(BaseCog):
    def __init__(self, bot: Bot) -> None:
        for cmd in settings.COMMANDS:
            setattr(self, cmd[0], build_command(*cmd))

        super().__init__(bot)
