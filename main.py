# main.py
import asyncio
import discord
import os
from discord.ext import commands
from coup.controllers import setup as setup_coup
from utils import setup_logger
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()

# Setup up loggers
coup_logger = setup_logger("coup")
bot_logger = setup_logger("bot")

# Set up intents
intents = discord.Intents.default()
intents.message_content = True

# Create bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

# Debug
@bot.event
async def on_ready():
    bot_logger.info(f'Logged in as {bot.user}')  # This confirms the bot is logged in

async def main():
    # Load Coup cog
    await setup_coup(bot)
    await bot.start(os.getenv("DISCORD_BOT_TOKEN"))

asyncio.run(main())