# main.py
import asyncio
import discord
from discord.ext import commands
from coup import setup as setup_coup

# Set up intents
intents = discord.Intents.default()
intents.message_content = True

# Create bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

# Debug
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')  # This confirms the bot is logged in

async def main():
    # Load Coup cog

    await setup_coup(bot)

    await bot.start('MTMyODg4NTcyMjgxOTcyNzQ3Mg.G_1cyc.Ddxy1AjI2v1_OxYTGb7FJ7FSq_3jUc-hmVF7jM')

asyncio.run(main())