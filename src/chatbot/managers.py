# pylint: disable=no-self-use, unused-argument
from typing import TypeVar, TYPE_CHECKING, AsyncIterable, Iterable, Sequence

from django.db.models import Model
from django.db.models.manager import BaseManager

from chatbot.querysets import AsyncEnabledQuerySet

_T = TypeVar("_T", bound=Model, covariant=True)

if TYPE_CHECKING:
    from typing import Any, MutableMapping, Optional

    class _Base(BaseManager[_T]):  # pylint: disable=inherit-non-class
        async def async_get(self, *args: Any, **kwargs: Any) -> _T:
            ...

        async def async_get_or_create(
            self, defaults: Optional[MutableMapping[str, Any]] = None, **kwargs: Any
        ) -> tuple[_T, bool]:
            ...

        async def to_list(
            self,
        ) -> list[_T]: ...

        async def __aiter__(self) -> AsyncIterable[_T]: ...

        async def async_create(
            self,
            **kwargs: Any
        ) -> _T: ...

        async def async_update_or_create(
            self,
            defaults: Optional[MutableMapping[str, Any]] = None,
            **kwargs: Any
        ) -> tuple[_T, bool]: ...

        async def async_update(
            self,
            **kwargs: Any
        ) -> int: ...

        async def async_bulk_create(
            self,
            objs: Iterable[_T],
            batch_size: Optional[int] = None,
            ignore_conflicts: bool = False
        ) -> list[_T]: ...

        async def async_bulk_update(
            self,
            objs: Iterable[_T],
            fields: Sequence[str],
            batch_size: Optional[int] = None
        ) -> None: ...

else:
    _Base = BaseManager.from_queryset(AsyncEnabledQuerySet[_T])


class AsyncEnabledManager(_Base[_T]):
    pass
