# Generated by Django 3.2.8 on 2021-11-03 03:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0005_prediction_predictionchoice_wager'),
    ]

    operations = [
        migrations.RenameField(
            model_name='wager',
            old_name='bettor',
            new_name='user',
        ),
    ]