# bot.py
import os

import discord
import random
import aiohttp
import asyncio
import motor.motor_asyncio
from dotenv import load_dotenv
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
# GUILD = os.getenv('DISCORD_GUILD')
APPID = os.getenv('DISCORD_APPID')
MONGO = os.getenv('MONGO_URI')

# client =
bot = commands.Bot(command_prefix='!', intents=intents)

class myBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='$',
            intents = discord.Intents.all(),
            application_id = APPID
        )
        self.initial_extensions = [
            "cogs.economy",
            "cogs.gacha",
            "cogs.test",
            "cogs.help"
        ]
    async def setup_hook(self):
        self.session = aiohttp.ClientSession()

        for ext in self.initial_extensions:
            await self.load_extension(ext)

        # await bot.tree.sync(guild = discord.Object(id = GUILD))
        await bot.tree.sync()

    async def close(self):
        await super().close()
        await self.session.close()

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')

bot = myBot() # this is where the fun begins

@bot.event
async def on_guild_join(guild):
    db = bot.mongoConnect["gyachaServers"]
    collection = db["guildIDs"]

    if await collection.find_one({"guildID": guild.id}) == None:
        newData = {
            "guildID": guild.id,
            "guildName": guild.name
        }
        # Insert data
        await collection.insert_one(newData)
 
async def main():
    async with bot:
        bot.mongoConnect = motor.motor_asyncio.AsyncIOMotorClient(MONGO)
        await bot.start(TOKEN)

asyncio.run(main())