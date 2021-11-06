from django.db import models

from async_helpers.managers import AsyncEnabledManager
from async_helpers.mixins import AsyncModelMixin
from discord_bot.models import DiscordUser
from .managers import AccountManager


class Account(models.Model, AsyncModelMixin):
    user = models.OneToOneField(DiscordUser, primary_key=True, on_delete=models.CASCADE)
    coins = models.PositiveIntegerField(default=0)

    objects = AccountManager["Account"]()


class Prediction(models.Model, AsyncModelMixin):
    class State(models.IntegerChoices):
        ACCEPTING_WAGERS = 1
        WAITING_FOR_RESOLUTION = 2
        RESOLVED = 3

    prediction_text = models.TextField()
    thread_id = models.BigIntegerField(
        primary_key=True
    )  # This is the ID of the message the bot sends that replies should go to
    state = models.IntegerField(choices=State.choices, default=State.ACCEPTING_WAGERS)

    objects = AsyncEnabledManager["Prediction"]()


class PredictionChoice(models.Model, AsyncModelMixin):
    prediction = models.ForeignKey(Prediction, on_delete=models.CASCADE)
    choice = models.TextField()

    objects = AsyncEnabledManager["PredictionChoice"]()

    class Meta:
        unique_together = ("prediction", "choice")


class Wager(models.Model, AsyncModelMixin):
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE
    )  # Person who made the wager
    amount = models.PositiveIntegerField()  # Amount they're wagering
    choice = models.ForeignKey(
        PredictionChoice, on_delete=models.CASCADE
    )  # Choice they're wagering on

    objects = AsyncEnabledManager["Wager"]()
