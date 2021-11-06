from discord.ext.commands import Cog
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord.ext.commands import Bot, Context

    _base = Cog["Context"]
else:
    _base = Cog


class BaseCog(_base):
    def __init__(self, bot: "Bot[Context]") -> None:
        self._bot = bot

    @property
    def bot(self) -> "Bot[Context]":
        return self._bot
