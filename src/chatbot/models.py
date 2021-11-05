from django.db import models

from async_helpers.managers import AsyncEnabledManager
from async_helpers.mixins import AsyncModelMixin


class GamUser(models.Model, AsyncModelMixin):
    discord_id = models.BigIntegerField(primary_key=True)
    gam_coins = models.PositiveIntegerField(default=0)
    social_score = models.IntegerField(default=0)

    objects = AsyncEnabledManager["GamUser"]()


class Prediction(models.Model, AsyncModelMixin):
    prediction_text = models.TextField()
    thread_id = models.BigIntegerField(
        null=True
    )  # This is the ID of the message the bot sends that replies should go to
    open = models.BooleanField(default=True)  # True if wagers can be placed

    objects = AsyncEnabledManager["Prediction"]()


class PredictionChoice(models.Model, AsyncModelMixin):
    prediction = models.ForeignKey(Prediction, on_delete=models.CASCADE)
    choice = models.TextField()

    objects = AsyncEnabledManager["PredictionChoice"]()


class Wager(models.Model, AsyncModelMixin):
    user = models.ForeignKey(
        GamUser, on_delete=models.CASCADE
    )  # Person who made the wager
    amount = models.IntegerField()  # Amount they're wagering
    choice = models.ForeignKey(
        PredictionChoice, on_delete=models.CASCADE
    )  # Choice they're wagering on

    objects = AsyncEnabledManager["Wager"]()


class EmojiScore(models.Model, AsyncModelMixin):
    emoji_id = models.TextField()
    score = models.IntegerField(default=0)

    objects = AsyncEnabledManager["EmojiScore"]()
