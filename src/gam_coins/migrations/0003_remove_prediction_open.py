# Generated by Django 3.2.8 on 2021-11-06 18:01

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("gam_coins", "0002_prediction_state"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="prediction",
            name="open",
        ),
    ]
