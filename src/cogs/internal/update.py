from os import system

from discord import Embed
from discord.ext import commands
from loguru import logger

from src.internal.bot import Bot
from src.internal.context import Context


class Update(commands.Cog):
    """Run bot updates as a command."""

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.group(name="run")
    @commands.is_owner()
    async def run(self, ctx: Context):
        pass

    @run.command(name="update", aliases=["deploy"])
    async def update(self, ctx: Context):
        """Update the bot."""

        msg = await ctx.reply(
            embed=Embed(
                title="Bot Restarting",
                colour=0x87CEEB,
            )
        )

        try:
            await self.bot.db.create_restart(msg.channel.id, msg.id)
        except:
            logger.error("Failed to create DB restart.")

        system("./update.sh")

    @run.command(name="pull")
    async def pull(self, ctx: Context):
        """Update the bot."""

        await ctx.reply(
            embed=Embed(
                title="Pulling from git...",
                colour=0x87CEEB,
            )
        )

        system("git pull origin master")

        await ctx.message.add_reaction("👌")

    @commands.command(name="rsalert", aliases=["alert"])
    @commands.is_owner()
    async def restart_alert(self, ctx: Context, channel: int, value: str):
        """Create a restart alert channel."""

        if value == "on":
            await self.bot.db.create_restart_alert(channel)
            await ctx.reply(f"Now alerting restarts on <#{channel}>")
        else:
            await self.bot.db.delete_restart_alert(channel)
            await ctx.reply(f"No longer alerting restarts on <#{channel}>")


def setup(bot: Bot):
    bot.add_cog(Update(bot))
