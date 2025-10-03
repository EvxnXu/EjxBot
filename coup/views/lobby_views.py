# coup_views.py
import discord
from discord.ui import Button, View


def create_lobby_view(lobby, ctx):
    """
    Create the lobby view with buttons for join/leave/start game buttons.
    """
    view = View(timeout=None)  # Add timeout=None to prevent expiration
    view.add_item(join_bt(lobby, ctx))
    view.add_item(leave_bt(lobby, ctx))
    view.add_item(start_bt(lobby, ctx))

    return view


def create_lobby_embed(players: dict):
    """
    Create the lobby embed showing current players in the lobby.
    
    Args:
        players: Dictionary of current players {user_id: user_name}
    """

    # Convert display names into a string
    if players:
        players_string = "\n".join(players.values())
    else:
        players_string = "No players have joined yet."

    # Create embed with title, description
    embed = discord.Embed(
        title = "Game of Coup!",
        description = "2-6 Player Game",
    )

    # Add player names to embed
    embed.add_field(
        name="Players", 
        value=players_string, 
        inline=False
    )

    return embed

# -------------------- 
# Buttons
# --------------------

def join_bt(lobby, ctx):
    """Create the Join Game button"""
    button = Button(label="Join Game", style=discord.ButtonStyle.primary)

    async def callback(interaction: discord.Interaction):
        user = interaction.user

        # Check if game is full
        if lobby.is_full():
            await interaction.response.send_message(
                "The game is already full (6/6 players).", 
                ephemeral=True
            )
            return
        
        # Check if already in game
        if user.id in lobby.players:
            await interaction.response.send_message(
                "You are already in this game!", 
                ephemeral=True
            )
            return
        # Add player
        lobby.add_player(user)
        await interaction.response.defer()  # Acknowledge the interaction
        await lobby.update_message(ctx)

    button.callback = callback
    return button

def leave_bt(lobby, ctx):
    """Create the Leave Game button"""
    button = Button(label="Leave Game", style=discord.ButtonStyle.red)

    async def callback(interaction: discord.Interaction):
        user = interaction.user

        if user.id not in lobby.players:
            await interaction.response.send_message(
                "You are not in this game.", 
                ephemeral=True
                )
            return

        if lobby.game:
            await interaction.response.send_message(
                "You cannot leave a game in progress.", 
                ephemeral=True
                )
            return
        
        # Remove player
        lobby.remove_player(user)
        await interaction.response.defer()  # Acknowledge the interaction
        await lobby.update_message(ctx)

    button.callback = callback
    return button

def start_bt(lobby, ctx):
    """Create the Start Game button"""
    button = Button(label="Start Game", style=discord.ButtonStyle.green)

    async def callback(interaction: discord.Interaction):
        user = interaction.user

        if lobby.game:
            await interaction.response.send_message(
                "The game has already started.", 
                ephemeral=True
            )
            return
        
        if not lobby.can_start():
            await interaction.response.send_message(
                "Not enough players to start the game. Minimum 2 players required.", 
                ephemeral=True
            )
            return
        
        if user.id not in lobby.players:
            await interaction.response.send_message(
                "Only players in the lobby can start the game.", 
                ephemeral=True
            )
            return

        lobby.create_game()
    
    button.callback = callback
    return button


