import discord
from discord.ext import commands
from discord.ui import Button, View

# Set up intents
intents = discord.Intents.default()
intents.message_content = True

# Create bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

# Debug
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')  # This confirms the bot is logged in

# Game of Coup
coup_status = False # A variable to track game's status
players = {} # a variable to track game's players
prev_msg = None

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

# Print Current Players for Game
@bot.command(name="players", help="Print current players of Coup")
async def show_players(ctx):
    await ctx.message.delete()
    if not players:
        await ctx.send("No players have joined the game yet.")
    else:
        await print_players(ctx)

# Create Coup Lobby Message
async def print_players(ctx):
    # add join game button
    coup_join_button = Button(label="Join Game", style=discord.ButtonStyle.blue)

    # add button interaction functionality
    # on click if player is not in the game, add them then redisplay players.
    async def button_callback(interaction: discord.Interaction):
        user = interaction.user
        if user.id not in players:
            players[user.id] = user.name
            await show_players(ctx)

    couop_join_button.callback = button_callback

    join_button = View()
    join_button.add_item(button)

    players_string = "\n".join(players.values())
    embed = discord.Embed(
        title = "Game of Coup!",
        description = "2-6 Player Game",
    )
    embed.add_field(name="Players", value=players_string, inline=False)
    prev_msg = await ctx.send(embed=embed, view=join_button)

    # remove the previous lobby message if it exists
    global prev_msg

    if prev_msg != None:
        await prev_msg.delete()
    # previous message is now this message
    prev_msg = players_message


       
bot.run('MTMyODg4NTcyMjgxOTcyNzQ3Mg.G_1cyc.Ddxy1AjI2v1_OxYTGb7FJ7FSq_3jUc-hmVF7jM')