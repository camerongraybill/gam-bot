from django.db import migrations


def forwards_func(apps, schema_editor):
    GamUser = apps.get_model("chatbot", "GamUser")
    DiscordUser = apps.get_model("discord_bot", "DiscordUser")
    db_alias = schema_editor.connection.alias
    DiscordUser.objects.using(db_alias).bulk_create(
        [DiscordUser(discord_id=user.discord_id) for user in GamUser.objects.all()]
    )


class Migration(migrations.Migration):

    dependencies = [
        ("chatbot", "0007_merge_0005_emojiscore_0006_rename_bettor_wager_user"),
        ("discord_bot", "__first__"),
    ]

    operations = [
        migrations.RunPython(forwards_func),
    ]
