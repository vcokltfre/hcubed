from datetime import timedelta
from time import time

from discord import Embed
from discord.ext import commands
from git import Repo

from src.internal.bot import Bot
from src.internal.context import Context

desc = """
I'm logged in as {bot} ({bot.id}).
I can see {guilds} servers, and {users} users.
My current uptime is {uptime}.
I have {cogs} cogs loaded with a total of {commands} commands.
"""


class Status(commands.Cog):
    """Get the current bot status."""

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(name="status")
    @commands.is_owner()
    async def status(self, ctx: Context):
        """Get the current bot status."""

        description = desc.format(
            bot=self.bot.user,
            guilds=len(self.bot.guilds),
            users=len(self.bot.users),
            uptime=str(timedelta(seconds=round(time() - self.bot.start_time))),
            cogs=len(self.bot.cogs),
            commands=len(self.bot.commands),
        )

        embed = Embed(
            title="h³ status",
            colour=0x87CEEB,
            timestamp=ctx.message.created_at,
            description=description,
        )

        embed.set_author(
            name=str(self.bot.user),
            icon_url=(str(self.bot.user.avatar_url)),
        )

        repo = Repo(".")

        embed.add_field(
            name="Commit",
            value=f"[{str(repo.head.commit)[:7]}](https://github.com/vcokltfre/hcubed/commit/{repo.head.commit})",
        )

        embed.set_footer(
            icon_url=(str(self.bot.user.avatar_url)),
            text=str(repo.head.commit),
        )

        embed.add_field(
            name="Repository",
            value="https://github.com/vcokltfre/hcubed",
        )

        await ctx.reply(embed=embed)


def setup(bot: Bot):
    bot.add_cog(Status(bot))
