from django.contrib import admin
from .models import Account, Prediction, PredictionChoice, Wager

# Register your models here.

admin.site.register(Account)
admin.site.register(Prediction)
admin.site.register(PredictionChoice)
admin.site.register(Wager)
