from django.core.management.base import BaseCommand, CommandParser
from discord_bot import settings
from discord_bot.bot import build_bot


class Command(BaseCommand):
    help = "Runs the discord bot"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--discord-key",
            type=str,
            required=True,
            default=settings.KEY,

        )

    # pylint: disable=unused-argument
    def handle(self, discord_key: str) -> None:
        build_bot().run(discord_key)
