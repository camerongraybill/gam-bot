# Generated by Django 3.2.8 on 2021-11-06 17:52
from typing import Any

from django.db import migrations, models


def populate_state_field(apps: Any, schema_editor: Any) -> None:
    Prediction = apps.get_model("gam_coins", "Prediction")
    Prediction.objects.filter(open=False).update(state=3)


class Migration(migrations.Migration):
    dependencies = [
        ("gam_coins", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="prediction",
            name="state",
            field=models.IntegerField(
                choices=[
                    (1, "Accepting Wagers"),
                    (2, "Waiting For Resolution"),
                    (3, "Resolved"),
                ],
                default=1,
            ),
        ),
        migrations.RunPython(populate_state_field),
    ]
