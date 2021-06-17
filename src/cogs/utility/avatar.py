from io import BytesIO

from discord import File
from discord.ext import commands
from shavatar import generate

from src.internal.bot import Bot
from src.internal.context import Context


class Avatar(commands.Cog):
    """Generate an avatar with SHAvatar."""

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(name="shavatar")
    async def shavatar(self, ctx: Context) -> None:
        """Generate an avatar with SHAvatar."""

        io = BytesIO()

        avatar = generate(str(ctx.author.id), size=512)
        avatar.save(io, "png")

        await ctx.reply(file=File(io, "avatar.png"))


def setup(bot: Bot):
    bot.add_cog(Avatar(bot))