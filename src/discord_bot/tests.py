from unittest.mock import patch

from discord.ext import tasks
from django.db import InterfaceError, OperationalError
from django.test import SimpleTestCase

from .cog import DatabaseConnectionCog
from .db import refresh_db_connections, survive_database_outage


class SurviveDatabaseOutageTests(SimpleTestCase):
    async def test_connection_errors_are_swallowed(self) -> None:
        for error in (OperationalError, InterfaceError):

            @survive_database_outage
            async def task(error: type[Exception] = error) -> None:
                raise error("the connection is closed")

            with self.assertLogs("discord_bot.db", "WARNING"):
                await task()

    async def test_other_errors_still_raise(self) -> None:
        @survive_database_outage
        async def task() -> None:
            raise ValueError("a real bug")

        with self.assertRaises(ValueError):
            await task()

    async def test_loop_keeps_running_after_a_connection_error(self) -> None:
        runs: list[int] = []

        @tasks.loop(seconds=0, count=3)
        @survive_database_outage
        async def task() -> None:
            runs.append(len(runs))
            if len(runs) == 1:
                raise OperationalError("terminating connection")

        with self.assertLogs("discord_bot.db", "WARNING"):
            await task.start()
        self.assertEqual(runs, [0, 1, 2])


class RefreshDbConnectionsTests(SimpleTestCase):
    async def test_closes_old_connections(self) -> None:
        with patch("discord_bot.db.close_old_connections") as close:
            await refresh_db_connections()
        close.assert_called_once_with()

    async def test_cog_loop_refreshes_connections(self) -> None:
        with patch("discord_bot.cog.refresh_db_connections") as refresh:
            await DatabaseConnectionCog.refresh_connections.coro(None)  # type: ignore[arg-type]
        refresh.assert_called_once_with()
