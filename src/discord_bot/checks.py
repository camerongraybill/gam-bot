from typing import Collection
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands._types import Check
from discord.ext.commands.context import Context

from django.conf import settings


def is_in_channel[T: Bot](
    command_channels: Collection[str],
) -> Check[Context[T]]:
    @commands.check
    async def predicate(ctx: Context[T]) -> bool:
        if command_channels and ctx.channel and hasattr(ctx.channel, "name"):
            return ctx.channel.name in command_channels
        return True

    return predicate


def only_debug[T: Bot]() -> Check[Context[T]]:
    @commands.check
    async def predicate(ctx: Context[T]) -> bool:
        return settings.DEBUG

    return predicate
