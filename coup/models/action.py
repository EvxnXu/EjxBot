# action.py
from abc import ABC
from typing import Optional
from .player import Player
import logging

logger = logging.getLogger("coup")

class Action(ABC):
    """Base class for all game actions"""
    name: str = "base"

    def __init__(self, actor: Player, target: Optional[Player] = None):
        self.actor = actor
        self.target = target
        self.blocker: Optional[Player]
        self.challenger: Optional[Player]
        self.blocked = False
        self.challenged = False

    async def execute(self, game):
        logger.error("Base Class Method Called")
        
    async def on_block(self, game, blocker):
        pass

class Income(Action):
    name = "income"
    async def execute(self, game):
        self.actor.gain_income(1)
        await game.send_update_msg(
            content=f"{self.actor.user_name} gained 1 coin. They now have {self.actor.coins} coin(s)."
        )
        await game.end_turn()

class Foreign_Aid(Action):
    name = "foreign_aid"
    async def execute(self, game):
        self.actor.gain_income(2)
        await game.send_update_msg(
            content=f"{self.actor.user_name} gained 2 coins. They now have {self.actor.coins} coin(s)."
        )
        await game.end_turn()

class Tax(Action):
    name = "tax"
    async def execute(self, game):
        self.actor.gain_income(3)
        await game.send_update_msg(
            content=f"{self.actor.user_name} gained 3 coins. They now have {self.actor.coins} coin(s)."
        )
        await game.end_turn()

class Coup(Action):
    name = "coup"
    async def execute(self, game):
        """COUP MUST BE AFFORDABLE. HANDLE IN ACTION_VIEW"""
        game.deck.return_revealed(self.target.lose_influence()) # Target Loses Influence
        self.actor.spend_coins(7) # Actor spends 7 coins
        await game.end_turn()

class Exchange(Action):
    name = "exchange"
    async def execute(self, game):
        game.deck.return_deck(self.actor.lose_influence()) # Lose actor's choice of influence
        self.actor.gain_influence(game.deck.draw()) # Draw a new role card

class Assasinate(Action):
    name = "assassinate"
    async def execute(self, game):
        game.deck.return_revealed(self.target.lose_influence()) # Target Loses Influence
        self.actor.spend_coins(3) # Actor spends 3 coins
        await game.end_turn()

class Steal(Action):
    name = "steal"
    async def execute(self, game):
        self.target.lose_coins(2) # Target loses 2 coins
        self.actor.gain_income(2) # Actor gains 2 coins
        await game.end_turn()




        