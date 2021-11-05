from typing import Type, TypeVar

from django.db.models import Model

from .managers import AsyncEnabledManager
from .querysets import AsyncEnabledQuerySet
from .utils import sync_to_async

_T = TypeVar("_T", bound=Model)


class AsyncModelMixin:
    async def async_save(self: _T) -> None:  # type: ignore
        @sync_to_async
        def _() -> None:
            self.save()

        await _()

    @classmethod
    def async_qs(cls: Type[_T]) -> AsyncEnabledQuerySet[_T]:  # type: ignore
        if not isinstance(cls.objects, AsyncEnabledManager):
            raise AssertionError()
        return cls.objects.all()  # type: ignore

    async def async_delete(self: _T) -> None:  # type: ignore
        @sync_to_async
        def _() -> None:
            self.delete()

        await _()
