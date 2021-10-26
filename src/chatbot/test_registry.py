import pytest
from unittest import IsolatedAsyncioTestCase
from mock import Mock
from .command import Command, DiscordCommandRegistry  # pylint: disable=import-error


class CommandTest(IsolatedAsyncioTestCase):
    def setUp(self):
        self.registry = DiscordCommandRegistry()
        self.message = Mock()

    def test_registry_from_args(self):
        command: Command = self.registry.from_args("test", None, ("Response",))
        self.assertEqual(command.keyword, "test")
        self.assertIsNone(command.channels)
        self.assertSequenceEqual(command.response, ("Response",))

    def test_registry_register(self):
        command: Command = self.registry.from_args("test", None, ("Response",))
        self.registry.register(command)

    def test_registry_register_fail(self):
        command: Command = self.registry.from_args("test", None, ("Response",))
        self.registry.register(command)
        with pytest.raises(KeyError):
            self.registry.register(command)

    async def test_registry_dispatch(self):
        command: Command = self.registry.from_args("test", None, ("Response",))
        self.registry.register(command)
        self.assertSequenceEqual(
            await self.registry(self.message, "test", "channel"), ("Response",)
        )

    async def test_registry_dispatch_args(self):
        async def test_func(message, channel, args):  # pylint: disable=unused-argument
            return args

        command: Command = self.registry.from_args(
            "test", None, ("Response",), func=test_func
        )
        self.registry.register(command)
        self.assertSequenceEqual(
            await self.registry(self.message, "test arg1 arg2", "channel"),
            ("arg1", "arg2"),
        )

    async def test_registry_dispatch_fail(self):
        command: Command = self.registry.from_args("test", None, ("Response",))
        self.registry.register(command)
        with pytest.raises(KeyError):
            await self.registry(self.message, "test1 arg1 arg2", "channel")
