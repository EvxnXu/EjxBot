import random as random
import logging

logger = logging.getLogger("coup")

cards = ["Duke", "Assassin", "Ambassador", "Captain", "Contessa", "Inquisitor"]

class Deck():
    """Model represeting the coup deck"""
    def __init__(self):
        self.cards = ["Duke"] * 3 + ["Assassin"] * 3 + ["Ambassador"] * 3 + ["Captain"] * 3 + ["Contessa"] * 3
        self.shuffle()
        self.burned = self.cards.pop() # burn a card at the start of the game
        self.revealed = [] # list of revealed role cards
        logger.info(f"Iniitalized Deck: {self}")
    
    def __repr___(self):
        return f"<deck={self.cards} burned={self.burned} revealed={self.revealed}>"

    def shuffle(self):
        """Shuffle the Deck"""
        random.shuffle(self.cards)
    
    def draw(self):
        """Draw a card from the deck"""
        if not self.cards:
            logger.error(f"{self} has no cards left in the deck; a card cannot be drawn")
        drawn = self.cards.pop()
        logger.info(f"{self} has had {drawn} drawn from its deck")
        return drawn
    
    def return_deck(self, card: str):
        """Return a card to the deck for challenge or exchange"""
        self.cards.append(card)
        logger.info(f"{self} has had {card} returned to its deck")
        random.shuffle(self.cards)
    
    def return_revealed(self, card: str):
        """Return a card to the revealed list as a result of lost influence"""
        self.revealed.append(card)
        logger.info(f"{self} has had {card} added to the revealed pile")

    def show_revealed(self):
        """Show revealed cards for player reference"""
        return self.revealed

    def deck_size(self):
        """Returns the number of cards left in the deck"""""
        return len(self.cards)

