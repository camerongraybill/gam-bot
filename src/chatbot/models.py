from django.db import models

from chatbot.managers import AsyncEnabledManager
from chatbot.model_mixins import AsyncModelMixin


class GamUser(models.Model, AsyncModelMixin):
    discord_id = models.BigIntegerField(primary_key=True)
    gam_coins = models.PositiveIntegerField(default=0)
    social_score = models.IntegerField(default=0)

    objects = AsyncEnabledManager["GamUser"]()
