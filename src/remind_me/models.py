from django.db import models

from discord_bot.models import DiscordUser


# Create your models here.
class Reminder(models.Model):
    creator = models.OneToOneField(
        DiscordUser, primary_key=True, on_delete=models.CASCADE
    )
    reminder_text = models.TextField(blank=False, null=False)
    reminder_time = models.DateTimeField()
    initial_channel_id = models.PositiveBigIntegerField()
