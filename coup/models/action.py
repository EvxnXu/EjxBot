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
    name = "income"

    async def execute(self, game):
        self.actor.gain_income(1)
        await game.send_update_msg(
            content=f"{self.actor.user_name} gained 1 coin. They now have {self.actor.coins} coin(s)."
        )
        await game.end_turn()

    def can_respond(self):
        return False

class Foreign_Aid(Action):
    name = "foreign_aid"

    async def execute(self, game):
        self.actor.gain_income(2)
        await game.send_update_msg(
            content=f"{self.actor.user_name} gained 2 coins. They now have {self.actor.coins} coin(s)."
        )
        await game.end_turn()
    
    def blockable(self):
        return True

class Tax(Action):
    name = "tax"
    role = "Duke"

    async def execute(self, game):
        self.actor.gain_income(3)
        await game.send_update_msg(
            content=f"{self.actor.user_name} gained 3 coins. They now have {self.actor.coins} coin(s)."
        )
        await game.end_turn()

class Coup(Action):
    name = "coup"

    async def execute(self, game):
        game.deck.return_revealed(self.target.lose_influence()) # Target Loses Influence
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
    name = "exchange"
    role = "Ambassador"

    async def execute(self, game):
        game.deck.return_deck(self.actor.lose_influence()) # Lose actor's choice of influence
        self.actor.gain_influence(game.deck.draw()) # Draw a new role card

class Assassinate(Action):
    name = "assassinate"
    role = "Assassin"

    async def execute(self, game):
        game.deck.return_revealed(self.target.lose_influence()) # Target Loses Influence
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
    name = "steal"
    role = "Captain"

    async def execute(self, game):
        self.target.lose_coins(2) # Target loses 2 coins
        self.actor.gain_income(2) # Actor gains 2 coins
        logger.info(f"{self.actor} stole 2 coins from {self.target}")
        await game.end_turn()

    def has_target(self):
        return True
    
    def blockable(self):
        return True




        