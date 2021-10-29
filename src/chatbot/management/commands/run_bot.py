from django.core.management.base import BaseCommand
from chatbot.bot import bot
from typing import Any
from django.conf import settings


class Command(BaseCommand):
    help = "Runs the chatbot"

    # pylint: disable=unused-argument
    def handle(self, *args: Any, **options: Any) -> None:
        if settings.DISCORD_KEY is None:
            raise Exception("DISCORD_KEY is not set")
        bot.run(settings.DISCORD_KEY)
