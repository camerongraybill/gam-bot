from async_helpers.managers import AsyncEnabledManager
from typing import TypeVar, TYPE_CHECKING

from discord_bot.models import DiscordUser

if TYPE_CHECKING:
    from .models import Account


_T = TypeVar('_T', bound='Account')


class AccountManager(AsyncEnabledManager[_T]):
    async def lookup_account(self, discord_id: int) -> _T:
        return await self.async_get_or_create(
            user=await DiscordUser.objects.lookup_user(discord_id)
        )[0]
