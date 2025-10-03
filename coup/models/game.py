from collections import deque
import random
import discord
from .player import Player
from .deck import Deck
from .action import Action


class Game:
    """Model representing the state of an ongoing game."""
    def __init__(self, players: dict):
        # Create Player objects from the input mapping
        self.players = [Player(user_id, user_name) for user_id, user_name in players.items()]
        self.game_thread: discord.Thread | None = None
        self.deck = Deck()
        self.dead_players: list[Player] = []
        self.game_active = True
        self.prev_msg: discord.Message | None = None
        self.action_state = Action()


        # Deal 2 cards to each player
        for player in self.players:
            player.gain_influence(self.deck.draw())
            player.gain_influence(self.deck.draw())

        # Randomize turn order
        if self.players:
            randomized = random.sample(self.players, k=len(self.players))
            self.turn_order = deque(randomized)
            self.current_player = self.turn_order.popleft()
        else:
            raise ValueError("Game has no players.")

    async def game_loop(self, msg: discord.Message):
        """Main game loop."""
        # Create game thread
        try:
            self.game_thread = await msg.create_thread(name="Game Thread")
        except Exception as e:
            print(f"Failed to create thread: {e}")

        # Notify players
        await self.ping_players()

        while self.game_active:
            # Send current
            print("game loop start!")
            await self.take_turn() #TODO: fix here
            print("first turn complete?")
            # wait until turn is complete
            self.advance_turn()
            

    async def ping_players(self):
        """Ping all players at start of game."""
        mentions = " ".join([f"<@{p.user_id}>" for p in self.players])
        await self.game_thread.send(mentions + " The game has begun!")

    def advance_turn(self):
        """
        Advance to the next player's turn.
        Current player moves to the end of the deque.
        Front of the deque becomes current player.
        If no players left to go, only one player left --> end game
        """
        if not self.turn_order:
            self.end_game()
            return
        self.turn_order.append(self.current_player)
        self.current_player = self.turn_order.popleft()

    def get_turn_order_ids(self):
        """Return list of player IDs in turn order."""
        return [p.user_id for p in self.turn_order]

    async def take_turn(self):
        """Handle current player's turn."""
        # Must coup if coins >= 10
        if self.current_player.coins >= 10:
            await self.create_target_message(force_coup=True)
        else:
            print("Create Action Message being called")
            await self.create_action_message()

    async def send_update_msg(self, content: str):
        """Delete previous interactable message and send a log message in thread."""
        if self.prev_msg:
            try:
                await self.prev_msg.delete()
            except:
                pass
        self.prev_msg = None
        await self.game_thread.send(content)

    async def send_interact_msg(self, content: str, view: discord.ui.View, embed: discord.Embed):
        """Send a message with an interactive view."""
        if self.prev_msg:
            try:
                await self.prev_msg.delete()
            except:
                pass
        self.prev_msg = await self.game_thread.send(content=content, view=view, embed=embed)

    async def create_action_message(self):
        """Send dropdown for player action selection."""
        from coup.views.game_views import create_action_view, create_action_embed

        print("action message create function reached!")
        view = create_action_view(self)
        embed = create_action_embed(self)
        await self.send_interact_msg(
            content=f"{self.current_player.user_name}, choose an action!",
            view=view,
            embed=embed
        )

    async def create_target_message(self, force_coup=False):
        """Send dropdown for target selection."""
        from coup.views.game_views import create_target_view, create_action_embed

        view = create_target_view(self, force_coup=force_coup)
        embed = create_action_embed(self)
        await self.send_interact_msg(
            content=f"{self.current_player.user_name}, select a target!",
            view=view,
            embed=embed
        )

    def end_game(self):
        """Ends the current game."""
        self.game_active = False
    