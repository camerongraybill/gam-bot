# Generated by Django 3.2.8 on 2021-11-05 02:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("discord_bot", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="EmojiScore",
            fields=[
                ("emoji_id", models.TextField(primary_key=True, serialize=False)),
                ("score", models.IntegerField(default=0)),
            ],
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="SocialScore",
            fields=[
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to="discord_bot.discorduser",
                    ),
                ),
                ("score", models.IntegerField(default=0)),
            ],
            bases=(models.Model,),
        ),
    ]
