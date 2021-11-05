from logging import getLogger
from discord.enums import Status

from django.conf import settings

from discord.ext.commands import Cog
from discord.ext import tasks

from .models import GamUser

from typing import TYPE_CHECKING

logger = getLogger(__name__)


if TYPE_CHECKING:
    from discord.ext.commands import Bot, Context


# pylint: disable=inherit-non-class
class UserPresenceDetectorCog(Cog):  # type: ignore
    def __init__(self, bot: "Bot[Context]"):
        self.bot = bot
        self.check_user_presence.start()  # pylint: disable=no-member

    @tasks.loop(minutes=1.0)
    async def check_user_presence(self) -> None:
        for user in self.bot.get_all_members():
            gam_user, _ = await GamUser.objects.async_get_or_create(discord_id=user.id)
            if (
                isinstance(user.status, Status)
                and user.status is Status.online
                and not user.bot
            ):
                gam_user.gam_coins += settings.GAM_COINS_PER_MINUTE
                await gam_user.async_save()

    @check_user_presence.before_loop  # type: ignore
    async def before_check_user_presence(self) -> None:
        logger.info("Waiting for bot to start before checking user presence")
        await self.bot.wait_until_ready()
