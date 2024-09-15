from django.db import models

from discord_bot.models import DiscordUser


class EmojiScore(models.Model):
    emoji_id = models.TextField(primary_key=True)
    score = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.emoji_id} score is {self.score}"


class SocialScore(models.Model):
    user = models.OneToOneField(DiscordUser, on_delete=models.CASCADE, primary_key=True)
    score = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.user}'s Social Score is {self.score}"
