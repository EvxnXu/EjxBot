# main.py
import discord
from discord.ext import commands
from discord.ui import Button, View

# import commands from coup_views.py
from coup_views import create_lobby_view, create_lobby_embed

# Set up intents
intents = discord.Intents.default()
intents.message_content = True

# Create bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

# Debug
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')  # This confirms the bot is logged in

# Coup Global Variables
coup_status = False # A variable to track game's status
players = {} # a variable to track game's players
prev_msg = None


# !coup command
@bot.command(name="coup", help="Start a game of Coup")
async def coup(ctx):
    # initialize variables as global
    global coup_status
    global players

    # if already running game, don't start another
    if coup_status:
        await ctx.send(f'There is already a game of Coup in progress.')

    # otherwise, start a game
    else:
        # set running status to True
        coup_status = True

        # automatically add the author to players
        players[ctx.author.id] = ctx.author.name

        await print_players(ctx)

# !players command
@bot.command(name="players", help="Print current players of Coup")
async def show_players(ctx):
    await ctx.message.delete()
    if not players:
        await ctx.send("No players have joined the game yet.")
    else:
        await print_players(ctx)

# Create Coup Lobby Message
async def print_players(ctx):
    # declare global variables
    global prev_msg

    view = create_lobby_view(players, print_players, coup_status, ctx)
    embed = create_lobby_embed(players)

    # delete the previous lobby message
    if prev_msg != None:
        await prev_msg.delete()

    # output new message. It is now the previously sent message
    prev_msg = await ctx.send(embed=embed, view=view)
       
bot.run('MTMyODg4NTcyMjgxOTcyNzQ3Mg.G_1cyc.Ddxy1AjI2v1_OxYTGb7FJ7FSq_3jUc-hmVF7jM')