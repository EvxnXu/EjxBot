from collections import deque
import random
import discord
from .player import Player
from .deck import Deck


class Game:
    """Model representing the state of an ongoing game.

    Args:
        players: dict mapping user_id -> user_name (same shape as Lobby.players)
    """
    def __init__(self, players: dict):
        
        # ---------------------------------
        # Create necessary member variables
        # ---------------------------------

        # Create Player objects from the input mapping
        # players is expected to be a dict: {user_id: user_name}
        self.players = [Player(user_id, user_name) for user_id, user_name in players.items()]
        self.game_thread = None # Thread for all messages relating to game
        self.deck = Deck() # Deck of cards
        self.dead_players = [] # List of Dead Players for Reference
        self.game_active = True # State variable for run function   

        # ---------------
        # Game Init Logic
        # ---------------

        # Deal 2 cards to each player
        for player in self.players:
            player.gain_influence(self.deck.draw())
            player.gain_influence(self.deck.draw())

        # Randomize turn order using random.sample and store in a deque for efficient rotation
        if self.players:
            randomized = random.sample(self.players, k=len(self.players))
            self.turn_order = deque(randomized)
            self.current_player = self.turn_order[0]
        else:
            raise ValueError("Game has no players.")

    async def game_loop(self, msg):
        # Create Game Thread
        print("Creating Game Thread")

        try:
            self.game_thread = await msg.create_thread(
                name=f"Game Thread"
            )
            print("Game Thread Created")
        except Exception as e:
            print(f"Failed to create thread: {e}")


        # Inform players the game has started
        # self.ping_players()
        
        """Game loop"""
        while self.game_active:
            self.take_turn()
            self.advance_turn()
        return False #TODO: return game result data

    async def ping_players(self):
        mentions = []

        for player in self.players:
            mentions.append(player.user_id)

        mention_text = " ".join(mentions)

        await self.game_thread.send(mention_text)

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
        """Return the current turn order as a list of player ids."""
        return [p.user_id for p in self.turn_order]
    
    def take_turn(self):
        """Current player takes their turn."""
        # current player chooses their action from roleActions + globalActions
        # if action requires target, choose target from players in turn order (alive players excl. self)
            # Option 1: IF action is a roleAction, players can challenge
                # 1a. If challenge occurs, resolve challenge
                # 1b. If no challenge, action can be blocked by target if applicable, resolve block
            # Option 2: globalAction
                # 2a. if action can be blocked, resolve block logic
            # Losing influence, exchanging cards, etc. logic handled in respective methods
        # return

    def block_action(self, action, actor):
        """Handles giving other players the option to block an action."""

    
    def challenge_action(self, action, actor):
        """Handles giving other players the option to challenge an action."""

    def end_game(self):
        """Ends the current game."""
        self.game_active = False
    