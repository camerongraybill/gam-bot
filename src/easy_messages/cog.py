from __future__ import annotations

from typing import Optional, Sequence, Any

from discord.ext import commands
from discord.ext.commands import Context

from discord_bot.cog import BaseCog
from discord_bot.checks import is_in_channel
from . import settings

from discord.ext.commands import Command, Bot


class EasyCog(BaseCog):
    def __new__(cls, bot: Bot) -> Any:
        for cmd in settings.COMMANDS:
            cls.__cog_commands__.append(build_command(*cmd))
        return super().__new__(cls, bot)


def build_command(
    name: str, channels: Optional[set[str]], response: Sequence[str]
) -> Command[EasyCog, Any, Any]:
    async def _(self: EasyCog, ctx: Context[Bot]) -> None:
        for resp in response:
            await ctx.send(resp)

    f = _
    f.__name__ = name
    if channels:
        f = is_in_channel(channels)(f)

    return commands.command(name=name)(f)
