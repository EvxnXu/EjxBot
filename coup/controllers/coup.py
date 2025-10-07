# coup.py
import discord
import logging
from discord.ext import commands
from coup.models import Lobby

logger = logging.getLogger("coup")

class Coup(commands.Cog):
    """
    Discord Cog for playing the Coup card game.
    Manages game lobbies and Database
    """

    def __init__(self, bot):
        logger.info("Coup cog initialized.")
        self.bot = bot
        self.lobbies = {} # Lobby ID -> Lobby Instance
        self.next_id = 1
    
    # --------------
    # Lobby Commands
    # --------------

    @commands.command(name="coup", help="Start a game of Coup")
    async def coup(self, ctx: commands.Context):
        """Starts a new lobby with a unique lobby ID"""
        # Create lobby
        lobby = Lobby(self.next_id, ctx)
        self.lobbies[self.next_id] = lobby

        # Debug Statement
        logger.info(f"Lobby {lobby.lobby_id} created.")

        # Update next lobby id
        self.next_id += 1

        results = await lobby.run(ctx)

        # TODO: DB does something with results

        return

    
    # -----------------
    # Database Commands
    # -----------------
       

async def setup(bot):
    """Setup function to add the Coup cog to the bot."""
    await bot.add_cog(Coup(bot))