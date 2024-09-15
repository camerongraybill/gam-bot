from typing import TYPE_CHECKING

from django.db.models import Manager

from discord_bot.models import DiscordUser

if TYPE_CHECKING:
    from .models import Account


class AccountManager(Manager["Account"]):
    async def lookup_account(self, discord_id: int) -> "Account":
        u = await DiscordUser.objects.lookup_user(discord_id)
        account, _ = await self.aget_or_create(user=u)
        account.user = u
        return account
