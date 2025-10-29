# action.py
from abc import ABC
from typing import Optional
from .player import Player
import logging

logger = logging.getLogger("coup")

class Action(ABC):
    """Base class for all game actions"""
    name: str = "base"
    role: str = "base"

    def __init__(self, actor: Player, target: Optional[Player] = None):
        self.actor = actor
        self.target = target
        self.blocker: Optional[Player] = None
        self.challenger: Optional[Player] = None
        self.blocked = False
        self.blocking_role: str = None
        self.challenged = False

    def __repr__(self):
        return (
            f"<Action={self.name} "
            f"target={self.target} " 
            f"blocked={self.blocked} " 
            f"blocker={self.blocker} " 
            f"blocking_role={self.blocking_role} "
            f"challenged={self.challenged} "
            f"challenger={self.challenger} "
        )
    async def execute(self, game):
        logger.error("Base Class Method Called")
        
    async def on_block(self, game):
        # Default Behavior: Action doesn't go through, end turn
        if self.blocked and not self.challenged:
            game.send_update_msg(
                f"{self.name} got blocked by {self.blocker.name}."
            )
        await game.end_turn()

    def is_valid(self) -> bool:
        return True

    def has_target(self) -> bool:
        return False
    
    def can_respond(self) -> bool:
        return True
    
    def blockable(self) -> bool:
        return False
    
class Income(Action):
    name = "Collect Income"

    async def execute(self, game):
        self.actor.gain_income(1)
        await game.send_update_msg(
            content=f"{self.actor.name} gained 1 coin. They now have {self.actor.coins} coin(s)."
        )
        await game.end_turn()

    def can_respond(self):
        return False

class Foreign_Aid(Action):
    name = "Collect Foreign Aid"

    async def execute(self, game):
        self.actor.gain_income(2)
        await game.send_update_msg(
            content=f"{self.actor.name} gained 2 coins. They now have {self.actor.coins} coin(s)."
        )
        await game.end_turn()
    
    def blockable(self):
        return True

class Tax(Action):
    name = "Collect Tax"
    role = "Duke"

    async def execute(self, game):
        self.actor.gain_income(3)
        await game.send_update_msg(
            content=f"{self.actor.name} gained 3 coins. They now have {self.actor.coins} coin(s)."
        )
        await game.end_turn()

class Coup(Action):
    name = "Coup"

    async def execute(self, game):
        # Target Loses Influence
        await game.handle_lose_influence(self.target)
        self.actor.spend_coins(7) # Actor spends 7 coins
        await game.end_turn()

    def is_valid(self):
        if self.actor.coins >= 7:
            return True
        return False
    
    def has_target(self):
        return True
    
    def can_respond(self):
        return False

class Exchange(Action):
    name = "Exchange Roles"
    role = "Inquisitor"

    async def execute(self, game):
        # Draw 1 card from the deck
        self.actor.gain_influence(game.deck.draw())

        # Return a Choice of Role Card to the Deck
        await game.handle_lose_influence(player=self.actor, exchange=True)
        
        await game.end_turn()

class Assassinate(Action):
    name = "Assasinate"
    role = "Assassin"

    async def execute(self, game):
        # Target Loses Influence
        await game.handle_lose_influence(self.target)
        self.actor.spend_coins(3) # Actor spends 3 coins
        await game.end_turn()

    async def on_block(self, game):
        self.actor.spend_coins(3) # Actor spends 3 coins
        await game.end_turn()

    def is_valid(self):
        if self.actor.coins >= 3:
            return True
        return False
    
    def has_target(self):
        return True
    
    def blockable(self):
        return True

class Steal(Action):
    name = "Steal"
    role = "Captain"

    async def execute(self, game):
        amount = min(2, self.target.coins)
        self.actor.gain_income(amount) # Actor gains up to 2 coins
        self.target.lose_coins(amount) # Target loses 2 coins
        logger.info(f"{self.actor} stole {amount} coins from {self.target}")
        await game.end_turn()

    def has_target(self):
        return True
    
    def blockable(self):
        return True




        