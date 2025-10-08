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

    def __repr__(self):
        return f"<Player {self.user_name} ({self.user_id}) coins={self.coins} hand={self.hand}>"
    
    def is_alive(self) -> bool:
        """Checks if Player still has an influence card."""
        return len(self.hand) > 0
    
    def check_role(self, role: str) -> bool:
        """Checks if Player has the passed role."""
        return role in self.hand

    def lose_influence(self, card: Optional[str] = None) -> str:
        """Handles the player losing an influence (card)"""
        logger.info(f"{self} is losing influence.")
        if not self.is_alive():
            logger.error(f"{self} is already dead; cannot lose influence.")
            return None
    
        if len(self.hand) == 2:
            if card and card in self.hand:
                self.hand.remove(card)
                logger.info(f"{self} lost influence: {card}")
                return card
            else:
                print("Player has 2 cards, needs to choose one to lose.")
                return
                # TODO: Implement logic for providing the user a message + view with buttons to choose card
        elif len(self.hand) == 1:
            lost_card = self.hand.pop()
            logger.info(f"{self} lost their last influence: {lost_card}")
            return lost_card

    def gain_influence(self, card: str):
        """Adds a card to the player's hand (user exchanges or challenge win)"""
        if len(self.hand) >= 2:
            logger.error(f"{self} cannot have more than 2 influence.")
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
        