from typing import TypeVar, Callable, Awaitable

from asgiref.sync import sync_to_async as asgrief_sync_to_async

RV = TypeVar("RV")


def sync_to_async(f: Callable[[], RV]) -> Callable[[], Awaitable[RV]]:
    return asgrief_sync_to_async(f)
