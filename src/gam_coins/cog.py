from itertools import groupby, chain
from logging import getLogger
from typing import Optional, Mapping, TYPE_CHECKING

from discord.enums import Status
from discord.ext import commands, tasks
from discord.ext.commands import Context
from django.db.models import Q

from discord_bot.checks import only_debug
from discord_bot.cog import BaseCog
from .models import Prediction, Account, Wager, PredictionChoice
from . import settings

if TYPE_CHECKING:
    from discord.ext.commands import Bot

logger = getLogger(__name__)


# pylint: disable=no-self-use
class GamCoinsCog(BaseCog):
    def __init__(self, bot: "Bot[Context]") -> None:
        super().__init__(bot)
        # pylint: disable=no-member
        self.check_user_presence.start()

    @commands.command(help="Create a new prediction people can wager on")
    async def make_prediction(
        self, ctx: Context, prediction_text: str, options: Optional[str]
    ) -> None:
        if not options:
            options = "yes,no"
        thread_message = await ctx.send(
            f"Prediction '{prediction_text}' has been created, reply to this message with the wager command:\n{self.bot.command_prefix}make_wager <choice> <amount>\npossible choices are {options}\nOr use {self.bot.command_prefix}all_in <choice> to bet the farm!"
        )
        prediction_options = options.split(",")
        prediction_model = await Prediction.async_qs().async_create(
            thread_id=thread_message.id, prediction_text=prediction_text
        )
        await PredictionChoice.async_qs().async_bulk_create(
            [
                PredictionChoice(prediction=prediction_model, choice=option.lower())
                for option in prediction_options
            ]
        )

    @commands.command(help="Special command for making a wager with all your GamCoins")
    async def all_in(self, ctx: Context, choice: str) -> None:
        await self.handle_wager(ctx, choice, -1, True)

    @commands.command(
        help="Reply to a prediction message from the bot to make your wager"
    )
    async def make_wager(self, ctx: Context, choice: str, amount: int) -> None:
        await self.handle_wager(ctx, choice, amount, False)

    async def handle_wager(
        self, ctx: Context, choice: str, amount: int, all_in: bool
    ) -> None:
        if ctx.message.reference:
            thread_id = ctx.message.reference.message_id
            account = await Account.objects.lookup_account(ctx.message.author.id)
            if not all_in and amount > account.coins:
                logger.info(
                    "User %d does not have enough GamCoins to wager (tried wagering %d, only had %d)",
                    account.user.discord_id,
                    amount,
                    account.coins,
                )
                await ctx.message.add_reaction(settings.NO_MONEY_REACTION)
                return

            try:
                prediction = await Prediction.objects.async_get(thread_id=thread_id)
                if prediction.state != Prediction.State.ACCEPTING_WAGERS:
                    logger.info(
                        "User tried wagering on closed prediction thread_id %d",
                        thread_id,
                    )
                    await ctx.message.add_reaction(settings.ERROR_REACTION)
                    return

            except Prediction.DoesNotExist:
                # This should only happen if someone replies to the wrong message
                logger.info(
                    "User tried wagering on thread_id %d which does not correspond to a prediction",
                    thread_id,
                )
                await ctx.message.add_reaction(settings.ERROR_REACTION)
                return

            try:
                prediction_choice = await PredictionChoice.objects.async_get(
                    choice=choice.lower(), prediction=prediction
                )

                if all_in:
                    await Wager.objects.async_create(
                        account=account, amount=account.coins, choice=prediction_choice
                    )

                    account.coins = 0

                    await account.async_save()

                    await ctx.message.add_reaction(settings.ALL_IN_REACTION)
                else:
                    account.coins -= amount
                    await account.async_save()

                    await Wager.objects.async_create(
                        account=account, amount=amount, choice=prediction_choice
                    )

                    await ctx.message.add_reaction(settings.SUCCESS_REACTION)
            except PredictionChoice.DoesNotExist:
                logger.info(
                    "User's provided choice %s did not match any choices available for prediction %d",
                    choice,
                    prediction.thread_id,
                )
                await ctx.message.add_reaction(settings.ERROR_REACTION)
        else:
            logger.info("User tried to wager without replying to a prediction thread.")

    @commands.command(
        help="Reply to a prediction message from the bot to prevent new wagers from being placed"
    )
    async def close(self, ctx: Context) -> None:
        if ctx.message.reference:
            thread_id = ctx.message.reference.message_id
            try:
                prediction = await Prediction.objects.async_get(thread_id=thread_id)
                if prediction.state != Prediction.State.ACCEPTING_WAGERS:
                    logger.info(
                        "User tried to close prediction thread_id %d but it has been closed already",
                        thread_id,
                    )
                    await ctx.message.add_reaction(settings.ERROR_REACTION)
                    return

                prediction.state = Prediction.State.WAITING_FOR_RESOLUTION
                await prediction.async_save()
                await ctx.message.add_reaction(settings.SUCCESS_REACTION)
            except Prediction.DoesNotExist:
                # This should only happen if someone replies to the wrong message
                logger.info(
                    "User tried closing on thread_id %d which does not correspond to a prediction",
                    thread_id,
                )
                await ctx.message.add_reaction(settings.ERROR_REACTION)
        else:
            logger.info(
                "User tried to close prediction without replying to a prediction thread."
            )

    @commands.command(help="List all open predictions")
    async def list_predictions(self, ctx: Context) -> None:
        predictions = (
            await Prediction.objects.all()
            .filter(~Q(state=Prediction.State.RESOLVED.value))
            .to_list()
        )
        if not predictions:
            await ctx.send("No predictions are currently available")
        else:
            await ctx.send(
                "Open predictions:" + "\n" + "\n".join([str(p) for p in predictions])
            )

    @commands.command()
    @only_debug()
    async def add_coins(self, ctx: Context, amount: int) -> None:
        account = await Account.objects.lookup_account(ctx.message.author.id)
        account.coins += amount
        await account.async_save()

    @commands.command(
        help="Reply to a prediction message from the bot to cancel all wagers currently placed"
    )
    async def cancel_prediction(self, ctx: Context) -> None:
        if ctx.message.reference:
            thread_id = ctx.message.reference.message_id
            try:
                prediction = await Prediction.objects.async_get(thread_id=thread_id)
                if prediction.state == Prediction.State.RESOLVED:
                    logger.info(
                        "User tried cancelling prediction on thread id %d which has already been resolved",
                        thread_id,
                    )
                    await ctx.message.add_reaction(settings.ERROR_REACTION)

                async for wager in Wager.objects.select_related("account").filter(choice__prediction=prediction):  # type: ignore
                    # Refund user their wager size
                    account = wager.account
                    account.coins += wager.amount
                    await account.async_save()
                # Delete the prediction and all associated data
                await prediction.async_delete()
                await ctx.message.add_reaction(settings.SUCCESS_REACTION)
            except Prediction.DoesNotExist:
                # This should only happen if someone replies to the wrong message or the prediction already
                # was deleted
                logger.info(
                    "User tried cancelling on thread_id %d which does not correspond to a prediction",
                    thread_id,
                )
                await ctx.message.add_reaction(settings.ERROR_REACTION)
        else:
            logger.info(
                "User tried to cancel prediction without replying to a prediction thread."
            )

    @commands.command(
        help="Reply to a prediction message from the bot with the actual outcome to pay out the winnings"
    )
    async def resolve(self, ctx: Context, correct_choice: str) -> None:
        # pylint: disable=too-many-locals
        # Resolves a prediction thread by getting all users that made the correct choice
        # and then assigning a payout based on their relative pot contributions
        if ctx.message.reference:
            try:
                prediction = (
                    await Prediction.async_qs()
                    .prefetch_related(
                        "predictionchoice_set",
                        "predictionchoice_set__wager_set__account",
                        "predictionchoice_set__wager_set__account__user",
                    )
                    .async_get(thread_id=ctx.message.reference.message_id)
                )
            except Prediction.DoesNotExist:
                # This should only happen if someone replies to the wrong message
                logger.info(
                    "User tried resolving on thread_id %d which does not correspond to a prediction",
                    ctx.message.reference.message_id,
                )
                await ctx.message.add_reaction(settings.ERROR_REACTION)
                return
            if prediction.state == Prediction.State.RESOLVED:
                logger.info(
                    "User tried to resolve a prediction that has already been resolved on thread %d",
                    ctx.message.reference.message_id,
                )
                await ctx.message.add_reaction(settings.ERROR_REACTION)
                return

            correct_prediction_choice = next(
                (
                    x
                    for x in prediction.predictionchoice_set.all()
                    if x.choice == correct_choice.lower()
                ),
                None,
            )
            if not correct_prediction_choice:
                logger.info(
                    "Correct choice %s did not match any choices available for prediction %d",
                    correct_choice,
                    prediction.thread_id,
                )
                await ctx.message.add_reaction(settings.ERROR_REACTION)
                return
            # Get all wagers associated with this prediction, select_related to get our FK models
            wagers = list(
                chain.from_iterable(
                    x.wager_set.all() for x in prediction.predictionchoice_set.all()
                )
            )
            pot = sum([wager.amount for wager in wagers])
            # Get all wagers associated with the correct choice and sort
            discord_id_lambda = lambda wager: wager.account.user.discord_id
            correct_wagers = sorted(
                [
                    wager
                    for wager in wagers
                    if wager.choice == correct_prediction_choice
                ],
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
                account = user_wagers[0].account
                coins_to_award = int(
                    (sum([wager.amount for wager in user_wagers]) / correct_wagers_pot)
                    * pot
                )
                logger.info("Awarding %d coins to user %d", coins_to_award, discord_id)
                account.coins += coins_to_award
                discord_user = await self.bot.fetch_user(discord_id)
                winner_strings.append(f"{discord_user.name} won {coins_to_award} coins")
                await account.async_save()
            prediction.state = Prediction.State.RESOLVED
            await prediction.async_save()
            await ctx.message.reply(f"{', '.join(winner_strings)}!")
        else:
            logger.info(
                "User tried to resolve prediction without replying to a prediction thread."
            )
            await ctx.message.add_reaction(settings.ERROR_REACTION)

    @tasks.loop(minutes=1.0)
    async def check_user_presence(self) -> None:
        for user in self.bot.get_all_members():
            account = await Account.objects.lookup_account(user.id)
            if (
                isinstance(user.status, Status)
                and user.status is Status.online
                and not user.bot
            ):
                account.coins += settings.INCOME_PER_MINUTE
                await account.async_save()

    @check_user_presence.before_loop  # type: ignore
    async def before_check_user_presence(self) -> None:
        logger.info("Waiting for bot to start before checking user presence")
        await self.bot.wait_until_ready()

    @commands.command(help="Get a DM from the bot with your GamCoin balance")
    async def check_balance(self, ctx: Context) -> None:
        account = await Account.objects.lookup_account(discord_id=ctx.message.author.id)
        dm_channel = ctx.author.dm_channel or await ctx.author.create_dm()
        await dm_channel.send(f"Your GamCoin balance is {account.coins} coins.")
