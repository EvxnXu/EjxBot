# coup.py
import discord
from discord.ext import commands
from discord.ui import View

# import commands from coup_views.py
from coup_views import create_lobby_view, create_lobby_embed

class Coup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.coup_status = False
        self.players = {}
        self.prev_msg = None

    # !coup command
    @commands.command(name="coup", help="Start a game of Coup")
    async def coup(self, ctx):
        
        # if already running game, don't start another
        if self.coup_status:
            await ctx.send(f'There is already a game of Coup in progress.')
        else:
            # otherwise, start a game, add person starting the game and reprint msg
            self.coup_status = True
            self.players[ctx.author.id] = ctx.author.name
            await self.print_players(ctx)

    # !players command
    @commands.command(name="players", help="Print current players of Coup")
    async def show_players(self, ctx):
        await ctx.message.delete()
        if not self.players:
            await ctx.send("No players have joined the game yet.")
        else:
            await self.print_players(ctx)

    # Create Coup Lobby Message
    async def print_players(self, ctx):

        view = create_lobby_view(self.players, self.print_players, self.coup_status, ctx)
        embed = create_lobby_embed(self.players)

        # delete the previous lobby message
        if self.prev_msg is not None:
            await self.prev_msg.delete()

        # output new message. It is now the previously sent message
        self.prev_msg = await ctx.send(embed=embed, view=view)
       

async def setup(bot):
    await bot.add_cog(Coup(bot))