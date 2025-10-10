# game.py
import asyncio
import random
import discord
import logging
from collections import deque
from coup.models import Player, Deck, Action, Coup
from coup.views import (
    create_action_view, create_action_embed,
    create_target_view, create_target_embed,
    create_response_view, create_response_embed, update_response_timer,
    create_prompt_view, create_prompt_embed,
    create_hand_view, create_hand_embed
    )

logger = logging.getLogger("coup")

class Game:
    """Model representing the state of an ongoing game."""
    def __init__(self, players: dict):
        # Create Player objects from the input mapping
        self.players = [Player(user_id, user_name) for user_id, user_name in players.items()]
        self.dead: list[Player] = []
        # Create Deck
        self.deck = Deck()
        # Game Metadata
        self.game_active = True
        self.game_thread: discord.Thread | None = None
        self.prev_msg: discord.Message | None = None
        self.hand_msg: discord.Message | None = None
        # Turn Data
        self.turn_order = deque()
        self.current_player: Player | None = None
        self.current_action: Action | None = None
        self.turn_completed = asyncio.Event() # To check for turn finish before advancing turn order

        # Deal 2 cards to each player
        for player in self.players:
            player.gain_influence(self.deck.draw())
            player.gain_influence(self.deck.draw())

        

        # Randomize turn order
        randomized = random.sample(self.players, k=len(self.players))
        self.turn_order = deque(randomized)
        self.current_player = self.turn_order.popleft()
        # Log Game Init
        logger.info(f"Initialized Game: {self}")

    def __repr__(self):
        return (
            f"<Game current_player={self.current_player} "
            f"turn_info={self.current_action} "
            f"turn_order={self.get_turn_order_ids()} deck={self.deck}>"
        )
        
    # -----------------------
    # Game Flow
    # -----------------------

    async def game_loop(self, msg: discord.Message):
        """Main game loop."""
        # Create Game Thread
        try:
            self.game_thread = await msg.create_thread(name="Game Thread", auto_archive_duration=1440)
        except Exception as e:
            logger.error(f"Failed to create thread: {e}")
            return # Do not continue if game thread doesn't exist

        # Start Sending Hand Message
        try:
            asyncio.create_task(self.start_hand_loop())
        except Exception as e:
            logger.error(f"Failed to start hand loop: {e}")
            return

        await self.ping_players()

        while self.game_active:
            await self.take_turn()

            # Wait until Active Player Finishes Taking Turn
            await self.turn_completed.wait()
            self.turn_completed.clear()

            logger.info(f"Game Turn Complete")
            self.current_action = None

            await self.advance_turn()

        #TODO: return some result TBD
    
    async def take_turn(self):
        """Handle current player's turn."""
        logger.info(f"Starting turn for {self.current_player}")

        # Must coup if coins >= 10
        if self.current_player.coins >= 10:
            self.current_action = Coup(self.current_player)
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
        if self.current_player and self.current_player.is_alive():
            self.turn_order.append(self.current_player)
        # New active player is the front of the turn order.
        self.current_player = self.turn_order.popleft()
    
    async def end_turn(self):
        logger.info(f"Ending turn for {self.current_player}")
        self.turn_completed.set()

    async def end_game(self):
        logger.info("Ending Game")
        self.game_active = False
    
    # -----------------------
    # Utility Functions
    # -----------------------

    def get_player_ids(self):
        """Return list of player IDs in game"""
        return [p.user_id for p in self.players]

    def get_turn_order_ids(self):
        """Return list of player IDs in turn order  ."""
        return [p.user_id for p in self.turn_order]
    
    def get_player_by_id(self, user_id: int) -> Player:
        """Returns Player Object given a user_id"""
        for player in self.players:
            if player.user_id == user_id:
                return player
        logger.error(f"Player with id {user_id} not found in list of living players")
        return None
    
    async def ping_players(self):
        """Ping all players at start of game to invite them to game thread."""
        mentions = " ".join([f"<@{p.user_id}>" for p in self.players])
        await self.game_thread.send(mentions + " The game has begun!")

    # -----------------------
    # Message Handling
    # -----------------------

    async def send_hand_msg(self):
        if self.hand_msg:
            try:
                await self.hand_msg.delete()
            except:
                logger.error("Could not delete the previous hand_msg")
        
        self.hand_msg = await self.game_thread.send(
            embed=create_hand_embed(),
            view=create_hand_view(self)
        )

    async def start_hand_loop(self):
        while self.game_active:
            await self.send_hand_msg()
            await asyncio.sleep(30)
    
    async def send_update_msg(self, content: str):
        """Delete previous interactable message and send a log message in thread."""
        if self.prev_msg:
            try:
                await self.prev_msg.delete()
            except:
                logger.error("Previous Message Not Found")
                pass
        self.prev_msg = None
        embed = discord.Embed(
            description = content
        )
        await self.game_thread.send(embed=embed)

        logger.info(f"Update Message Sent: {content}")

    async def send_interact_msg(self, view: discord.ui.View, embed: discord.Embed, response_msg: bool):
        """Send a message with an interactive view."""
        if self.prev_msg:
            try:
                await self.prev_msg.delete()
            except:
                logger.error("Previous Message Not Found")
                pass
        msg = await self.game_thread.send(view=view, embed=embed)
        self.prev_msg = msg

        logger.info(f"Interactable Message Sent")

        # Countdown updates for non-update messages
        if response_msg:
            timeout = 10 # time to respond
            asyncio.create_task(update_response_timer(self, msg, embed, timeout))

    async def send_action_message(self):
        """Send dropdown for player action selection."""
        logger.info("Creating Action Message.")
        view = create_action_view(self)
        logger.info("Action View Created.")
        embed = create_action_embed(self)
        logger.info("Action Embed Created.")
        await self.send_interact_msg(
            view=view,
            embed=embed,
            response_msg=False
        )
    
    async def send_response_message(self):
        """Create message with buttons to respond to an action"""
        logger.info("Creating Response Message.")
        view = create_response_view(self)
        logger.info("Response View Created.")
        embed = create_response_embed(self)
        logger.info("Response Embed Created.")

        await self.send_interact_msg(
            view=view,
            embed=embed,
            response_msg=True
        )

    async def send_target_message(self, force_coup=False):
        """Send dropdown for target selection."""
        logger.info("Creating Target Message.")
        view = create_target_view(self, force_coup=force_coup)
        logger.info("Target View Created.")
        embed = create_target_embed(self)
        logger.info("Target Embed Created.")

        await self.send_interact_msg(
            view=view,
            embed=embed,
            response_msg=False
        )

    # -----------------------
    # Turn Flow
    # -----------------------

    async def handle_challenge(self):
        """Handle Who wins the Challenge."""
        action = self.current_action
        actor = action.actor
        blocker = action.blocker
        challenger = action.challenger
        
        logger.info(f"Handling Challenge: challenger={challenger}")
        
        # Case: Challenge is made on blocker
        if action.blocked == True:
            logger.info(f"Defending Challenge: blocker={blocker}")
            # If blocker does not have role they are blocking with
            if not blocker.check_role(action.blocking_role):
                logger.info("Defending Player does not have role.")
                # Blocker loses influence, return to revealed pile
                await self.handle_lose_influence(blocker)
                # Check if Blocker is Alive
                await self.check_alive(blocker)
                # Carry out action (Block Failed)
                await action.execute(self)
            # If blocker has role
            else:
                logger.info("Defending Player has role.")
                # Challenger Loses Influence
                await self.handle_lose_influence(challenger)
                # Blocker Exchanges Challenged Role
                await self.handle_lose_influence(blocker, True)
                blocker.gain_influence(self.deck.draw())
                # Check if Challenger is Alive
                await self.check_alive(challenger)
                # Action is Blocked
                await action.on_block(self)
        # Case: Challenge is made on actor
        else:
            logger.info(f"Defending Challenge: actor={self.current_player}")
            acting_role = action.role
            # If actor does not have role they are blocking with
            if not actor.check_role(acting_role):
                logger.info("Defending Player does not have role.")
                # Actor Loses Influence
                await self.handle_lose_influence(actor)
                # Check if Actor is Alive
                await self.check_alive(actor)
                # Action is Blocked
                action.on_block()
            # If actor has role
            else:
                logger.info("Defending Player has role.")
                # Challenger Loses Influence
                await self.handle_lose_influence(challenger)
                # Actor Exchanges Challenged Role
                await self.handle_lose_influence(actor, True)
                actor.gain_influence(self.deck.draw())
                # Check if Challenger is Alive
                await self.check_alive(challenger)
                # Carry out Action
                await action.execute()

    async def action_selected(self, action: Action):
        """Handle the logic following an action being selected"""
        self.current_action = action(self.current_player)
        # Check if can afford the action. If not, prompt new selection.
        if not self.current_action.is_valid():
            await self.send_update_msg("Not enough coins to carry out that action. Choose again.")
            self.current_action = None
            await self.send_action_message()
            return
        
        if self.current_action.has_target():
            await self.send_target_message()
        elif self.current_action.can_respond():
            await self.send_response_message()
        else:
            await self.current_action.execute(self)
        
    async def target_selected(self):
        """Handle the logic after target is selected"""
        if self.current_action.can_respond():
            await self.send_response_message()
        else:
            await self.current_action.execute(self)

    async def no_response(self):
        """Handle no response to an action or block"""
        if self.current_action.blocked:
            await self.current_action.on_block(self)
        else:
            await self.current_action.execute(self)

    async def check_alive(self, player: Player):
        """Handle Player Death if Player Loses Influence"""
        if not player.is_alive():
            # Remove the dead player form the turn order
            if player == self.current_player:
                self.current_player = None
            else:
                self.turn_order.remove(player)
            # Move from players to dead
            self.players.remove(player)
            self.dead.append(player)
        return
    
    async def handle_lose_influence(self, player: Player, exchange: bool = False):
        """Handle Logic for Player Losing Influence."""
        logger.info(f"Handling {player} losing influence")
        card_choice = None
        # Obtain the Card Player is Losing
        if player.num_influence() >= 2:
            logger.info(f"Player has {player.num_influence()} cards. Must Choose one.")
            # Must allow player to choose which to lose.
            future = asyncio.get_event_loop().create_future()
            msg = await self.game_thread.send(
                view = create_prompt_view(target=player, future=future),
                embed = create_prompt_embed(target=player))
            card_choice = await future
            await msg.delete()
            return player.lose_influence(card_choice)
        else:
            # No need to get card choice
            card_choice = player.lose_influence()
        # Return Card to Deck
        if exchange:
            # Return to Deck, do not tell players the card's identity
            self.deck.return_deck(card_choice)
        else:
            # Return to Revealed Pile, send update message with card's identity
            self.deck.return_revealed(card_choice)
            await self.send_update_msg(
                f"{player.user_name} has lost influence: {card_choice}"
            )
