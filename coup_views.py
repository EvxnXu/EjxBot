# views.py
from discord.ui import Button, View
import discord

def create_lobby_view(players: dict, print_players, status, ctx):
    # initialize a view
    view = View()

    view.add_item(join_bt(players, print_players, ctx))
    view.add_item(leave_bt(players, print_players, ctx))
    view.add_item(start_bt(players, status, ctx))

    return view

def create_lobby_embed(players: dict):
    # convert display names into a string
    players_string = "\n".join(players.values())

    # create embed with title, description to view
    embed = discord.Embed(
        title = "Game of Coup!",
        description = "2-6 Player Game",
    )
    # add player names to embed
    embed.add_field(name="Players", value=players_string, inline=False)

    return embed

def join_bt(players: dict, print_players, ctx):
    button = Button(label="Join Game", style=discord.ButtonStyle.primary)

    async def callback(interaction: discord.Interaction):
        user = interaction.user
        if user.id not in players and len(players) < 6:
            players[user.id] = user.name
            await print_players(ctx)
    
    button.callback = callback
    return button

def leave_bt(players: dict, print_players, ctx):
    button = Button(label="Leave Game", style=discord.ButtonStyle.red)

    async def callback(interaction: discord.Interaction):
        user = interaction.user
        if user.id in players:
            del players[user.id]
            await print_players(ctx)

    button.callback = callback
    return button

def start_bt(players: dict, status: bool, ctx):
    button = Button(label="Start Game", style=discord.ButtonStyle.green)

    async def callback(interaction: discord.Interaction):
        user = interaction.user
        if len(players) < 2:
            await ctx.send("At least 2 players required to start the game.")
        if user.id in players:
            status = True

    button.callback = callback
    return button


