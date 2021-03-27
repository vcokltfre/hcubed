from discord import DMChannel
from discord.ext.commands import check

from src.internal.context import Context


def can_access(name: str, allow_dms: bool = False):
    async def predicate(ctx: Context):
        if await ctx.bot.is_owner(ctx.author):
            return True

        user = await ctx.bot.db.fetch_user(ctx.author.id)

        if user["plevel"] >= 1000:
            return True

        if user["banned"]:
            return False

        if isinstance(ctx.channel, DMChannel):
            if allow_dms:
                return True
            return False

        guild = await ctx.bot.db.fetch_guild(ctx.guild.id, ctx.guild.owner_id)

        if guild["plevel"] >= 1000:
            return True

        if guild["banned"]:
            return False

        # TODO: implement override logic

        return True

    return check(predicate)
