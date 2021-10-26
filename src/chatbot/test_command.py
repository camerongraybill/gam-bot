from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock
from typing import Sequence, Optional
from .command import Command  # pylint: disable=import-error
from discord import Message


class CommandTest(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.message = Mock()

    async def test_command_empty_channels(self) -> None:
        command = Command("test", None, ("Response",))
        self.assertTrue(command.match("channel"))
        self.assertSequenceEqual(
            await command(self.message, "channel", "test"), ("Response",)
        )

    async def test_command_empty_response(self) -> None:
        command = Command(keyword="test", channels={"channel"})
        self.assertTrue(command.match("channel"))
        response = await command(self.message, "channel", "test")
        self.assertEqual(len(response), 0)

    async def test_command_match_regex(self) -> None:
        command = Command("test", None, ("Response",))
        self.assertSequenceEqual(
            await command(self.message, "channel", "test muh command"), ("Response",)
        )

    async def test_command_lambda_returns_arguments(self) -> None:
        # pylint: disable=unused-argument
        async def test_func(
            message: Message, channel: Optional[Sequence[str]], args: Sequence[str]
        ) -> Sequence[str]:
            return args

        command = Command("test", None, ("Response",), func=test_func)
        self.assertTrue(command.match("channel"))
        response = await command(self.message, "channel", ["muh", "command"])
        self.assertSequenceEqual(response, ["muh", "command"])
