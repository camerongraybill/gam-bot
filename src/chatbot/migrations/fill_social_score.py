from django.db import migrations


def forwards_func(apps, schema_editor):
    GamUser = apps.get_model("chatbot", "GamUser")
    DiscordUser = apps.get_model("discord_bot", "DiscordUser")
    SocialScore = apps.get_model("social_score", "SocialScore")
    for user in GamUser.objects.all():
        discord_user, _ = DiscordUser.objects.get_or_create(discord_id=user.discord_id)
        SocialScore.objects.create(score=user.social_score, user=discord_user)


class Migration(migrations.Migration):

    dependencies = [
        ("chatbot", "fill_discord_bot"),
        ("social_score", "__first__"),
    ]

    operations = [
        migrations.RunPython(forwards_func),
    ]
