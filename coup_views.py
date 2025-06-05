# views.py
from discord.ui import Button, View
import discord

def create_join_game_button(players: dict, ctx, print_players):
    button = Button(label="Join Game", style=discord.ButtonStyle.primary)

    async def callback(interaction: discord.Interaction):
        user = interaction.user
        if user.id not in players:
            players[user.id] = user.name
            await print_players(ctx)
    
    button.callback = callback
    return button

def create_leave_game_button(players: dict, ctx, print_players):
    button = Button(label="Leave Game", style=discord.ButtonStyle.red)

    async def callback(interaction: discord.Interaction):
        user = interaction.user
        if user.id in players:
            del players[user.id]
            await print_players(ctx)

    button.callback = callback
    return button

