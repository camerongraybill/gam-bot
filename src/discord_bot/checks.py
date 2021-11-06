from typing import Collection
from discord.channel import DMChannel
from discord.ext import commands
from discord.ext.commands.context import Context

from django.conf import settings

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord.ext.commands.core import _CheckDecorator


def is_in_channel(
    command_channels: Collection[str],
) -> "_CheckDecorator":
    @commands.check
    async def predicate(ctx: Context) -> bool:
        if command_channels and ctx.channel and not isinstance(ctx.channel, DMChannel):
            return ctx.channel.name in command_channels
        return True

    return predicate


def only_debug() -> "_CheckDecorator":
    @commands.check
    # pylint: disable=unused-argument
    async def predicate(ctx: Context) -> bool:
        return settings.DEBUG

    return predicate
