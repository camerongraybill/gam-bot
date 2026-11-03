from collections.abc import Callable, Coroutine
from functools import wraps
from logging import getLogger
from typing import Any, ParamSpec

from asgiref.sync import sync_to_async
from django.db import InterfaceError, OperationalError, close_old_connections

logger = getLogger(__name__)

P = ParamSpec("P")


async def refresh_db_connections() -> None:
    """Drop stale database connections, so the next query opens a new one.

    Django does this at the start and end of each web request, but the bot has no
    requests. Without this, a database restart breaks every query until the bot restarts.
    This has to use the same thread as the async ORM, which sync_to_async does by default.
    """
    await sync_to_async(close_old_connections)()


def survive_database_outage(
    func: Callable[P, Coroutine[Any, Any, None]],
) -> Callable[P, Coroutine[Any, Any, None]]:
    """Log database connection errors from a task and skip that run.

    An unhandled exception stops a discord.ext.tasks loop for good, so without this a
    database restart would end the task until the bot restarts.
    """

    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
        try:
            await func(*args, **kwargs)
        except (OperationalError, InterfaceError) as exc:
            logger.warning(
                "Skipping this run of %s, the database is unavailable: %s",
                func.__name__,
                exc,
            )

    return wrapper
