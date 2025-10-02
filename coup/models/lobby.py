import asyncio
from discord.ext import commands
from coup.views import create_lobby_view, create_lobby_embed
from .game import Game

class Lobby:
    """Model representing the state of a game lobby."""
    def __init__(self, lobby_id: int, ctx: commands.Context):
        print("Lobby init")
        self.lobby_id = lobby_id
        self.players = {} # user_id -> user_name
        self.game = None # Game State Object
        self.prev_msg = None

        # Add initial member and send lobby message
        self.add_player(ctx.author)
    
    async def run(self, ctx):
        # Put in first update message
        await self.update_message(ctx)

        # Wait for Game to Start (Handled by repeated update messages)
        while not self.game:
            await asyncio.sleep(0.1)
        
        # Put in update message without buttons
        await self.update_message(ctx) # TODO: Change to message saying that lobby has started with lobby id and players
        
        # Wait for Game to finish, resturn result to Coup.py
        result = await self.game.game_loop(self.prev_msg)
        return result

    async def update_message(self, ctx: commands.Context):
        """
        Create and display the lobby message with current players and buttons.
        Deletes the previous lobby message if it exists
        """
        if not self.game: # Join/Leave/Start Buttons only necessary if game hasn't started yet
            view = create_lobby_view(self, ctx)
        else:
            view = None
        embed = create_lobby_embed(self.players) #TODO: Add lobby id to lobby embed

        # delete the previous lobby message if it exists
        if self.prev_msg:
            try:
                await self.prev_msg.delete()
            except:
                pass 

        # Send new message and save reference as previous message
        self.prev_msg = await ctx.send(embed=embed, view=view)
    
    def add_player(self, user):
        self.players[user.id] = user.name

    def remove_player(self, user):
        self.players.pop(user.id, None)
    
    def is_full(self):
        return len(self.players) >= 6

    def is_empty(self):
        return len(self.players) == 0
    
    def can_start(self):
        return len(self.players) >= 2 and not self.is_full()
    
    def create_game(self):
        """Initialize game instance"""
        if not self.can_start():
            raise ValueError("Not correct # of players to start.")
        self.game = Game(self.players)
