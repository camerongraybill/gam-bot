from typing import Any, TypeVar, MutableMapping, Optional, cast

from asgiref.sync import sync_to_async
from django.db.models import QuerySet, Model

_T = TypeVar("_T", bound=Model, covariant=True)


# pylint: disable=inherit-non-class
class AsyncEnabledQuerySet(QuerySet[_T]):
    async def async_get(self, *args: Any, **kwargs: Any) -> _T:
        @sync_to_async
        def _() -> _T:
            return self.get(*args, **kwargs)

        return cast(_T, await _())

    async def async_get_or_create(
        self, defaults: Optional[MutableMapping[str, Any]] = None, **kwargs: Any
    ) -> tuple[_T, bool]:
        @sync_to_async
        def _() -> tuple[_T, bool]:
            return self.get_or_create(defaults=defaults, **kwargs)

        return cast(tuple[_T, bool], await _())
