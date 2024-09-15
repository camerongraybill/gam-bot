from __future__ import annotations

from typing import Optional, Sequence, Any

from discord.ext import commands
from discord.ext.commands import Context

from discord_bot.cog import BaseCog
from discord_bot.checks import is_in_channel
from . import settings

from discord.ext.commands import Command, Bot


class EasyCog(BaseCog):
    """ Attributes are dynamically defined on import """

def build_command(
    name: str, channels: Optional[set[str]], response: Sequence[str]
) -> None:
    async def _(self: EasyCog, ctx: Context[Bot]) -> None:
        for resp in response:
            await ctx.send(resp)

    f = _
    f.__name__ = name
    if channels:
        f = is_in_channel(channels)(f)

    setattr(EasyCog, name, commands.command(name=name)(f))

for cmd in settings.COMMANDS:
    build_command(*cmd)
