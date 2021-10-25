from logging import getLogger
from urllib.parse import urlencode

import discord
from discord import Message, GroupChannel, TextChannel, RawReactionActionEvent
from asgiref.sync import sync_to_async

from .easy_messages import easy_message_processor
from django.conf import settings
from .models import GamUser

logger = getLogger(__name__)


class Bot(discord.Client):
    @staticmethod
    async def on_message(message: Message) -> None:
        if message.content.startswith(settings.TRIGGER):
            stripped_content = message.content.strip().removeprefix(settings.TRIGGER)
            logger.info("Got message %s", message)
            if easy_response := easy_message_processor(
                stripped_content,
                message.channel.name
                if isinstance(message.channel, (TextChannel, GroupChannel))
                else None,
            ):
                for response in easy_response:
                    await message.channel.send(response)
            elif stripped_content == "show_score":
                user_to_lookup = await Bot.get_gam_user(message.author.id)
                await message.channel.send(
                    f"Your social score is currently {user_to_lookup.social_score}"
                )
            elif stripped_content == "lmgtfy":
                channel = message.channel
                if (
                    message.reference is not None
                    and message.reference.message_id is not None
                ):
                    # use message being replied to
                    original = await channel.fetch_message(
                        id=message.reference.message_id
                    )
                else:
                    # use message immediately before this one
                    original = await channel.history(
                        limit=1, before=message, oldest_first=False
                    ).next()

                query = urlencode({"q": original.content})
                await original.reply(f"https://lmgtfy.app/?{query}")
            else:
                await message.channel.send(f"Unexpected command {stripped_content}")

    @staticmethod
    @sync_to_async
    def get_gam_user(user_id: int) -> GamUser:
        user, _ = GamUser.objects.get_or_create(discord_id=user_id)
        return user

    @staticmethod
    @sync_to_async
    def save_gam_user(user: GamUser) -> None:
        user.save()

    async def on_raw_reaction_add(self, payload: RawReactionActionEvent) -> None:
        channel = await self.fetch_channel(payload.channel_id)
        if isinstance(channel, (TextChannel, GroupChannel)):
            message = await channel.fetch_message(payload.message_id)
            if message.author.id != payload.user_id:
                user: GamUser = await Bot.get_gam_user(message.author.id)
                emoji_str = str(payload.emoji)
                logger.debug("User's current social score is %d", user.social_score)
                if emoji_str == settings.ADD_SOCIAL_SCORE:
                    user.social_score += 1
                elif emoji_str == settings.REMOVE_SOCIAL_SCORE:
                    user.social_score -= 1
                logger.debug("User's new social score is %d", user.social_score)
                await Bot.save_gam_user(user)

    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent) -> None:
        channel = await self.fetch_channel(payload.channel_id)
        if isinstance(channel, (TextChannel, GroupChannel)):
            message = await channel.fetch_message(payload.message_id)
            if message.author.id != payload.user_id:
                user: GamUser = await Bot.get_gam_user(message.author.id)
                emoji_str = str(payload.emoji)
                logger.debug("User's current social score is %d", user.social_score)
                if emoji_str == settings.ADD_SOCIAL_SCORE:
                    user.social_score -= 1
                elif emoji_str == settings.REMOVE_SOCIAL_SCORE:
                    user.social_score += 1
                logger.debug("User's new social score is %d", user.social_score)
                await Bot.save_gam_user(user)
