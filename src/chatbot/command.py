from __future__ import annotations
import re
from typing import Callable, Optional, Sequence, Set
from dataclasses import dataclass, field

from discord import Client


CallableFunc = Callable[[str, Optional[str], Optional[Sequence[str]]], Sequence[str]]
COMMAND_REGEX = re.compile(r"^(?P<keyword>\w+)((?P<args>\s\w+))*\s*$")


@dataclass
class Command:
    keyword: str
    channels: Optional[Set[str]] = None
    response: Sequence[str] = field(default_factory=list)
    func: Optional[CallableFunc] = None
    client: Optional[Client] = None

    def match(self, channel: Optional[str]) -> bool:
        return self.channels is None or channel in self.channels

    def __call__(self, user: str, channel: Optional[str], args: Sequence[str]) -> Sequence[str]:
        if self.func:
            return self.func(user, channel, args)
        return self.response


@dataclass
class DiscordCommandRegistry:
    _client: Optional[Client] = None
    _mappings: dict[str, Command] = field(default_factory=dict)

    def from_args(
        self,
        keyword: str,
        channels: Optional[Set[str]],
        response: Sequence[str],
        func: Optional[CallableFunc] = None,
    ) -> Command:
        if func is not None:
            return Command(keyword=keyword, channels=channels, response=response, func=func, client=self._client)
        return Command(keyword=keyword, channels=channels, response=response, client=self._client)

    def register(self, command: Command) -> None:
        if command.keyword in self._mappings:
            raise KeyError(
                "`{}` is already a registered command keyword".format(command.keyword)
            )
        self._mappings[command.keyword] = command

    def __call__(self, user: str, message: str, channel: Optional[str]) -> Sequence[str]:
        full_match = COMMAND_REGEX.fullmatch(message)
        if full_match is None:
            raise Exception("could not parse message")
        keyword = full_match.group("keyword").strip()
        if keyword not in self._mappings:
            raise KeyError("`{}` is not a registered command keyword".format(keyword))
        command = self._mappings[keyword]
        if not command.match(channel):
            return []

        args = message.removeprefix(full_match.group("keyword")).split()
        return command(user, channel, args)


REGISTRY = DiscordCommandRegistry()
