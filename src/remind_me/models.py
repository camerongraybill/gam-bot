from django.db import models

from async_helpers.managers import AsyncEnabledManager
from async_helpers.mixins import AsyncModelMixin
from discord_bot.models import DiscordUser

# Create your models here.
class Reminder(models.Model, AsyncModelMixin):
    creator = models.OneToOneField(
        DiscordUser, primary_key=True, on_delete=models.CASCADE
    )
    reminder_text = models.TextField(blank=False, null=False)
    reminder_time = models.DateTimeField()
    initial_channel_id = models.PositiveBigIntegerField()

    objects = AsyncEnabledManager["Reminder"]()
