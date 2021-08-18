from datetime import datetime, timedelta
from time import mktime

from discord import AllowedMentions
from discord.ext import commands, tasks
from loguru import logger
from parsedatetime import Calendar

from src.internal.bot import Bot
from src.internal.context import Context


class Reminders(commands.Cog):
    """Set reminders."""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.cal = Calendar()
        self.remind_loop.start()

    @commands.command(name="remind", aliases=["remindme"])
    async def remind(self, ctx: Context, t: str, *, message: str):
        """Set a reminder."""

        parsed, success = self.cal.parse(t)

        if not success:
            return await ctx.reply("Please use a valid time string, such as 3d6h.")

        time = mktime(parsed)
        dt = datetime.fromtimestamp(time)

        td = dt - datetime.utcnow()
        total_diff = td.total_seconds()

        if total_diff < 5:
            return await ctx.reply(
                "I can't create reminders less than 5 seconds in the future!"
            )

        id = await self.bot.db.create_reminder(
            ctx.author.id, ctx.guild.id, ctx.channel.id, ctx.message.id, dt, message
        )

        await ctx.reply(
            f"Reminder created with ID {id} set to remind you at <t:{int(dt.timestamp())}:F>."
        )

    @tasks.loop(seconds=10)
    async def remind_loop(self):
        await self.bot.wait_until_ready()

        rs = await self.bot.db.get_expired_reminders()

        for reminder in rs:
            if reminder["expires"] > datetime.now():
                continue
            logger.info(
                f"Actioning reminder ID {reminder['id']} from {reminder['userid']}"
            )
            await self.bot.db.mark_reminder_completed(reminder["id"])

            channel = self.bot.get_channel(reminder["cid"])
            if not channel:
                continue

            jump = f"https://discord.com/channels/{reminder['gid']}/{reminder['cid']}/{reminder['mid']}"

            await channel.send(
                f"<@{reminder['userid']}> reminder:\n{reminder['content']}\n\nOriginal message: {jump}",
                allowed_mentions=AllowedMentions(users=True),
            )


def setup(bot: Bot):
    bot.add_cog(Reminders(bot))
