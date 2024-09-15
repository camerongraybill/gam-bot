from logging import getLogger

from discord.ext import tasks
from discord.ext.commands import Cog, Bot

logger = getLogger(__name__)


class BaseCog(Cog):
    def __init__(self, bot: Bot) -> None:
        self._bot = bot

    @property
    def bot(self) -> Bot:
        return self._bot


class UserTrackingCog(BaseCog):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot)
        self.grab_user_info.start()

    @tasks.loop(minutes=1.0)
    async def grab_user_info(self) -> None:
        # Django complains about importing this too early so we do it locally instead.
        from .models import DiscordUser

        user_objs = []
        for user in self.bot.get_all_members():
            user_objs.append(await DiscordUser.objects.lookup_user(user.id))
            user_objs[-1].last_known_nickname = (
                user.nick or user_objs[-1].last_known_nickname
            )
            user_objs[-1].last_known_account_name = (
                str(user) or user_objs[-1].last_known_account_name
            )
        await DiscordUser.objects.abulk_update(
            user_objs, ("last_known_nickname", "last_known_account_name")
        )

    @grab_user_info.before_loop
    async def before_grab_user_info(self) -> None:
        logger.info("Waiting for bot to start before checking user info")
        await self.bot.wait_until_ready()
