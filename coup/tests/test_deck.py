# tests/test_deck.py
import pytest
from coup.models import Deck

class TestDecK:
    def test_deck_init(self):
        deck = Deck()
        assert deck.deck_size() == 14
        assert deck.burned != None
        assert len(deck.revealed) == 0

    def test_deck_draw(self):
        deck = Deck()
        card = deck.draw()
        assert card in ["Duke", "Assassin", "Ambassador", "Captain", "Contessa", "Inquisitor"]
        assert deck.deck_size() == 13

    def test_deck_return(self):
        deck = Deck()
        card = deck.draw()
        deck.return_deck(card)
        assert deck.deck_size() == 14
    
    def test_return_revealed(self):
        deck = Deck()
        card = deck.draw()
        deck.return_revealed(card)
        assert deck.show_revealed != None
        assert deck.deck_size() == 13