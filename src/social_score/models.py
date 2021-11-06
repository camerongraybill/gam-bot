from django.db import models

from async_helpers.managers import AsyncEnabledManager
from async_helpers.mixins import AsyncModelMixin
from discord_bot.models import DiscordUser


class EmojiScore(models.Model, AsyncModelMixin):
    emoji_id = models.TextField(primary_key=True)
    score = models.IntegerField(default=0)

    objects = AsyncEnabledManager["EmojiScore"]()

    def __str__(self) -> str:
        return f"{self.emoji_id} score is {self.score}"


class SocialScore(models.Model, AsyncModelMixin):
    user = models.OneToOneField(DiscordUser, on_delete=models.CASCADE, primary_key=True)
    score = models.IntegerField(default=0)

    objects = AsyncEnabledManager["SocialScore"]()

    def __str__(self) -> str:
        return f"{self.user}'s Social Score is {self.score}"
