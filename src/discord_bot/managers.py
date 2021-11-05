from async_helpers.managers import AsyncEnabledManager
from typing import TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from .models import DiscordUser


_T = TypeVar('_T', bound='DiscordUser')


class DiscordUserManager(AsyncEnabledManager[_T]):
    async def lookup_user(self, discord_id: int) -> _T:
        return await self.async_get_or_create(discord_id=discord_id)[0]
