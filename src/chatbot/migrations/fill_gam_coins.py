from django.db import migrations


def forwards_func(apps, schema_editor):
    GamUser = apps.get_model("chatbot", "GamUser")
    DiscordUser = apps.get_model("discord_bot", "DiscordUser")
    Account = apps.get_model("gam_coins", "CoinCount")

    for user in GamUser.objects.all():
        discord_user, _ = DiscordUser.objects.get_or_create(discord_id=user.discord_id)
        Account.objects.create(coins=user.gam_coins, user=discord_user)


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', 'fill_discord_bot'),
        ('gam_coins', '__first__'),
    ]

    operations = [
        migrations.RunPython(forwards_func),
    ]