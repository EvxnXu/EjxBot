import random as random

class Deck():
    """Model represeting the coup deck"""
    def __init__(self):
        self.cards = ["Duke"] * 3 + ["Assassin"] * 3 + ["Ambassador"] * 3 + ["Captain"] * 3 + ["Contessa"] * 3
        self.shuffle()
        self.burned = self.cards.pop() # burn a card at the start of the game
        self.revealed = [] # list of revealed role cards

    def shuffle(self):
        random.shuffle(self.cards)
    
    def draw(self):
        """Draw a card from the deck"""
        if not self.cards:
            raise ValueError("No cards left in the deck.")
        return self.cards.pop()
    
    def return_card(self, card):
        """Return a card to the deck for challenge or exchange"""
        self.cards.append(card)
        random.shuffle(self.cards)

    def show_revealed(self):
        """Show revealed cards for player reference"""
        return self.revealed

    def deck_size(self):
        """Returns the number of cards left in the deck"""""
        return len(self.cards)

