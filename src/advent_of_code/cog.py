from datetime import date
from html.parser import HTMLParser
from logging import getLogger
from typing import Optional, Union

from discord import TextChannel, Message, DMChannel, GroupChannel
from discord.ext import commands, tasks
from discord.ext.commands import Context, Bot

from advent_of_code import settings
from discord_bot.cog import BaseCog
from aiohttp.client import ClientSession
from yarl import URL
from django.utils.timezone import now
from discord.utils import get
logger = getLogger(__name__)

async def create_thread(channel: TextChannel, name: str, minutes: int, message: Message) -> None:
    async with ClientSession() as session:
        async with session.post(
            url=f"https://discord.com/api/v9/channels/{channel.id}/messages/{message.id}/threads",
            json={
                "name": name,
                "type": 11,
                "auto_archive_duration": minutes
            },
            headers={
                "authorization": 'Bot ' + channel._state.http.token,
                "content-type": "application/json"
            }
        ):
            pass


class _AOCHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.last_title = None
        self._seen_first_h2 = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == 'h2':
            self._seen_first_h2 = True

    def reset(self) -> None:
        self._seen_first_h2 = False
        self.last_title = None
        super().reset()

    def handle_data(self, data: str) -> None:
        if self._seen_first_h2 and self.last_title is None:
            self.last_title = data.strip('- ')


PARSER = _AOCHTMLParser()

AOC_BASE_URL = URL('https://adventofcode.com/')


class AdventOfCodeCog(BaseCog):
    def __init__(self, bot: "Bot[Context]") -> None:
        super().__init__(bot)
        # pylint: disable=no-member
        self.check_post_for_day.start()
        self._last_posted_day = None

    @tasks.loop(minutes=1.0)
    async def check_post_for_day(self) -> None:
        now_dt = now()
        today = now_dt.date()
        if today != self._last_posted_day and now_dt.hour == 5 and today.month == 12 and today.day <= 25:
            await self._send_aoc_message(get(self.bot.get_all_channels(), name=settings.SUBSCRIBED_CHANNEL), today)
            self._last_posted_day = today

    @check_post_for_day.before_loop  # type: ignore
    async def before_check_post_for_day(self) -> None:
        logger.info("Waiting for bot to start before checking to post AOC message")
        await self.bot.wait_until_ready()

    @staticmethod
    async def _build_aoc_message(
        day: date,
    ) -> tuple[str, Optional[str]]:
        prompt_link = AOC_BASE_URL / str(day.year) / 'day' / str(day.day)
        input_link = prompt_link / 'input'
        async with ClientSession() as session:
            async with session.get(prompt_link) as response:
                if not response.ok or day.month != 12:
                    return f"Invalid day to get aoc prompt for: {day}", None
                PARSER.feed(await response.text())
                title = PARSER.last_title
                PARSER.reset()
        return f"{title}\nPrompt link: {str(prompt_link)}\nInput link: {str(input_link)}\nReply in thread with solutions and discussion!", f"{title} discussion"

    @classmethod
    async def _send_aoc_message(
        cls,
        channel: Union[TextChannel, DMChannel, GroupChannel],
        day: date,
    ) -> None:
        message_text, thread_name = await cls._build_aoc_message(day)
        sent_message = await channel.send(message_text)
        if isinstance(channel, TextChannel) and thread_name is not None:
            await create_thread(channel, thread_name, 60*24*3, sent_message)

    @commands.command(help="Post an advent of code message")
    async def aoc_message(self, ctx: Context, day: int, year: int) -> None:
        await self._send_aoc_message(ctx.channel, date(day=day, year=year, month=12))

