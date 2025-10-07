# player.py
from typing import Optional
import logging

logger = logging.getLogger("coup")

class Player():
    """Class represnting a player's state in the game."""
    def __init__(self, user_id: int, user_name: str):
        logger.info(f"Created Player Object with UID: {user_id} and user_name: {user_name}")
        self.user_id = user_id
        self.user_name = user_name
        self.coins = 2
        self.hand = []
    
    def is_alive(self) -> bool:
        if len(self.hand) == 0:
            return False
        return True
    
    def check_role(self, role: str) -> bool:
        """Checks if Player has the passed role."""
        if role in self.hand:
            return True
        return False

    def lose_influence(self, card: Optional[str]) -> str:
        """Handles the player losing an influence (card)"""
        logger.info(f"Player {self.user_id} is losing an influence. Specified: {card}")
        if len(self.hand) == 2:
            if card in self.hand:
                return self.hand.remove(card)
            else:
                print("Player has 2 cards, needs to choose one to lose.")
                # TODO: Implement logic for providing the user a message + view with buttons to choose card
        elif len(self.hand) == 1:
            return self.hand.pop()
        else:
            logger.error(f"Player {self.user_id} is already dead, cannot lose influence.")
    
    def gain_influence(self, card: str):
        """Adds a card to the player's hand (user exchanges or challenge win)"""
        logger.info(f"Player {self.user_id} is gaining influence: {card}")
        if len(self.hand) >= 2:
            logger.error(f"Player {self.user_id} cannot have more than 2 influence.")
        self.is_alive = True # in case player was at 0 cards before gaining influence
        self.hand.append(card)
        
    def gain_income(self, amount: int):
        """Increase player's coins by the specified amount"""
        self.coins += amount
        logger.info(f"Player {self.user_id} gained {amount} coins. Now owns {self.coins} coins.")
    
    def spend_coins(self, amount: int):
        """Decrease player's coins by the specified amount"""
        if amount > self.coins:
            logger.error("Not enough coins to take this action.")
        self.coins -= amount
        logger.info(f"Player {self.user_id} spent {amount} coins. Now owns {self.coins} coins.")

    