from django.db import models


class GamUser(models.Model):
    discord_id = models.IntegerField(primary_key=True)
    gam_coins = models.PositiveIntegerField(default=0)
