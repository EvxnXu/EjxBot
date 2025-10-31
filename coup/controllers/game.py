# game.py
import asyncio
import random
import discord
import logging
from typing import Optional
from collections import deque
from coup.models import Player, Deck, Action, Coup
from coup.views import *

logger = logging.getLogger("coup")

class Game:
    """Model representing the state of an ongoing game."""
    def __init__(self, players: dict):
        # Create Player objects from the input mapping
        self.players = [Player(id, name) for id, name in players.items()]
        self.dead: list[Player] = []
        # Create Deck
        self.deck = Deck()
        # Game Metadata
        self.game_active = True
        self.game_thread: discord.Thread | None = None
        self.prev_msg: discord.Message | None = None
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

        await self.ping_players()

        while self.game_active:
            await self.send_turn_start_msg()
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
        return [p.id for p in self.players]

    def get_turn_order_ids(self):
        """Return list of player IDs in turn order."""
        return [p.id for p in self.turn_order]

    def get_turn_order_names(self):
        """Return list of player names in turn order."""
        return [p.name for p in self.turn_order]
    
    def get_player_by_id(self, id: int) -> Player:
        """Returns Player Object given an id"""
        for player in self.players:
            if player.id == id:
                return player
        logger.error(f"Player with id {id} not found in list of living players")
        return None
    
    async def ping_players(self):
        """Ping all players at start of game to invite them to game thread."""
        mentions = " ".join([f"<@{p.id}>" for p in self.players])
        await self.game_thread.send(mentions + " The game has begun!")

    # -----------------------
    # Message Handling
    # -----------------------

    async def send_turn_start_msg(self):
        self.hand_msg = await self.game_thread.send(
            embed=create_turn_start_embed(self),
            view=create_hand_view(self)
        )
        logger.info(f"Start of Turn Message Sent.")
    
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
                await self.send_update_msg(
                    f"{challenger.name} won the challenge against {blocker.name}; {blocker.name} does not have {action.blocking_role}."
                )
                # Blocker loses influence, return to revealed pile
                await self.handle_lose_influence(blocker)
                # Check if Blocker is Alive
                await self.check_alive(blocker)
                # Carry out action (Block Failed)
                await self.send_update_msg(
                    f"{actor.name} succesfully carries out {action.name}."
                )
                await action.execute(self)
            # If blocker has role
            else:
                logger.info("Defending Player has role.")
                await self.send_update_msg(
                    f"{challenger.name} lost the challenge against {blocker.name}; {blocker.name} had {action.blocking_role}."
                )
                # Challenger Loses Influence
                await self.handle_lose_influence(challenger)
                # Blocker Exchanges Challenged Role
                await self.handle_lose_influence(player=blocker, card=action.blocking_role, exchange=True)
                blocker.gain_influence(self.deck.draw())
                await self.send_update_msg(
                    f"{blocker.name} is exchanging {action.blocking_role} with a new card from the deck."
                )
                # Check if Challenger is Alive
                await self.check_alive(challenger)
                # Action is Blocked
                await self.send_update_msg(
                    f"{blocker.name} succesfully blocks {action.name}."
                )
                await action.on_block(self)
        # Case: Challenge is made on actor
        else:
            logger.info(f"Defending Challenge: actor={self.current_player}")
            acting_role = action.role
            # If actor does not have role they are blocking with
            if not actor.check_role(acting_role):
                logger.info("Defending Player does not have role.")
                await self.send_update_msg(
                    f"{challenger.name} won the challenge against {actor.name}; {actor.name} does not have {acting_role}."
                )
                # Actor Loses Influence
                await self.handle_lose_influence(actor)
                # Check if Actor is Alive
                await self.check_alive(actor)
                # Action is Blocked
                await self.send_update_msg(
                    f"{blocker.name} succesfully blocks {action.name}."
                )
                await action.on_block(self)
            # If actor has role
            else:
                logger.info("Defending Player has role.")
                await self.send_update_msg(
                    f"{challenger.name} lost the challenge against {actor.name}; {actor.name} had {acting_role}."
                )
                # Challenger Loses Influence
                await self.handle_lose_influence(challenger)
                # Actor Exchanges Challenged Role
                await self.handle_lose_influence(player=actor, card=acting_role, exchange=True)
                actor.gain_influence(self.deck.draw())
                await self.send_update_msg(
                    f"{actor.name} is exchanging {acting_role} with a new card from the deck."
                )
                # Check if Challenger is Alive
                await self.check_alive(challenger)
                # Carry out Action
                await self.send_update_msg(
                    f"{actor.name} succesfully carries out {action.name}."
                )
                await action.execute(self)

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
        action = self.current_action
        if action.blocked:
            await action.on_block(self)
        else:
            await action.execute(self)

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
    
    async def handle_lose_influence(self, player: Player, card: Optional[str] = None, exchange: bool = False ):
        """Handle Logic for Player Losing Influence."""
        logger.info(f"Handling {player} losing influence")
        card_choice = None
        # Obtain the Card Player is Losing
        if player.num_influence() >= 2 and not card:
            logger.info(f"Player has {player.num_influence()} cards. Must Choose one.")
            # Must allow player to choose which to lose.
            future = asyncio.get_event_loop().create_future()
            msg = await self.game_thread.send(
                view = create_prompt_view(target=player, future=future),
                embed = create_prompt_embed(target=player, mode="lose"))
            card_choice = await future
            await msg.delete()
            player.lose_influence(card_choice)
        elif player.num_influence() >= 2 and card:
            card_choice = player.lose_influence(card)
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
                f"{player.name} has lost influence: {card_choice}"
            )

    async def handle_examine(self):
        """Handle logic for Player being examined"""
        target = self.current_action.target
        actor = self.current_player

        logger.info(f"Handing {target.name} being examined by {actor.name}")

        # --- Step 1: Obtain the Role Target is Revealing ---
        if target.num_influence() == 2:
            logger.info(f"{target.name} has 2 influence, must choose one to reveal")
            future = asyncio.get_event_loop().create_future()
            msg = await self.game_thread.send(
                view = create_prompt_view(target=target, future=future),
                embed = create_prompt_embed(target=target, mode="examine")
            )
            examined = await future
            await msg.delete()

        # --- Step 2: Reveal Examined role to Inquisitor ---
        future = asyncio.get_event_loop().create_future()
        msg = await self.game_thread.send(
            view = create_swap_view(game=self, role=examined, future=future),
            embed=create_prompt_embed(target=actor, mode="swap")
        )
        swap: bool = await future

        # --- Step 2a: If Actor wants target to exchange the role ---
        if swap:
            self.send_update_msg(f"{actor.name} opted to have {target.name} exchange their role.")
            await self.handle_lose_influence(player=target, card=examined, exchange=True)
        # -- Step 2b: If Actor wants target to keep the role ---
        else:
            self.send_update_msg(f"{actor.name} opted to have {target.name} keep their role.")
        
        return
