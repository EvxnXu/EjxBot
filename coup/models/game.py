import asyncio
import random
import discord
from collections import deque
from .player import Player
from .deck import Deck
from .action import Action
from coup.views import create_action_view, create_target_view, create_response_view, create_action_embed, create_response_embed, update_response_timer

class Game:
    """Model representing the state of an ongoing game."""
    def __init__(self, players: dict):
        # Create Player objects from the input mapping
        self.players = [Player(user_id, user_name) for user_id, user_name in players.items()]
        self.deck = Deck()
        self.dead_players: list[Player] = []
        self.game_active = True

        self.game_thread: discord.Thread | None = None
        self.prev_msg: discord.Message | None = None

        self.current_player = None
        self.turn_info = Action()
        self.turn_completed = asyncio.Event() # To check for turn finish before advancing turn order


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

        
    # -----------------------
    # Game Functions
    # -----------------------

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
            await self.take_turn()

            # wait until turn is complete
            await self.turn_completed.wait()
            self.turn_completed.clear()

            print("turn complete!") # debug statement
            self.turn_info = Action() # Reset Action State

            await self.advance_turn()

            #TODO: return some result TBD
    
    async def take_turn(self):
        """Handle current player's turn."""
        # Must coup if coins >= 10
        if self.current_player.coins >= 10:
            self.turn_info.action = "coup"
            await self.send_target_message(force_coup=True)
        else:
            await self.send_action_message()
    
    async def advance_turn(self):
        """Advance to the next player's turn."""
        # If no players other than current player, current player has won. End game
        if not self.turn_order:
            await self.end_game()
            return
        # If current player isn't dead, add them to the end of the turn order
        if self.current_player:
            self.turn_order.append(self.current_player)
        # New active player is the front of the turn order.
        self.current_player = self.turn_order.popleft()

    # -----------------------
    # Misc.
    # -----------------------

    async def ping_players(self):
        """Ping all players at start of game to invite them to game thread."""
        mentions = " ".join([f"<@{p.user_id}>" for p in self.players])
        await self.game_thread.send(mentions + " The game has begun!")

    def get_player_ids(self):
        """Return list of player IDs in game"""
        return [p.user_id for p in self.players]

    def get_turn_order_ids(self):
        """Return list of player IDs in turn order."""
        return [p.user_id for p in self.turn_order]
    
    # -----------------------
    # Message Handling
    # -----------------------
    
    async def send_update_msg(self, content: str):
        """Delete previous interactable message and send a log message in thread."""
        print("Printing update message: " + content) # debug statement
        if self.prev_msg:
            try:
                await self.prev_msg.delete()
            except:
                pass
        self.prev_msg = None
        embed = discord.Embed(
            description = content
        )
        await self.game_thread.send(embed=embed)

    async def send_interact_msg(self, view: discord.ui.View, embed: discord.Embed, response_msg: bool):
        """Send a message with an interactive view."""
        if self.prev_msg:
            try:
                await self.prev_msg.delete()
            except:
                pass
        msg = await self.game_thread.send(view=view, embed=embed)
        self.prev_msg = msg

        
        # Countdown updates for non-update messages
        if response_msg:
            timeout = 10 # time to respond
            asyncio.create_task(update_response_timer(self, msg, embed, timeout))

    async def send_action_message(self):
        """Send dropdown for player action selection."""
        view = create_action_view(self)
        embed = create_action_embed(self)
        await self.send_interact_msg(
            view=view,
            embed=embed,
            response_msg=False
        )
    
    async def send_response_message(self):
        """Create message with buttons to respond to an action"""
        view = create_response_view(self)
        embed = create_response_embed(self)

        await self.send_interact_msg(
            view=view,
            embed=embed,
            response_msg=True
        )

    async def send_target_message(self, force_coup=False):
        """Send dropdown for target selection."""
        view = create_target_view(self, force_coup=force_coup)
        embed = create_action_embed(self)
        await self.send_interact_msg(
            view=view,
            embed=embed,
            response_msg=False
        )
    
    # -----------------------
    # Successful Actions
    # -----------------------

    async def take_income(self):
        """Active player takes income"""
        print("Take Income")
        self.current_player.gain_income(1)
        await self.send_update_msg(
            content=f"{self.current_player.user_name} gained 1 coin, and now has {self.current_player.coins} coins."
        )
        await self.end_turn()
    
    async def collect_foreign_aid(self):
        """Active player takes foreign aid"""
        self.current_player.gain_income(2)
        await self.send_update_msg(
            content=f"{self.current_player.user_name} gained 2 coins, and now has {self.current_player.coins} coins."
        )
        await self.end_turn()
    
    async def collect_tax(self):
        """Active player collects tax"""
        self.current_player.gain_income(3)
        await self.send_update_msg(
           content=f"{self.current_player.user_name} gained 3 coins, and now has {self.current_player.coins} coins."
        )
        await self.end_turn()
    
    async def coup(self):
        """Active player coups target"""
        self.current_player.spend_coins(7)
        # Find target's Player object
        for target in self.players:
            if target.user_id == self.turn_info.target_id:
                # Target loses influence
                self.deck.return_revealed(target.lose_influence())
                
        await self.end_turn()
    
    async def check_alive(self, player: Player):
        """Hanndle Player Death if Player Loses Influence"""
        if not player.is_alive():
            # Remove the dead player form the turn order
            if player == self.current_player:
                self.current_player = None
            else:
                self.turn_order.remove(player)
            # Move from players to dead_players
            self.players.remove(player)
            self.dead_players.append(player)
        return

    # -----------------------
    # Challenge/Block Logic
    # -----------------------

    async def handle_challenge(self):
        """Handle Who wins the Challenge."""
        print("Handle Action Called!")
        action = self.turn_info.action
        # Get the blocker and challenger Player Objects
        blocker, challenger = None, None
        for player in self.players():
            if self.turn_info.blocker_id == player.id:
                blocker = player
            elif self.turn_info.challenger_id == player.id:
                challenger = player
        # Error Handling
        if not blocker or not challenger:
            raise AttributeError("Blocker or Challenger not found.")
        
        # Case: Challenge is made on blocker
        if self.turn_info.blocked == True:
            # If blocker does not have role they are blocking with
            if not blocker.check_role(self.turn_info.blocking_role):
                self.deck.return_revealed(blocker.lose_influence()) # Blocker loses influence
                self.action_successful() # Carry out the action
            # If blocker has role
            else:
                self.deck.return_revealed(challenger.lose_influence()) # Challenger loses influence
                self.deck.return_deck(blocker.lose_influence(self.turn_info.blocking_role)) # Blocker swaps associated role
                blocker.gain_influence(self.deck.draw())
                self.check_alive(challenger)

            """
            If blocker has role in hand:
                challenger loses influence
                blocker swaps associated role
                action is not carried out (end turn)
            """
        # Case: Challenge is made on actor
        else:
            role = Action.getRole[self.turn_info.action]
            """
            If actor has role in hand:
                challenger loses influence
                actor swaps associated role
                action is carried out.
            If actor does not have role in hand:
                actor loses influence
                action is not carried out (end turn)
            """

    async def handle_no_response(self):
        if self.turn_info.blocked:
            await self.blocked_action()
        else:
            await self.action_successful()

    async def blocked_action(self):
        """Handle Blocked Action Successful."""
        await self.end_turn()

    async def action_successful(self):
        """Handle successful action (no block or challenge)"""
        # TODO: call function associated with self.turn_info.action
        action = self.turn_info.action
        match action:
            case "income": 
                await self.take_income()
            case "foreign_aid":
                await self.collect_foreign_aid()
            case "coup":
                await self.coup()
            case "tax":
                await self.collect_tax()
            # TODO: Map other actions to relevant functions

    
    # -----------------------
    # State Update Functions
    # -----------------------

    async def end_turn(self):
        """Set the turn to done"""
        self.turn_completed.set()

    async def end_game(self):
        """Ends the current game."""
        self.game_active = False
    