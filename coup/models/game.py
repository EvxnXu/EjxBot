from collections import deque
import random
from .player import Player
from .deck import Deck


class Game:
    """Model representing the state of an ongoing game.

    Args:
        players: dict mapping user_id -> user_name (same shape as Lobby.players)
    """
    def __init__(self, players: dict):
        # Create Player objects from the input mapping
        # players is expected to be a dict: {user_id: user_name}
        self.players = [Player(user_id, user_name) for user_id, user_name in players.items()]

        # Deck for drawing cards
        self.deck = Deck()
        self.dead_players = []

        # Randomize turn order using random.sample and store in a deque for efficient rotation
        if self.players:
            randomized = random.sample(self.players, k=len(self.players))
            self.turn_order = deque(randomized)
            self.current_player = self.turn_order[0]
        else:
            raise ValueError("Game has no players.")

    def init_game(self):
        """Initializes the game by shuffling the deck (if supported) and dealing cards to players.

        After dealing, the current player is set from the randomized turn_order.
        """
        # If Deck exposes a shuffle method, call it. Otherwise assume Deck.draw() is random.
        if hasattr(self.deck, "shuffle"):
            try:
                self.deck.shuffle()
            except Exception:
                pass

        # Deal 2 cards to each player
        for player in self.players:
            player.add_influence(self.deck.draw())
            player.add_influence(self.deck.draw())

        # Ensure current_player is set
        if self.turn_order:
            self.current_player = self.turn_order[0]

    def advance_turn(self):
        """Advance to the next player's turn.

        Rotates the deque so the leftmost player moves to the end and updates current_player.
        """
        if not self.turn_order:
            self.end_game()
            return
        self.turn_order.append(self.current_player)
        self.current_player = self.turn_order.popleft()

    def get_turn_order_ids(self):
        """Return the current turn order as a list of player ids."""
        return [p.user_id for p in self.turn_order]