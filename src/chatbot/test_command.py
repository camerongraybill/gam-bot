from unittest import IsolatedAsyncioTestCase
from mock import Mock
from .command import Command  # pylint: disable=import-error


class CommandTest(IsolatedAsyncioTestCase):
    def setUp(self):
        self.message = Mock()

    async def test_command_empty_channels(self):
        command = Command("test", None, ("Response",))
        self.assertTrue(command.match("channel"))
        self.assertSequenceEqual(
            await command(self.message, "channel", "test"), ("Response",)
        )

    async def test_command_empty_response(self):
        command = Command(keyword="test", channels={"channel"})
        self.assertTrue(command.match("channel"))
        response = await command(self.message, "channel", "test")
        self.assertEqual(len(response), 0)

    async def test_command_match_regex(self):
        command = Command("test", None, ("Response",))
        self.assertSequenceEqual(
            await command(self.message, "channel", "test muh command"), ("Response",)
        )

    async def test_command_lambda_returns_arguments(self):
        async def test_func(message, channel, args):  # pylint: disable=unused-argument
            return args

        command = Command("test", None, ("Response",), func=test_func)
        self.assertTrue(command.match("channel"))
        response = await command(self.message, "channel", ["muh", "command"])
        self.assertSequenceEqual(response, ["muh", "command"])
