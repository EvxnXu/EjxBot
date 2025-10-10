# player.py
from typing import Optional
import logging

logger = logging.getLogger("coup")

class Player():
    """Class represnting a player's state in the game."""
    def __init__(self, uid: int, uname: str):
        logger.info(f"Created Player Object with UID: {uid} and name: {uname}")
        self.id = uid
        self.name = uname
        self.coins = 2
        self.hand = []

    def __repr__(self):
        return f"<Player {self.name} ({self.id}) coins={self.coins} hand={self.hand}>"
    
    def is_alive(self) -> bool:
        """Checks if Player still has an influence card."""
        return len(self.hand) > 0
    
    def check_role(self, role: str) -> bool:
        """Checks if Player has the passed role."""
        return role in self.hand
    
    def num_influence(self) -> int:
        """Checks the number of influence a player has."""
        return len(self.hand)

    def lose_influence(self, card: Optional[str] = None) -> str:
        """Handles the player losing an influence (card)"""
        logger.info(f"{self} is losing influence.")
    
        if len(self.hand) >= 2:
            if card and card in self.hand:
                self.hand.remove(card)
                logger.info(f"{self} lost influence: {card}")
                return card
            else:
                logger.error("Player has >1 influence, must be provided card to remove as argument.")
        elif len(self.hand) == 1:
            lost_card = self.hand.pop()
            logger.info(f"{self} lost their last influence: {lost_card}")
            return lost_card
        else:
            logger.error(f"{self} is already dead; Cannot lose influence.")

        return None

    def gain_influence(self, card: str):
        """Adds a card to the player's hand (user exchanges or challenge win)"""
        self.hand.append(card)
        logger.info(f"{self} gained influence: {card}")
        
    def gain_income(self, amount: int):
        """Increase player's coins by the specified amount"""
        self.coins += amount
        logger.info(f"{self} gained {amount} coin(s)")
    
    def spend_coins(self, amount: int) -> bool:
        """Decrease player's coins by the specified amount. Returns False if Player cannot afford."""
        if amount > self.coins:
            logger.error(f"{self} does not have enough coins to spend {amount}")
            return False
        self.coins -= amount
        logger.info(f"{self} spent {amount} coin(s)")
        return True
    
    def lose_coins(self, amount: int) -> int:
        """Decreases player's coins by the specified amount to 0. Returns the max amount lost."""
        lost = 0
        if amount > self.coins:
            lost = self.coins
            self.coins = 0
        else:
            lost = amount
            self.coins = self.coins - amount
        logger.info(f"{self} lost up to {amount} coin(s)")
        return lost
        