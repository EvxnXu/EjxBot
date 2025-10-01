# coup_views.py
from discord.ui import Button, View
import discord

def create_lobby_view(coup_cog, ctx):
    """
    Create the lobby view with buttons for join/leave/start game buttons.
    
    Args:
        coup_cog: The instnace of the coup cog to call functions
        ctx: Discord context to pass to functions
    """
    view = View(timeout=None)  # Add timeout=None to prevent expiration
    view.add_item(join_bt(coup_cog, ctx))
    view.add_item(leave_bt(coup_cog, ctx))
    view.add_item(start_bt(coup_cog, ctx))

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

def join_bt(coup_cog, ctx):
    """Create the Join Game button"""
    button = Button(label="Join Game", style=discord.ButtonStyle.primary)

    async def callback(interaction: discord.Interaction):
        user = interaction.user

        # Check if game is full
        if len(coup_cog.players) >= 6:
            await interaction.response.send_message(
                "The game is already full (6/6 players).", 
                ephemeral=True
            )
            return
        
        # Check if already in game
        if user.id in coup_cog.players:
            await interaction.response.send_message(
                "You are already in this game!", 
                ephemeral=True
            )
            return
        
        # Add player
        coup_cog.players[user.id] = user.name
        await interaction.response.defer()  # Acknowledge the interaction
        await coup_cog.print_players(ctx)

    button.callback = callback
    return button

def leave_bt(coup_cog, ctx):
    """Create the Leave Game button"""
    button = Button(label="Leave Game", style=discord.ButtonStyle.red)

    async def callback(interaction: discord.Interaction):
        user = interaction.user

        if user.id not in coup_cog.players:
            await interaction.response.send_message(
                "You are not in this game.", 
                ephemeral=True
                )
            return
            
        # Remove player
        del coup_cog.players[user.id]
        await interaction.response.defer()  # Acknowledge the interaction
        await coup_cog.print_players(ctx)

    button.callback = callback
    return button

def start_bt(coup_cog, ctx):
    """Create the Start Game button"""
    button = Button(label="Start Game", style=discord.ButtonStyle.green)

    async def callback(interaction: discord.Interaction):
        user = interaction.user
       # Check minimum players
        if len(coup_cog.players) < 2:
            await interaction.response.send_message(
                "At least 2 players are required to start the game.", 
                ephemeral=True
            )
            return
        
        # Check if user is in the game
        if user.id not in coup_cog.players:
            await interaction.response.send_message(
                "Only players in the game can start it!", 
                ephemeral=True
            )
            return
            
        # Start the game
        await interaction.response.defer()  # Acknowledge the interaction
        await coup_cog.start_game(ctx)
    
    button.callback = callback
    return button


