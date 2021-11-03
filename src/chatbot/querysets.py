from typing import Any, TypeVar, MutableMapping, Optional, AsyncIterable, Callable, Awaitable

from asgiref.sync import sync_to_async
from django.db.models import QuerySet, Model

_T = TypeVar("_T", bound=Model, covariant=True)
RV = TypeVar("RV")


def better_sync_to_async(f: Callable[[], RV]) -> Callable[[], Awaitable[RV]]:
    return sync_to_async(f)


# pylint: disable=inherit-non-class
class AsyncEnabledQuerySet(QuerySet[_T]):
    async def async_get(self, *args: Any, **kwargs: Any) -> _T:
        @better_sync_to_async
        def _() -> _T:
            return self.get(*args, **kwargs)

        return await _()

    async def async_get_or_create(
        self, defaults: Optional[MutableMapping[str, Any]] = None, **kwargs: Any
    ) -> tuple[_T, bool]:
        @better_sync_to_async
        def _() -> tuple[_T, bool]:
            return self.get_or_create(defaults=defaults, **kwargs)

        return await _()

    async def to_list(
        self,
    ) -> list[_T]:
        @better_sync_to_async
        def _() -> list[_T]:
            return list(self)

        return await _()

    async def __aiter__(self) -> AsyncIterable[_T]:
        for result in await self.to_list():
            yield result

    async def async_create(
        self,
        **kwargs: Any
    ) -> _T:
        @better_sync_to_async
        def _() -> _T:
            return self.create(**kwargs)

        return await _()

    async def async_update_or_create(
        self,
        defaults: Optional[MutableMapping[str, Any]] = None,
        **kwargs: Any
    ) -> tuple[_T, bool]:
        @better_sync_to_async
        def _() -> tuple[_T, bool]:
            return self.update_or_create(defaults=defaults, **kwargs)

        return await _()

    async def async_update(
        self,
        **kwargs: Any
    ) -> int:
        @better_sync_to_async
        def _() -> int:
            return self.update(**kwargs)

        return await _()
