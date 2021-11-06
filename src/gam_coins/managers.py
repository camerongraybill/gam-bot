from async_helpers.managers import AsyncEnabledManager
from typing import TypeVar, TYPE_CHECKING

from discord_bot.models import DiscordUser

if TYPE_CHECKING:
    from .models import Account

_T = TypeVar("_T", bound="Account")


# Unsure why this one complains but discord_bot.managers does not
# pylint: disable=inherit-non-class
class AccountManager(AsyncEnabledManager[_T]):
    async def lookup_account(self, discord_id: int) -> _T:
        u = await DiscordUser.objects.lookup_user(discord_id)
        account, _ = await self.async_get_or_create(user=u)
        account.user = u
        return account
