from logging import getLogger

import discord
from discord import Message, GroupChannel, TextChannel

from gam_bot.command import REGISTRY
from gam_bot.settings import TRIGGER

logger = getLogger(__name__)

class Bot(discord.Client):

    @staticmethod
    async def on_message(message: Message) -> None:
        if message.content.startswith(TRIGGER):
            stripped_content = message.content.strip().removeprefix(TRIGGER)
            logger.info("Got message %s", message)
            try:
                response = REGISTRY.dispatch(
                    stripped_content,
                    message.channel.name
                    if isinstance(message.channel, (TextChannel, GroupChannel))
                    else None,
                )
                for response in response:
                    await message.channel.send(response)
            except ValueError:
                await message.channel.send(f"Unexpected command {stripped_content}")
