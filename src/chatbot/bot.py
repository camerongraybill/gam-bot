from logging import getLogger
from typing import Optional, Sequence
from urllib.parse import urlencode

from discord import GroupChannel, RawReactionActionEvent, TextChannel
from discord.channel import DMChannel
from discord.ext import commands
from discord.ext.commands import Bot, Context
from django.conf import settings

from .models import GamUser

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord.ext.commands import Command
    from discord.ext.commands.core import _CheckDecorator

logger = getLogger(__name__)

bot = Bot(command_prefix="!")


def is_in_channel(
    command_channels: Optional[set[str]],
) -> "_CheckDecorator":
    @commands.check
    async def predicate(ctx: Context) -> bool:
        if command_channels and ctx.channel and not isinstance(ctx.channel, DMChannel):
            return ctx.channel.name in command_channels
        return True

    return predicate


def make_easy_command(
    command_keyword: str,
    command_channels: Optional[set[str]],
    command_responses: Sequence[str],
) -> None:
    @bot.command(name=command_keyword)
    @is_in_channel(command_channels)
    async def _easy_message_function(ctx: Context) -> None:
        for resp in command_responses:
            await ctx.send(resp)


for keyword, channels, responses in settings.EASY_MESSAGES:
    make_easy_command(keyword, channels, responses)


@bot.command()
async def lmgtfy(ctx: Context) -> None:
    message = ctx.message
    chan = message.channel
    if message.reference is not None and message.reference.message_id is not None:
        # use message being replied to
        original = await chan.fetch_message(id=message.reference.message_id)
    else:
        # use message immediately before this one
        original = await chan.history(
            limit=1, before=message, oldest_first=False
        ).next()

    query = urlencode({"q": original.content})
    await original.reply(f"https://lmgtfy.app/?{query}")


@bot.command()
async def show_score(ctx: Context) -> None:
    user_to_lookup, _ = await GamUser.objects.async_get_or_create(
        discord_id=ctx.message.author.id
    )
    await ctx.send(f"Your social score is currently {user_to_lookup.social_score}")


@bot.event
async def on_raw_reaction_add(payload: RawReactionActionEvent) -> None:
    channel = await bot.fetch_channel(payload.channel_id)
    if isinstance(channel, (TextChannel, GroupChannel)):
        message = await channel.fetch_message(payload.message_id)
        if message.author.id != payload.user_id:
            user, _ = await GamUser.objects.async_get_or_create(
                discord_id=message.author.id
            )
            emoji_str = str(payload.emoji)
            logger.debug("User's current social score is %d", user.social_score)
            if emoji_str == settings.ADD_SOCIAL_SCORE:
                user.social_score += 1
            elif emoji_str == settings.REMOVE_SOCIAL_SCORE:
                user.social_score -= 1
            logger.debug("User's new social score is %d", user.social_score)
            await user.async_save()


@bot.event
async def on_raw_reaction_remove(payload: RawReactionActionEvent) -> None:
    channel = await bot.fetch_channel(payload.channel_id)
    if isinstance(channel, (TextChannel, GroupChannel)):
        message = await channel.fetch_message(payload.message_id)
        if message.author.id != payload.user_id:
            user, _ = await GamUser.objects.async_get_or_create(
                discord_id=message.author.id
            )
            emoji_str = str(payload.emoji)
            logger.debug("User's current social score is %d", user.social_score)
            if emoji_str == settings.ADD_SOCIAL_SCORE:
                user.social_score -= 1
            elif emoji_str == settings.REMOVE_SOCIAL_SCORE:
                user.social_score += 1
            logger.debug("User's new social score is %d", user.social_score)
            await user.async_save()
