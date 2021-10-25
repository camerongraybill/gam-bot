from logging import getLogger
from os import stat
from typing import Text

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
            else:
                await message.channel.send(f"Unexpected command {stripped_content}")
    
    @staticmethod
    @sync_to_async
    def get_gam_user(id: int) -> GamUser:
        GamUser.objects.get_or_create(discord_id=id)
    
    @staticmethod
    @sync_to_async
    def save_gam_user(user: GamUser) -> None:
        user.save()
    
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent) -> None:
        channel = await self.fetch_channel(payload.channel_id)
        if isinstance(channel, (TextChannel, GroupChannel)):
            message = await channel.fetch_message(payload.message_id)
            user: GamUser = await Bot.get_gam_user(message.author.id)
            logger.info(str(payload.emoji) == settings.ADD_SOCIAL_SCORE)

