from discord.ext.commands import Bot


class BaseCog:
    def __init__(self, bot: Bot) -> None:
        self._bot = bot

    @property
    def bot(self) -> Bot:
        return self._bot
