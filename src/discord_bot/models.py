from django.db import models
from async_helpers.mixins import AsyncModelMixin
from .managers import DiscordUserManager


class DiscordUser(models.Model, AsyncModelMixin):
    discord_id = models.PositiveBigIntegerField(primary_key=True)
    last_known_nickname = models.CharField(blank=False, null=True, max_length=128)
    last_known_account_name = models.CharField(blank=False, null=True, max_length=128)

    objects = DiscordUserManager["DiscordUser"]()

    def __str__(self) -> str:
        return self.last_known_nickname or self.last_known_account_name or "Unknown"
