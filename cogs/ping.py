import discord
from discord.ext import commands
from discord import app_commands

import os


class Ping(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Cog {os.path.basename(__file__)[:-3]} loaded.")

    @app_commands.command(name="ping", description="Shows the bot's latency in ms.")
    async def ping(self, interaction: discord.Interaction):
        bot_latency = round(self.client.latency * 1000)
        await interaction.response.send_message(f"Pong! {bot_latency} ms.")


async def setup(client):
    await client.add_cog(Ping(client))
