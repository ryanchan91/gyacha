import discord
import requests
import json
import os
import datetime
import emoji
import random
import Paginator
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands

class gacha(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.checks.cooldown(1, 3.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.command(name = "gacha", description = "Roll for characters")
    async def gacha(self, interaction: discord.Interaction):
        card_url = "https://api.nekosbest.im/search"
        db = self.bot.mongoConnect["gyachaDB"]
        collection = db["economy"]
        card_collection = db["card_inv"]
        userData = await collection.find_one({"disco_id": interaction.user.id, "guild_id": interaction.guild_id})

        if(userData['coins'] >= 25):

            tagList = []
            gifFlag = False
            includeTag = None
            excludeTag = None  # None is NULL
            randomNum = random.randint(1, 100)
            print(randomNum)
            if (randomNum > 40):  # 60% chance
                rarity = "C"
            elif (randomNum > 15):  # 25% chance
                rarity = "R"
            elif (randomNum > 5):  # 10% chance
                rarity = "RR"
            else:
                rarity = "SP"  # 5%
                # gifFlag = True

            # rarity = "SP" # Rarity manip

            if (rarity == "C"):
                rarityEmoji = emoji.emojize(":star::star::star:")
            elif (rarity == "R"):
                rarityEmoji = emoji.emojize(":star::star::star::star:")
                tagList = ["sword"]
            elif (rarity == "RR"):
                rarityEmoji = emoji.emojize(":star::star::star::star::star:")
                tagList = ["shield"]
                excludeTag = ["mage"]
            else:
                rarityEmoji = emoji.emojize(":glowing_star:")
                gifFlag = True

            url = 'https://api.nekosbest.im/search'
            params = {
                'included_tags': [tagList]
                'gif': gifFlag,
                'excluded_tags': [excludeTag]
            }

            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()

                if await card_collection.find_one({"disco_id": interaction.user.id, "guild_id": interaction.guild_id, "card_id": data["images"][0]["image_id"]}) == None:
                    # print(data["images"][0]["extension"])
                    newData = {
                        "disco_id": interaction.user.id,
                        "guild_id": interaction.guild_id,
                        "card_id": data["images"][0]["image_id"],
                        "rarity": rarity,
                        "img_type": data["images"][0]["extension"]
                        # "card_url": data["images"][0]["url"]
                    }
                    # Insert data
                    await card_collection.insert_one(newData)
                    userData['coins'] -= 25
                    await collection.replace_one({"disco_id": interaction.user.id, "guild_id": interaction.guild_id},
                                                 userData)
                    embed = discord.Embed(
                        colour=discord.Colour.dark_teal(),
                        description=f"**Cost**: \n"
                                    f"You have spent **`25`** \n"
                                    f"You have **`{userData["coins"]}`** remaining",
                        title="`[" + rarityEmoji + "]`" + " Character #" + str(data["images"][0]["image_id"])
                    )
                    embed.set_author(name="You just got: ", icon_url=interaction.user.avatar.url)

                    embed.set_image(url=data["images"][0]["url"])
                    if(rarity == "SP"):
                        await interaction.response.send_message("@here", embed=embed)
                    else:
                        await interaction.response.send_message(embed=embed)

                else: #User already owns this card id
                    userData['coins'] -= 25
                    embed = discord.Embed(
                        colour=discord.Colour.dark_teal(),
                        description=f"You rolled a duplicate! \n"
                                    f"Refunding..."
                    )
                    await interaction.response.send_message(embed=embed)
                    userData['coins'] += 25
                    await collection.replace_one({"disco_id": interaction.user.id, "guild_id": interaction.guild_id}, userData)
            else:
                print("Request failed with status code ", response.status_code)
        else: # if user has less than 25 coins
            embed = discord.Embed(
                colour=discord.Colour.dark_teal(),
                description="Not enough coins to gacha! \n"
                        "You can use **/beg** to get coins!"
            )
        await interaction.response.send_message(embed=embed)
    @gacha.error
    async def gachaError(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            timeRemaining = str(datetime.timedelta(seconds=int(error.retry_after)))
            await interaction.response.send_message(
                f"Wait 3 seconds before entering another command!",
                ephemeral=True
            )

    @app_commands.checks.cooldown(1, 3.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.command(name="inv", description="view your collection")
    @app_commands.choices(choice=[
        app_commands.Choice(name="SP", value="0"),
        app_commands.Choice(name="5*", value="1"),
        app_commands.Choice(name="all", value="2")
    ])
    @app_commands.choices(choice2=[
        app_commands.Choice(name="show", value="show"),
        app_commands.Choice(name="hide", value="hide")
    ])
    async def inv(self, interaction: discord.Interaction, choice: app_commands.Choice[str], choice2: app_commands.Choice[str]):

        if(choice2.value != "show"):
            await interaction.response.defer(ephemeral=True, thinking=True)
        else:
            await interaction.response.defer(ephemeral=False, thinking=True)


        # await interaction.response.defer(ephemeral=True, thinking=True)

        card_url = "https://api.nekosbest.im/search"
        # Get Collection
        db = self.bot.mongoConnect["gyachaDB"]
        collection = db["card_inv"]

        # Check if user is already in collection
        if await collection.find_one({"disco_id": interaction.user.id, "guild_id": interaction.guild_id}) == None:
            embed = discord.Embed(
                colour=discord.Colour.dark_teal(),
                description="No cards in collection!"
            )
            await interaction.followup.send(embed=embed)
        else:
            cardURL = []
            # userData = await collection.find({"disco_id": interaction.user.id, "guild_id": interaction.guild_id}
            # IMPORTANT LOOP

            userData = collection.find({"disco_id": interaction.user.id, "guild_id": interaction.guild_id})
            async for x in userData:
                cardURL.append(x)

            embeds = []

            for i in cardURL:
                URL = card_url + str(i["card_id"]) + str(i["img_type"])
                rarity = i["rarity"]

                if(choice.value == '0'):
                    if (rarity != "SP"):
                        continue
                elif(choice.value == '1'):
                    if (rarity != "RR" and rarity != "SP"):
                        continue

                if (rarity == "C"):
                    rarityEmoji = emoji.emojize(":star::star::star:")
                elif (rarity == "R"):
                    rarityEmoji = emoji.emojize(":star::star::star::star:")
                elif (rarity == "RR"):
                    rarityEmoji = emoji.emojize(":star::star::star::star::star:")
                else:
                    rarityEmoji = emoji.emojize(":glowing_star:")

                embed = discord.Embed(colour = discord.Colour.dark_teal(),
                                      title ="`[" + rarityEmoji + "]`" + " Character #" + str(i["card_id"]))
                embed.set_author(name=interaction.user.name + "'s card collection",
                                 icon_url=interaction.user.avatar.url)
                embed.set_image(url=URL)
                embeds.append(embed)

            await Paginator.Simple().start(interaction, pages=embeds)

    @inv.error
    async def gachaError(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            timeRemaining = str(datetime.timedelta(seconds=int(error.retry_after)))
            await interaction.response.send_message(
                f"Wait 3 seconds before entering another command!",
                ephemeral=True
            )
async def setup(bot: commands.Bot):
    # await bot.add_cog(economy(bot), guilds = [discord.Object(id = GUILD)]
    await bot.add_cog(gacha(bot))
