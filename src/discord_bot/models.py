from django.db import models
from async_helpers.mixins import AsyncModelMixin
from .managers import DiscordUserManager


class DiscordUser(models.Model, AsyncModelMixin):
    discord_id = models.PositiveBigIntegerField(primary_key=True)

    objects = DiscordUserManager['DiscordUser']()
