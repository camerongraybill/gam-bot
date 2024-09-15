from django.db import models

from discord_bot.managers import UserManager


class DiscordUser(models.Model):
    discord_id = models.PositiveBigIntegerField(primary_key=True)
    last_known_nickname = models.CharField(blank=False, null=True, max_length=128)
    last_known_account_name = models.CharField(blank=False, null=True, max_length=128)
    notify_on_startup = models.BooleanField(default=False)

    objects = UserManager()

    def __str__(self) -> str:
        return self.last_known_nickname or self.last_known_account_name or "Unknown"
