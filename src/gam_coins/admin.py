from django.contrib import admin
from .models import Account, Prediction, PredictionChoice, Wager

# Register your models here.

admin.register(Account)
admin.register(Prediction)
admin.register(PredictionChoice)
admin.register(Wager)
