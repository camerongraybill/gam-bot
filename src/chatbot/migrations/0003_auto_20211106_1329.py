# Generated by Django 3.2.8 on 2021-11-06 17:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0002_merge_fill_gam_coins_fill_social_score'),
    ]

    operations = [
        migrations.DeleteModel(
            name='EmojiScore',
        ),
        migrations.RemoveField(
            model_name='predictionchoice',
            name='prediction',
        ),
        migrations.RemoveField(
            model_name='wager',
            name='choice',
        ),
        migrations.RemoveField(
            model_name='wager',
            name='user',
        ),
        migrations.DeleteModel(
            name='GamUser',
        ),
        migrations.DeleteModel(
            name='Prediction',
        ),
        migrations.DeleteModel(
            name='PredictionChoice',
        ),
        migrations.DeleteModel(
            name='Wager',
        ),
    ]
