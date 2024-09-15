from logging import getLogger
import asyncio
import datetime
import dateparser
from discord.ext import commands
from discord.ext.commands import Bot, Context
from discord_bot.cog import BaseCog
from discord_bot.models import DiscordUser
from .models import Reminder

logger = getLogger(__name__)


class RemindMeCog(BaseCog):
    def __init__(self, bot: "Bot[Context]") -> None:
        super().__init__(bot)

    async def cog_load(self) -> None:
        await self.bot.wait_until_ready()
        existing_reminders = Reminder.objects.all()
        start_time = datetime.datetime.now()
        # Check for any reminders that may have expired while the bot was down and send them
        # or create timers for the remaining ones
        existing_reminder: Reminder
        for existing_reminder in existing_reminders:
            if existing_reminder.reminder_time <= start_time:
                await self._send_reminder(existing_reminder)
            else:
                delta = (existing_reminder.reminder_time - start_time).seconds
                self._create_timer(delta, existing_reminder)

    def _create_timer(self, delta: float, reminder: Reminder) -> None:
        logger.info(
            "Reminding %s in %0.2f in channel %d",
            reminder.creator.last_known_account_name,
            delta,
            reminder.initial_channel_id,
        )
        asyncio.get_running_loop().call_later(
            delta, lambda: asyncio.create_task(self._send_reminder(reminder))
        )

    async def _send_reminder(self, reminder: Reminder) -> None:
        channel = self.bot.get_channel(reminder.initial_channel_id)
        if not channel:
            logger.warn(
                "No channel was found for %d, doing nothing.",
                reminder.initial_channel_id,
            )
            await reminder.async_delete()
        await channel.send(
            f'<@{reminder.creator.discord_id}>, I am reminding you about "{reminder.reminder_text}"'
        )
        await reminder.async_delete()

    @commands.command(
        help="Create a reminder to get pinged about something in the future"
    )
    async def remindme(self, ctx: Context, time_text: str, reminder_text: str) -> None:
        settings: dateparser._Settings = {
            "PREFER_DATES_FROM": "future",
            "RELATIVE_BASE": datetime.datetime.now(),
        }
        reminder_time = dateparser.parse(time_text, settings=settings)
        if not reminder_time:
            # We couldn't parse their reminder time so log and let user known
            logger.warn("User provided an invalid reminder time (%s)", time_text)
            await ctx.message.reply(
                "Your reminder time is invalid, please make sure it is correct and try again!"
            )
            return
        discord_user: DiscordUser = await DiscordUser.objects.lookup_user(ctx.author.id)
        reminder = Reminder(
            creator=discord_user,
            reminder_text=reminder_text,
            reminder_time=reminder_time,
            initial_channel_id=ctx.channel.id,
        )
        await reminder.async_save()
        await ctx.channel.send(f"Got it, I will remind you in {time_text}")
        start_time = datetime.datetime.now()
        delta = (reminder_time - start_time).seconds
        self._create_timer(delta, reminder)
