from django.db import models


class GamUser(models.Model):
    discord_id = models.BigIntegerField(primary_key=True)
    gam_coins = models.PositiveIntegerField(default=0)
    social_score = models.IntegerField(default=0)
