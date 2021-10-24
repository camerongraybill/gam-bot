from django.core.management.base import BaseCommand
from chatbot.bot import Bot
from typing import Any
from django.conf import settings


class Command(BaseCommand):
    help = "Runs the chatbot"

    # pylint: disable=unused-argument
    def handle(self, *args: Any, **options: Any) -> None:
        assert settings.DISCORD_KEY is not None
        Bot().run(settings.DISCORD_KEY)
