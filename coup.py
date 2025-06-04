# coup.py
import discord
from discord.ext import commands
from discord.ui import View

# import views from coup_views.py
from coup_views import create_lobby_view, create_lobby_embed

class Coup(commands.Cog):
    """
    Discord Cog for playing the Coup card game.
    Manages game lobbies, player management and game state
    """

    def __init__(self, bot):
        self.bot = bot
        self.coup_status = False # True (Game in progress), False (No game)
        self.players = {} # user_id: user_name
        self.prev_msg = None # Track the lobby message to update/delete
        self.game = None # Placeholder for game state object

    @commands.command(name="coup", help="Start a game of Coup")
    async def coup(self, ctx):
        """Starts a game of coup if not already running"""

        # Check if a game is running
        if self.coup_status:
            await ctx.send(f'There is already a game of Coup in progress.')
            return
        
        # Start a new game
        self.coup_status = True
        self.players[ctx.author.id] = ctx.author.name
        await self.print_players(ctx)

    @commands.command(name="players", help="Print current players of Coup")
    async def show_players(self, ctx):
        """Display the current players in the lobby"""
        try:
            await ctx.message.delete()
        except:
            pass # Ignore if cannot delete

        if not self.players:
            await ctx.send("No players have joined the game yet.")
        else:
            await self.print_players(ctx)
    
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