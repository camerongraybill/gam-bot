from unittest import TestCase
from .command import Command


class CommandTest(TestCase):
    def test_command_empty_channels(self):
        command = Command("test", None, ("Response",))
        self.assertTrue(command.match("channel"))
        self.assertSequenceEqual(command("user", "channel", "test"), ("Response",))

    def test_command_empty_response(self):
        command = Command(keyword="test", channels={"channel"})
        self.assertTrue(command.match("channel"))
        response = command("user", "channel", "test")
        self.assertEqual(len(response), 0)

    def test_command_match_regex(self):
        command = Command("test", None, ("Response",))
        self.assertSequenceEqual(
            command("user", "channel", "test muh command"), ("Response",)
        )

    def test_command_lambda_returns_arguments(self):
        command = Command("test", None, ("Response",), lambda user, channel, arguments: arguments)
        self.assertTrue(command.match("channel"))
        self.assertSequenceEqual(
            command("user", "channel", ["muh", "command"]), ["muh", "command"]
        )
