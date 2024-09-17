from django.db import models


# Create your models here.
class Reminder(models.Model):
    creator_id = models.PositiveBigIntegerField()
    reminder_text = models.TextField(blank=False, null=False)
    reminder_time = models.DateTimeField()
    initial_channel_id = models.PositiveBigIntegerField()
