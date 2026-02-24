import os
import discord
import datetime
import emoji
from discord import app_commands
from discord.ext import commands

import random

GUILD = os.getenv('DISCORD_GUILD')
# GUILD = NULL
coinEmoji = emoji.emojize(":coin:")

class economy(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name = "beg", description = "beg for money")
    @app_commands.checks.cooldown(1,1200.0, key=lambda i: (i.guild_id, i.user.id))
    async def beg(self, interaction: discord.Interaction):

        # Get Collection
        db = self.bot.mongoConnect["gyachaDB"]
        collection = db["economy"]

        # Check if user is already in collection, if not, create then insert
        moneyReceived = random.randint(25, 100)
        if await collection.find_one({"disco_id": interaction.user.id, "guild_id": interaction.guild_id}) == None:
            # if await collection.find_one({"disco_id": interaction.user.id}) == None:
            newData = {
                "disco_id": interaction.user.id,
                "guild_id": interaction.guild_id,
                "coins": 0
            }
            # Insert data
            await collection.insert_one(newData)
        # Fetch user's data
        userData = await collection.find_one({"disco_id": interaction.user.id, "guild_id": interaction.guild_id})

        userData["coins"] += moneyReceived
        # Update user's data
        await collection.replace_one({"disco_id": interaction.user.id, "guild_id": interaction.guild_id}, userData)

        embed = discord.Embed(
            colour=discord.Colour.dark_teal(),
            description=f"You just recieved **{moneyReceived}** `{coinEmoji}` ! \n"
                        f"You currently have **{userData["coins"]}** `{coinEmoji}`"
        )
        await interaction.response.send_message(embed=embed)

    @beg.error
    async def begError(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            timeRemaining = str(datetime.timedelta(seconds=int(error.retry_after)))
            await interaction.response.send_message(
                f"Try again in **{timeRemaining}**",
                ephemeral = True
            )

    @app_commands.checks.cooldown(1, 3.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.command(name="wallet", description="check your wallet")
    async def wallet(self, interaction: discord.Interaction):
        # Get Collection
        db = self.bot.mongoConnect["gyachaDB"]
        collection = db["economy"]

        # Check if user is already in collection, if not, create then insert
        if await collection.find_one({"disco_id": interaction.user.id, "guild_id": interaction.guild_id}) == None:
        # if await collection.find_one({"_id": interaction.user.id}) == None:
            newData = {
                "disco_id": interaction.user.id,
                "guild_id": interaction.guild_id,
                "coins": 0
            }
            # Insert data
            await collection.insert_one(newData)

        # userData = await collection.find_one({"disco_id": interaction.user.id, "guild_id": interaction.guild.id})
        userData = await collection.find_one({"disco_id": interaction.user.id, "guild_id": interaction.guild_id})

        embed = discord.Embed(
            colour=discord.Colour.dark_teal(),
            description=f"You have **{userData['coins']}** `{coinEmoji}` !"
        )
        await interaction.response.send_message(embed=embed)

    @wallet.error
    async def begError(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            timeRemaining = str(datetime.timedelta(seconds=int(error.retry_after)))
            await interaction.response.send_message(
                f"Wait 3 seconds before entering another command!",
                ephemeral = True
            )
async def setup(bot: commands.Bot):
    # await bot.add_cog(economy(bot), guilds = [discord.Object(id = GUILD)]
    await bot.add_cog(economy(bot))