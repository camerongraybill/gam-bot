from itertools import groupby, chain
from logging import getLogger
from typing import Optional, Mapping

from discord.enums import Status
from discord.ext import commands, tasks
from discord.ext.commands import Context
from django.db.models import Q

from discord_bot.checks import only_debug
from discord_bot.cog import BaseCog
from .models import Prediction, Account, Wager, PredictionChoice
from . import settings

from discord.ext.commands import Bot

logger = getLogger(__name__)


class GamCoinsCog(BaseCog):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot)
        self.check_user_presence.start()

    @commands.command(
        help="Create a new prediction people can wager on", pass_context=True
    )
    async def make_prediction(
        self, ctx: Context[Bot], prediction_text: str, options: Optional[str]
    ) -> None:
        if not options:
            options = "yes,no"
        thread_message = await ctx.send(
            f"Prediction '{prediction_text}' has been created, reply to this message with the wager command:\n{self.bot.command_prefix}make_wager <choice> <amount>\npossible choices are {options}\nOr use {self.bot.command_prefix}all_in <choice> to bet the farm!"
        )
        prediction_options = options.split(",")
        prediction_model = await Prediction.objects.acreate(
            thread_id=thread_message.id, prediction_text=prediction_text
        )
        await PredictionChoice.objects.abulk_create(
            [
                PredictionChoice(prediction=prediction_model, choice=option.lower())
                for option in prediction_options
            ]
        )

    @commands.command(
        help="Special command for making a wager with all your GamCoins",
        pass_context=True,
    )
    async def all_in(self, ctx: Context[Bot], choice: str) -> None:
        await self.handle_wager(ctx, choice, -1, True)

    @commands.command(
        help="Reply to a prediction message from the bot to make your wager",
        pass_context=True,
    )
    async def make_wager(self, ctx: Context[Bot], choice: str, amount: int) -> None:
        await self.handle_wager(ctx, choice, amount, False)

    async def handle_wager(
        self, ctx: Context[Bot], choice: str, amount: int, all_in: bool
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
                prediction = await Prediction.objects.aget(thread_id=thread_id)
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
                prediction_choice = await PredictionChoice.objects.aget(
                    choice=choice.lower(), prediction=prediction
                )

                if all_in:
                    await Wager.objects.acreate(
                        account=account, amount=account.coins, choice=prediction_choice
                    )

                    account.coins = 0

                    await account.asave()

                    await ctx.message.add_reaction(settings.ALL_IN_REACTION)
                else:
                    account.coins -= amount
                    await account.asave()

                    await Wager.objects.acreate(
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
        help="Reply to a prediction message from the bot to prevent new wagers from being placed",
        pass_context=True,
    )
    async def close(self, ctx: Context[Bot]) -> None:
        if ctx.message.reference:
            thread_id = ctx.message.reference.message_id
            try:
                prediction = await Prediction.objects.aget(thread_id=thread_id)
                if prediction.state != Prediction.State.ACCEPTING_WAGERS:
                    logger.info(
                        "User tried to close prediction thread_id %d but it has been closed already",
                        thread_id,
                    )
                    await ctx.message.add_reaction(settings.ERROR_REACTION)
                    return

                prediction.state = Prediction.State.WAITING_FOR_RESOLUTION
                await prediction.asave()
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

    @commands.command(help="List all open predictions", pass_context=True)
    async def list_predictions(self, ctx: Context[Bot]) -> None:
        predictions = [
            p
            async for p in Prediction.objects.filter(
                ~Q(state=Prediction.State.RESOLVED.value)
            )
        ]
        if not predictions:
            await ctx.send("No predictions are currently available")
        else:
            await ctx.send(
                "Open predictions:" + "\n" + "\n".join([str(p) for p in predictions])
            )

    @commands.command(pass_context=True)
    @only_debug()
    async def add_coins(self, ctx: Context[Bot], amount: int) -> None:
        account = await Account.objects.lookup_account(ctx.message.author.id)
        account.coins += amount
        await account.asave()

    @commands.command(
        help="Reply to a prediction message from the bot to cancel all wagers currently placed",
        pass_context=True,
    )
    async def cancel_prediction(self, ctx: Context[Bot]) -> None:
        if ctx.message.reference:
            thread_id = ctx.message.reference.message_id
            try:
                prediction = await Prediction.objects.aget(thread_id=thread_id)
                if prediction.state == Prediction.State.RESOLVED:
                    logger.info(
                        "User tried cancelling prediction on thread id %d which has already been resolved",
                        thread_id,
                    )
                    await ctx.message.add_reaction(settings.ERROR_REACTION)

                async for wager in Wager.objects.select_related("account").filter(
                    choice__prediction=prediction
                ):
                    # Refund user their wager size
                    account = wager.account
                    account.coins += wager.amount
                    await account.asave()
                # Delete the prediction and all associated data
                await prediction.adelete()
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
        help="Reply to a prediction message from the bot with the actual outcome to pay out the winnings",
        pass_context=True,
    )
    async def resolve(self, ctx: Context[Bot], correct_choice: str) -> None:
        # Resolves a prediction thread by getting all users that made the correct choice
        # and then assigning a payout based on their relative pot contributions
        if ctx.message.reference:
            try:
                prediction = await Prediction.objects.prefetch_related(
                    "predictionchoice_set",
                    "predictionchoice_set__wager_set__account",
                    "predictionchoice_set__wager_set__account__user",
                ).aget(thread_id=ctx.message.reference.message_id)
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
            pot = sum(wager.amount for wager in wagers)

            # Get all wagers associated with the correct choice and sort
            def discord_id_lambda(wager: Wager) -> int:
                return wager.account.user.discord_id

            correct_wagers = sorted(
                [
                    wager
                    for wager in wagers
                    if wager.choice == correct_prediction_choice
                ],
                key=discord_id_lambda,
            )
            # Get the sum of correct wagers
            correct_wagers_pot = sum(wager.amount for wager in correct_wagers)
            # We need to map users to the wagers they placed
            users_to_wagers: Mapping[int, list[Wager]] = {
                k: list(g) for k, g in groupby(correct_wagers, key=discord_id_lambda)
            }
            winner_strings: list[str] = []
            for discord_id, user_wagers in users_to_wagers.items():
                account = user_wagers[0].account
                coins_to_award = int(
                    (sum(wager.amount for wager in user_wagers) / correct_wagers_pot)
                    * pot
                )
                logger.info("Awarding %d coins to user %d", coins_to_award, discord_id)
                account.coins += coins_to_award
                discord_user = await self.bot.fetch_user(discord_id)
                winner_strings.append(f"{discord_user.name} won {coins_to_award} coins")
                await account.asave()
            prediction.state = Prediction.State.RESOLVED
            await prediction.asave()
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
                await account.asave()

    @check_user_presence.before_loop
    async def before_check_user_presence(self) -> None:
        logger.info("Waiting for bot to start before checking user presence")
        await self.bot.wait_until_ready()

    @commands.command(
        help="Get a DM from the bot with your GamCoin balance", pass_context=True
    )
    async def check_balance(self, ctx: Context[Bot]) -> None:
        account = await Account.objects.lookup_account(discord_id=ctx.message.author.id)
        dm_channel = ctx.author.dm_channel or await ctx.author.create_dm()
        await dm_channel.send(f"Your GamCoin balance is {account.coins} coins.")
