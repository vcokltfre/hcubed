from discord.ext import commands

from src.internal.bot import Bot
from src.internal.context import Context


class Config(commands.Cog):
    """Change the bot config."""

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(name="prefix")
    @commands.check_any(
        commands.is_owner(), commands.has_guild_permissions(manage_guild=True)
    )
    async def prefix(self, ctx: Context, *, new: str = None):
        """Set or get the guild prefix."""

        if not new:
            guild = await self.bot.db.fetch_guild(ctx.guild.id, ctx.guild.owner_id)
            return await ctx.reply(f"The prefix in this server is `{guild['prefix']}`")

        if len(new) > 16:
            return await ctx.reply("Prefixes should be 16 characters or fewer.")

        await self.bot.db.set_guild_prefix(ctx.guild.id, new)
        await ctx.reply(f"Changed this server's prefix to `{new}`")

        del self.bot.prefixes[ctx.guild.id]


def setup(bot: Bot):
    bot.add_cog(Config(bot))
