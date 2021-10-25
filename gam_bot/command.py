from __future__ import annotations
import re
from typing import Callable, Dict, Optional, Sequence, Set

from discord import Client


CallableFunc = Callable[[Optional[str], Optional[Sequence[str]]], Sequence[str]]
COMMAND_REGEX = re.compile(r"^(?P<keyword>\w+)((?P<args>\s\w+))*\s*$")

class Command:
    def __init__(self, keyword: str, channels: Optional[Set[str]], response: Sequence[str]=(lambda: list())(), func: CallableFunc=None, client: Optional[Client]=None):
        self.keyword: str = keyword
        self.channels: Optional[Set[str]] = channels
        self.response: Sequence[str] = response
        self.func: CallableFunc = lambda _channel, _args: self.response
        self.client: Optional[Client] = client
        if func is not None:
            self.func = func
    def match(self, channel: Optional[str]) -> bool:
        return self.channels is None or channel in self.channels

    def call(self, channel: Optional[str], args: Sequence[str]) -> Sequence[str]:
        return self.func(channel, args)


class DiscordCommandRegistry:

    def __init__(self, client: Optional[Client]=None):
        self._client: Optional[Client] = client
        self._mappings: Dict[str, Command] = {}

    def from_args(self, keyword: str, channels: Optional[Set[str]], response: Sequence[str], func: CallableFunc=None) -> Command:
        return Command(keyword, channels, response, func, self._client)

    def register(self, command: Command) -> None:
        if command.keyword in self._mappings:
            raise KeyError("`{}` is already a registered command keyword".format(command.keyword))
        self._mappings[command.keyword] = command

    def dispatch(self, message: str, channel: Optional[str]) -> Sequence[str]:
        full_match = COMMAND_REGEX.fullmatch(message)
        if full_match is None:
            raise Exception("could not parse message")
        keyword = full_match.group("keyword").strip()
        if keyword not in self._mappings:
            raise KeyError("`{}` is not a registered command keyword".format(keyword))
        command =self._mappings[keyword]
        if not command.match(channel):
            return []

        args = message.removeprefix(full_match.group("keyword")).split()
        return command.call(channel, args)


REGISTRY = DiscordCommandRegistry()


