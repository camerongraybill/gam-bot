from typing import Any

from django.core.management.base import BaseCommand, CommandParser
from discord_bot import settings
from discord_bot.bot import build_bot

try:
    from uvloop import run
except ImportError:
    from asyncio import run


class Command(BaseCommand):
    help = "Runs the discord bot"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--discord-key",
            type=str,
            required=settings.KEY is None,
            default=settings.KEY,
        )

    @classmethod
    async def amain(cls, discord_key: str) -> None:
        bot = await build_bot()

        async with bot:
            await bot.start(discord_key)

    def handle(self, *args: Any, discord_key: str, **kwargs: Any) -> None:
        run(self.amain(discord_key))
