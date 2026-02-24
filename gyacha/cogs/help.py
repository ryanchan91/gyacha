import os
import discord
import datetime
import emoji
from discord import app_commands
from discord.ext import commands

import random

class help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.checks.cooldown(1, 3.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.command(name="help", description="Show commands")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            colour=discord.Colour.dark_teal(),
            description=f"**/gacha** to roll for waifus \n"
                        f"**/beg** to get coins (20 min cd) \n"
                        f"**/wallet** to check owned coins \n"
                        f"**/inv** to check owned waifus \n "
        )
        await interaction.response.send_message(embed=embed)

    @help.error
    async def helpError(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            timeRemaining = str(datetime.timedelta(seconds=int(error.retry_after)))
            await interaction.response.send_message(
                f"Wait 3 seconds before entering another command!",
                ephemeral=True
            )
async def setup(bot: commands.Bot):
    await bot.add_cog(help(bot))