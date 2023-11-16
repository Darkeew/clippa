import discord
from discord.ext import commands

from dotenv import load_dotenv
import os

import asyncio

intents = discord.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)
load_dotenv()


@client.event
async def on_ready():
    await client.tree.sync()
    print(f"{client.user.name} connected successfully.")


async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith('.py'):
            await client.load_extension(f"cogs.{filename[:-3]}")


async def main():
    async with client:
        await load()
        await client.start(os.getenv("DISCORD_TOKEN"))


asyncio.run(main())
