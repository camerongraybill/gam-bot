from typing import Any, Sequence

from discord.app_commands import Command
from discord.ext import commands
from discord.ext.commands import Bot, Context

from discord_bot.checks import is_in_channel
from . import settings

def _build_command(name: str, channels: set[str] | None, response: Sequence[str]) -> Command[Any, Any, Any]:
    async def _(ctx: Context[Bot]) -> None:
        for resp in response:
            await ctx.send(resp)

    f = _
    f.__name__ = name
    if channels:
        f = is_in_channel(channels)(f)

    return commands.command(name=name)(f)

def add_easy_commands(bot: Bot) -> None:
    for command in settings.COMMANDS:
        bot.add_command(_build_command(*command))