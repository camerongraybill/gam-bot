from typing import (
    Any,
    TypeVar,
    MutableMapping,
    Optional,
    AsyncIterable,
    Iterable,
    Sequence,
)

from .utils import sync_to_async

from django.db.models import QuerySet, Model

_T = TypeVar("_T", bound=Model, covariant=True)


# pylint: disable=inherit-non-class
class AsyncEnabledQuerySet(QuerySet[_T]):
    async def async_get(self, *args: Any, **kwargs: Any) -> _T:
        @sync_to_async
        def _() -> _T:
            return self.get(*args, **kwargs)

        return await _()

    async def async_get_or_create(
        self, defaults: Optional[MutableMapping[str, Any]] = None, **kwargs: Any
    ) -> tuple[_T, bool]:
        @sync_to_async
        def _() -> tuple[_T, bool]:
            return self.get_or_create(defaults=defaults, **kwargs)

        return await _()

    async def to_list(
        self,
    ) -> list[_T]:
        @sync_to_async
        def _() -> list[_T]:
            return list(self)

        return await _()

    async def __aiter__(self) -> AsyncIterable[_T]:
        for result in await self.to_list():
            yield result

    async def async_create(self, **kwargs: Any) -> _T:
        @sync_to_async
        def _() -> _T:
            return self.create(**kwargs)

        return await _()

    async def async_update_or_create(
        self, defaults: Optional[MutableMapping[str, Any]] = None, **kwargs: Any
    ) -> tuple[_T, bool]:
        @sync_to_async
        def _() -> tuple[_T, bool]:
            return self.update_or_create(defaults=defaults, **kwargs)

        return await _()

    async def async_update(self, **kwargs: Any) -> int:
        @sync_to_async
        def _() -> int:
            return self.update(**kwargs)

        return await _()

    async def async_bulk_create(
        self,
        objs: Iterable[_T],
        batch_size: Optional[int] = None,
        ignore_conflicts: bool = False,
    ) -> list[_T]:
        @sync_to_async
        def _() -> list[_T]:
            return self.bulk_create(
                objs, batch_size=batch_size, ignore_conflicts=ignore_conflicts
            )

        return await _()

    async def async_bulk_update(
        self,
        objs: Iterable[_T],
        fields: Sequence[str],
        batch_size: Optional[int] = None,
    ) -> None:
        @sync_to_async
        def _() -> None:
            return self.bulk_update(objs, fields=fields, batch_size=batch_size)

        return await _()
