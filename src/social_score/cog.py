from logging import getLogger

from discord import RawReactionActionEvent, TextChannel, GroupChannel, PartialEmoji
from discord.ext import commands
from discord.ext.commands import Context

from discord_bot.checks import is_in_channel
from discord_bot.cog import BaseCog
from discord_bot.models import DiscordUser
from social_score.models import SocialScore, EmojiScore

logger = getLogger(__name__)


class SocialScoreCog(BaseCog):

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent) -> None:
        await self.apply_emoji_score(payload, 1)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent) -> None:
        # -1 means remove
        await self.apply_emoji_score(payload, -1)

    async def apply_emoji_score(
        self,
        payload: RawReactionActionEvent,
        score_multiplier: int
    ) -> None:
        channel = await self.bot.fetch_channel(payload.channel_id)
        if isinstance(channel, (TextChannel, GroupChannel)):
            message = await channel.fetch_message(payload.message_id)
            if message.author.id != payload.user_id:
                score: SocialScore = await SocialScore.objects.get_or_create(
                    user=await DiscordUser.objects.lookup_user(message.author.id)
                )[0]
                emoji_id = str(payload.emoji.id or payload.emoji)
                try:
                    logger.info(emoji_id)
                    emoji_score = await EmojiScore.objects.async_get(
                        emoji_id=emoji_id
                    )
                    logger.debug("User's current social score is %d", score.score)
                    score.score += emoji_score.score * score_multiplier
                    logger.debug("User's new social score is %d", score.score)
                    await score.async_save()
                except EmojiScore.DoesNotExist:
                    logger.debug("No emoji score registered for emoji ID %s", emoji_id)

    @commands.command()
    async def show_score(self, ctx: Context) -> None:
        score: SocialScore = await SocialScore.objects.get_or_create(
            user=await DiscordUser.objects.lookup_user(ctx.message.author.id)
        )[0]
        await ctx.send(f"Your social score is currently {score.score}")

    @commands.command()
    @is_in_channel({"bot-commands"})
    async def register_score(
        self,
        ctx: Context,
        emoji: PartialEmoji | str,
        score: int
    ) -> None:
        if isinstance(emoji, PartialEmoji):
            emoji_id = str(emoji.id)
        else:
            emoji_id = emoji
        logger.info("Registering emoji_id %s with score %d", emoji_id, score)
        # We don't actually need the resulting object here
        await EmojiScore.objects.async_update_or_create(
            emoji_id=emoji_id, defaults={"score": score}
        )
        await ctx.message.reply("Your emoji score was registered/updated successfully")


