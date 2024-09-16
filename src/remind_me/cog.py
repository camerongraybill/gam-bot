from logging import getLogger
import asyncio
import datetime
import dateparser
import tabulate
from asgiref.sync import sync_to_async
from discord.ext import commands
from discord.ext.commands import Bot, Context
from discord_bot.cog import BaseCog
from .models import Reminder


logger = getLogger(__name__)


LIST_REMINDERS_HEADERS = ["ID", "Reminder Time", "Reminder Text"]


class RemindMeCog(BaseCog):
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        existing_reminders = Reminder.objects.all()
        start_time = datetime.datetime.now(datetime.UTC)
        # Check for any reminders that may have expired while the bot was down and send them
        # or create timers for the remaining ones
        async for existing_reminder in existing_reminders:
            if existing_reminder.reminder_time <= start_time:
                await self._send_reminder(existing_reminder)
            else:
                delta = (existing_reminder.reminder_time - start_time).seconds
                self._create_timer(delta, existing_reminder)

    def _create_timer(self, delta: float, reminder: Reminder) -> None:
        logger.info(
            "Reminding Discord User (ID=%d) in %0.2f seconds in channel %d",
            reminder.creator_id,
            delta,
            reminder.initial_channel_id,
        )
        asyncio.get_running_loop().call_later(
            delta, lambda: asyncio.create_task(self._send_reminder(reminder))
        )

    async def _send_reminder(self, reminder: Reminder) -> None:
        channel = self.bot.get_partial_messageable(reminder.initial_channel_id)
        if not channel:
            logger.warn(
                "No channel was found for %d, doing nothing.",
                reminder.initial_channel_id,
            )
            await reminder.adelete()
        await channel.send(
            f'<@{reminder.creator_id}>, I am reminding you about "{reminder.reminder_text}"'
        )
        await reminder.adelete()

    @commands.command(
        help="Create a reminder to get pinged about something in the future"
    )
    async def remindme(
        self, ctx: Context[Bot], time_text: str, reminder_text: str
    ) -> None:
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
        reminder = Reminder(
            creator_id=ctx.author.id,
            reminder_text=reminder_text,
            reminder_time=reminder_time,
            initial_channel_id=ctx.channel.id,
        )
        await reminder.asave()
        await ctx.channel.send(f"Got it, I will remind you in {time_text}")
        start_time = datetime.datetime.now()
        delta = (reminder_time - start_time).seconds
        self._create_timer(delta, reminder)

    @commands.command(help="List all the reminders you have currently set")
    async def list_reminders(self, ctx: Context[Bot]) -> None:
        reminder_rows = []
        fake_idx = 0
        async for existing_reminder in Reminder.objects.filter(
            creator_id=ctx.author.id
        ).order_by("reminder_time"):
            reminder_text = (
                existing_reminder.reminder_text
                if len(existing_reminder.reminder_text) < 50
                else existing_reminder.reminder_text[:50] + "..."
            )
            reminder_rows.append(
                [fake_idx, existing_reminder.reminder_time, reminder_text]
            )
            fake_idx += 1
        if reminder_rows:
            await ctx.send(
                f"```\n{tabulate.tabulate(reminder_rows, headers=LIST_REMINDERS_HEADERS)}```"
            )
        else:
            await ctx.send("You have no active reminders")

    @sync_to_async
    def _get_reminder(self, creator_id: int, reminder_id: int) -> Reminder:
        return Reminder.objects.filter(creator_id=creator_id).order_by("reminder_time")[
            reminder_id
        ]

    @commands.command(help="Delete a particular reminder you have")
    async def delete_reminder(self, ctx: Context[Bot], reminder_id: int) -> None:
        try:
            reminder = await self._get_reminder(ctx.author.id, reminder_id)
            await reminder.adelete()
            await ctx.send("Reminder has been deleted")
        except Reminder.DoesNotExist:
            await ctx.send("No reminder exists for that ID!")
