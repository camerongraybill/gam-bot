from django.db import migrations


def forwards_func(apps, schema_editor):
    GamUser = apps.get_model("chatbot", "GamUser")
    DiscordUser = apps.get_model("discord_bot", "DiscordUser")
    SocialScore = apps.get_model("social_score", "SocialScore")
    OldEmojiScore = apps.get_model("chatbot", "EmojiScore")
    NewEmojiScore = apps.get_model("social_score", "EmojiScore")
    db_alias = schema_editor.connection.alias
    for user in GamUser.objects.all():
        discord_user, _ = DiscordUser.objects.get_or_create(discord_id=user.discord_id)
        SocialScore.objects.create(score=user.social_score, user=discord_user)
    NewEmojiScore.objects.bulk_create(
        [
            NewEmojiScore(
                emoji_id=x.emoji_id,
                score=x.score,
            )
            for x in OldEmojiScore.objects.all()
        ]
    )
    DiscordUser.objects.using(db_alias).bulk_create(
        [
            DiscordUser(discord_id=user.discord_id) for user in GamUser.objects.all()
        ]
    )


def reverse_func(apps, schema_editor):
    NewEmojiScore = apps.get_model("social_score", "EmojiScore")
    SocialScore = apps.get_model("social_score", "SocialScore")
    NewEmojiScore.objects.all().delete()
    SocialScore.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', 'fill_discord_bot'),
        ('social_score', '__first__'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]