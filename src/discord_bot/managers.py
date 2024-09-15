from typing import TYPE_CHECKING

from django.db.models import Manager

if TYPE_CHECKING:
    from .models import DiscordUser


class UserManager(Manager["DiscordUser"]):
    async def lookup_user(self, discord_id: int) -> "DiscordUser":
        obj, _ = await self.aget_or_create(discord_id=discord_id)
        return obj
