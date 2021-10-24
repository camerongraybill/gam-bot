from logging import getLogger

import discord
from discord import Message

from gam_bot.easy_messages import easy_message_processor
from gam_bot.settings import TRIGGER

logger = getLogger(__name__)


class Bot(discord.Client):
    async def on_message(self, message: Message) -> None:
        if message.content.startswith(TRIGGER):
            stripped_content = message.content.strip().removeprefix(TRIGGER)
            logger.info("Got message %s", message)
            if easy_response := easy_message_processor(stripped_content, message.channel.name):
                for response in easy_response:
                    await message.channel.send(response)
            else:
                await message.channel.send(f"Unexpected command {stripped_content}")
