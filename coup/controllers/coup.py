# coup.py
import discord
from discord.ext import commands
from views import create_lobby_view, create_lobby_embed
from models.lobby_manager import LobbyManager

class Coup(commands.Cog):
    """
    Discord Cog for playing the Coup card game.
    Manages game lobbies, player management and game state
    """

    def __init__(self, bot):
        self.bot = bot
        self.lobby_mananger = LobbyManager()
        self.lobby_msgs = {} # lobby_id -> last lobby mesasge
    
    # Lobby Commands

    @commands.command(name="coup", help="Start a game of Coup")
    async def coup(self, ctx):
        """Starts a new lobby with a unique lobby ID"""
        
        # Start a new game lobby
        lobby = self.lobby_manager.create_lobby()
        lobby.add_player(ctx.author)
        await self.update_lobby_message(lobby, ctx)

    # Lobby Message Handling

    async def update_lobby_message(self, lobby, ctx):
        """
        Create and display the lobby message with current players and buttons.
        Deletes the previous lobby message if it exists
        """
        view = create_lobby_view(self, lobby, ctx)
        embed = create_lobby_embed(lobby.players)

        # delete the previous lobby message
        prev_msg = self.lobby_msgs.get(lobby.lobby_id)
        if prev_msg:
            try:
                await prev_msg.delete()
            except:
                pass 

        # Send new message and save reference as previous message
        msg = await ctx.send(embed=embed, view=view)
        self.lobby_msgs[lobby.lobby_id] = msg
    
    async def end_game(self, ctx):
        """Ends the current game of coup"""
        if not self.coup_status:
            await ctx.send("No game is currently running")
            return
        
        self.coup_status = False
        self.players.clear()
        self.game = None
        self.prev_msg = None

        await ctx.send("Game ended. Use '!coup' to start a new game.")

    async def print_players(self, ctx):
        """
        Create and display the lobby message with current players and buttons.
        Deletes the previous lobby message if it exists
        """
        view = create_lobby_view(self.players, self, ctx)
        embed = create_lobby_embed(self.players)

        # delete the previous lobby message
        if self.prev_msg is not None:
            try:
                await self.prev_msg.delete()
            except:
                pass 

        # Send new message and save reference as previous message
        self.prev_msg = await ctx.send(embed=embed, view=view)
    
    async def start_game(self, ctx):
        """
        Starts the actual game of Coup
        """

        # TODO: Implement game start logic
        # 1. Create CoupGame instance with players
        # 2. Initilize deck in random order and deal cards
        # 3. Set initial coins for each player
        # 4. Send game start message and player hands to each player
        # 5. Start turn loop
       

async def setup(bot):
    """Setup function to add the Coup cog to the bot."""
    await bot.add_cog(Coup(bot))