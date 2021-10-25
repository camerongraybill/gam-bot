import pytest
from unittest import TestCase
from .command import Command, REGISTRY, DiscordCommandRegistry


class CommandTest(TestCase):
    def test_registry_from_args(self):
        command: Command = REGISTRY.from_args("test", None, ("Response",))
        self.assertEqual(command.keyword, "test")
        self.assertIsNone(command.channels)
        self.assertSequenceEqual(command.response, ("Response",))

    def test_registry_register(self):
        registry = DiscordCommandRegistry()
        command: Command = REGISTRY.from_args("test", None, ("Response",))
        registry.register(command)

    def test_registry_register_fail(self):
        registry = DiscordCommandRegistry()
        command: Command = REGISTRY.from_args("test", None, ("Response",))
        registry.register(command)
        with pytest.raises(KeyError):
            registry.register(command)

    def test_registry_dispatch(self):
        registry = DiscordCommandRegistry()
        command: Command = REGISTRY.from_args("test", None, ("Response",))
        registry.register(command)
        self.assertSequenceEqual(registry.dispatch("test", "channel"), ("Response",))

    def test_registry_dispatch_args(self):
        registry = DiscordCommandRegistry()
        command: Command = REGISTRY.from_args(
            "test", None, ("Response",), lambda a, b: b
        )
        registry.register(command)
        self.assertSequenceEqual(
            registry.dispatch("test arg1 arg2", "channel"), ("arg1", "arg2")
        )

    def test_registry_dispatch_fail(self):
        registry = DiscordCommandRegistry()
        command: Command = REGISTRY.from_args("test", None, ("Response",))
        registry.register(command)
        with pytest.raises(KeyError):
            registry.dispatch("test1 arg1 arg2", "channel")
