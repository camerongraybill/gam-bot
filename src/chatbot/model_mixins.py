from asgiref.sync import sync_to_async


# pylint: disable=too-few-public-methods
class AsyncModelMixin:
    async def async_save(self) -> None:
        @sync_to_async
        def _() -> None:
            self.save()  # type: ignore

        await _()
