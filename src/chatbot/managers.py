from typing import TypeVar, TYPE_CHECKING

from django.db.models import Model
from django.db.models.manager import BaseManager

from chatbot.querysets import AsyncEnabledQuerySet

_T = TypeVar("_T", bound=Model, covariant=True)

if TYPE_CHECKING:
    from typing import Any, MutableMapping, Optional

    class _Base(BaseManager[_T]):  # pylint: disable=inherit-non-class
        # pylint: disable=no-self-use
        async def async_get(self, *args: Any, **kwargs: Any) -> _T:
            ...

        # pylint: disable=no-self-use, unused-argument
        async def async_get_or_create(
            self, defaults: Optional[MutableMapping[str, Any]] = None, **kwargs: Any
        ) -> tuple[_T, bool]:
            ...


else:
    _Base = BaseManager.from_queryset(AsyncEnabledQuerySet[_T])


class AsyncEnabledManager(_Base[_T]):
    pass
