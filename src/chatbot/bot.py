from logging import getLogger
from typing import Mapping, Optional
from itertools import groupby

from discord.ext.commands import Bot, Context
from django.conf import settings

from .models import GamUser, Prediction, PredictionChoice, Wager
from discord_bot.checks import only_debug


logger = getLogger(__name__)

bot = Bot(command_prefix="!")


@bot.command()
async def make_prediction(
    ctx: Context, prediction_text: str, options: Optional[str]
) -> None:
    if not options:
        options = "yes,no"
    prediction_options = options.split(",")
    prediction_model = Prediction(prediction_text=prediction_text)
    await prediction_model.async_save()
    for option in prediction_options:
        prediction_choice = PredictionChoice(
            prediction=prediction_model, choice=option.lower()
        )
        await prediction_choice.async_save()
    thread_message = await ctx.send(
        f"Prediction '{prediction_text}' has been created, reply to this message with the wager command:\n!make_wager <choice> <amount>\npossible choices are {options}"
    )
    prediction_model.thread_id = thread_message.id
    await prediction_model.async_save()


@bot.command()
async def make_wager(ctx: Context, choice: str, amount: int) -> None:
    if ctx.message.reference:
        thread_id = ctx.message.reference.message_id
        try:
            user, _ = await GamUser.objects.async_get_or_create(
                discord_id=ctx.message.author.id
            )

            if amount > user.gam_coins:
                logger.info(
                    "User %d does not have enough GamCoins to wager (tried wagering %d, only had %d)",
                    user.discord_id,
                    amount,
                    user.gam_coins,
                )
                await ctx.message.add_reaction(settings.WAGER_NO_MONEY_REACTION)
                return

            prediction = await Prediction.objects.async_get(thread_id=thread_id)
            if not prediction.open:
                logger.info(
                    "User tried wagering on closed prediction thread_id %d", thread_id
                )
                await ctx.message.add_reaction(settings.WAGER_ERROR_REACTION)
                return

            prediction_choice = await PredictionChoice.objects.async_get(
                choice=choice.lower(), prediction=prediction
            )

            user.gam_coins -= amount
            await user.async_save()

            await Wager.objects.async_create(
                user=user, amount=amount, choice=prediction_choice
            )

            await ctx.message.add_reaction(settings.WAGER_SUCCESS_REACTION)
        except Prediction.DoesNotExist:
            # This should only happen if someone replies to the wrong message
            logger.info(
                "User tried wagering on thread_id %d which does not correspond to a prediction",
                thread_id,
            )
            await ctx.message.add_reaction(settings.WAGER_ERROR_REACTION)
        except PredictionChoice.DoesNotExist:
            logger.info(
                "User's provided choice %s did not match any choices available for prediction %d",
                choice,
                prediction.id,
            )
            await ctx.message.add_reaction(settings.WAGER_ERROR_REACTION)
    else:
        logger.info("User tried to wager without replying to a prediction thread.")


@bot.command()
async def close(ctx: Context) -> None:
    if ctx.message.reference:
        thread_id = ctx.message.reference.message_id
        try:
            prediction = await Prediction.objects.async_get(thread_id=thread_id)
            prediction.open = False
            await prediction.async_save()
            await ctx.message.add_reaction(settings.WAGER_SUCCESS_REACTION)
        except Prediction.DoesNotExist:
            # This should only happen if someone replies to the wrong message
            logger.info(
                "User tried closing on thread_id %d which does not correspond to a prediction",
                thread_id,
            )
    else:
        logger.info(
            "User tried to close prediction without replying to a prediction thread."
        )


@bot.command()
async def resolve(ctx: Context, correct_choice: str) -> None:
    # Resolves a prediction thread by getting all users that made the correct choice
    # and then assigning a payout based on their relative pot contributions
    if ctx.message.reference:
        try:
            prediction = await Prediction.objects.async_get(
                thread_id=ctx.message.reference.message_id
            )
            correct_prediction_coice = await PredictionChoice.objects.async_get(
                prediction=prediction, choice=correct_choice.lower()
            )
            # Get all wagers associated with this prediction, select_related to get our FK models
            wagers = await Wager.objects.select_related().filter(choice__prediction=prediction).to_list()  # type: ignore
            pot = sum([wager.amount for wager in wagers])
            # Get all wagers associated with the correct choice and sort
            discord_id_lambda = lambda wager: wager.user.discord_id
            correct_wagers = sorted(
                [wager for wager in wagers if wager.choice == correct_prediction_coice],
                key=discord_id_lambda,
            )
            # Get the sum of correct wagers
            correct_wagers_pot = sum([wager.amount for wager in correct_wagers])
            # We need to map users to the wagers they placed
            users_to_wagers: Mapping[int, list[Wager]] = {
                k: list(g) for k, g in groupby(correct_wagers, key=discord_id_lambda)
            }
            winner_strings: list[str] = []
            for discord_id, user_wagers in users_to_wagers.items():
                coins_to_award = int(
                    (sum([wager.amount for wager in user_wagers]) / correct_wagers_pot)
                    * pot
                )
                logger.info("Awarding %d coins to user %d", coins_to_award, discord_id)
                user_wagers[0].user.gam_coins += coins_to_award
                discord_user = await bot.fetch_user(discord_id)
                winner_strings.append(f"{discord_user.name} won {coins_to_award} coins")
                await user_wagers[0].user.async_save()
            await ctx.message.reply(f"{', '.join(winner_strings)}!")
        except Prediction.DoesNotExist:
            # This should only happen if someone replies to the wrong message
            logger.info(
                "User tried resolving on thread_id %d which does not correspond to a prediction",
                ctx.message.reference.message_id,
            )
        except PredictionChoice.DoesNotExist:
            logger.info(
                "Correct choice %s did not match any choices available for prediction %d",
                correct_choice,
                prediction.id,
            )
            await ctx.message.add_reaction(settings.WAGER_ERROR_REACTION)
    else:
        logger.info(
            "User tried to resolve prediction without replying to a prediction thread."
        )


@bot.command()
async def cancel_prediction(ctx: Context) -> None:
    if ctx.message.reference:
        thread_id = ctx.message.reference.message_id
        try:
            prediction = await Prediction.objects.async_get(thread_id=thread_id)
            async for wager in Wager.objects.select_related().filter(choice__prediction=prediction):  # type: ignore
                # Refund user their wager size
                wager.user.gam_coins += wager.amount
                await wager.user.async_save()
            # Delete the prediction and all associated data
            await prediction.async_delete()
            await ctx.message.add_reaction(settings.WAGER_SUCCESS_REACTION)
        except Prediction.DoesNotExist:
            # This should only happen if someone replies to the wrong message or the prediction already
            # was deleted
            logger.info(
                "User tried cancelling on thread_id %d which does not correspond to a prediction",
                thread_id,
            )
            await ctx.message.add_reaction(settings.WAGER_ERROR_REACTION)
    else:
        logger.info(
            "User tried to cancel prediction without replying to a prediction thread."
        )


@bot.command()
@only_debug()
async def add_coins(ctx: Context, amount: int) -> None:
    user, _ = await GamUser.objects.async_get_or_create(
        discord_id=ctx.message.author.id
    )
    user.gam_coins += amount
    await user.async_save()
