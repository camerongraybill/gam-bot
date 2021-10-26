from __future__ import annotations
import re
from typing import Awaitable, Optional, Sequence, Set, Callable
from dataclasses import dataclass, field

from discord import Client, Message


CallableFunc = Callable[
    [Message, Optional[str], Sequence[str]], Awaitable[Sequence[str]]
]
COMMAND_REGEX = re.compile(r"^(?P<keyword>\w+)((?P<args>\s\w+))*\s*$")


def _function_factory(resp: Sequence[str]) -> CallableFunc:
    # pylint: disable=unused-argument
    async def _anonymous_async_lambda(
        m: Message, channel: Optional[str], args: Sequence[str]
    ) -> Sequence[str]:
        return resp

    return _anonymous_async_lambda


@dataclass
class Command:
    keyword: str
    channels: Optional[Set[str]] = None
    response: Sequence[str] = field(default_factory=list)
    func: Optional[CallableFunc] = None
    client: Optional[Client] = None

    def match(self, channel: Optional[str]) -> bool:
        return self.channels is None or channel in self.channels

    async def __call__(
        self, message: Message, channel: Optional[str], args: Sequence[str]
    ) -> Sequence[str]:
        ret: Sequence[str] = []
        if self.func is None:
            ret = await _function_factory(self.response)(message, channel, args)
        else:
            ret = await self.func(message, channel, args)
        return ret


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
        if func is None:
            func = _function_factory(response)
        return Command(
            keyword=keyword,
            channels=channels,
            response=response,
            func=func,
            client=self._client,
        )

    def register(self, command: Command) -> None:
        if command.keyword in self._mappings:
            raise KeyError(
                "`{}` is already a registered command keyword".format(command.keyword)
            )
        self._mappings[command.keyword] = command

    async def __call__(
        self, message: Message, command_string: str, channel: Optional[str]
    ) -> Sequence[str]:
        full_match = COMMAND_REGEX.fullmatch(command_string)
        if full_match is None:
            raise Exception("could not parse message")
        keyword = full_match.group("keyword").strip()
        if keyword not in self._mappings:
            raise KeyError("`{}` is not a registered command keyword".format(keyword))
        command = self._mappings[keyword]
        if not command.match(channel):
            return []

        args = command_string.removeprefix(keyword).split()
        return await command(message, channel, args)
