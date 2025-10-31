# tests/test_player.py
import pytest
from coup.models import Player

class TestPlayer:
    def test_player_init(self):
        player = Player(123, 'Wumpus')
        assert player.id == 123
        assert player.name == 'Wumpus'
        assert player.coins == 2
        assert len(player.hand) == 0

    def test_gain_influence(self):
        player = Player(123, 'Wumpus')
        player.gain_influence('Duke')
        assert player.num_influence() == 1
        player.gain_influence('Inquisitor')
        assert player.num_influence() == 2
        assert player.check_role('Duke')
        assert player.check_role('Inquisitor')

    def test_lose_influence(self):
        player = Player(123, 'Wumpus')
        player.gain_influence('Duke')
        player.gain_influence('Captain')

        assert player.lose_influence('Duke') == 'Duke'
        assert player.num_influence() == 1
        assert player.check_role('Captain')
        assert player.lose_influence() == 'Captain'
    
    def test_overspend_coins(self):
        player = Player(123, 'Wumpus')
        
        assert not player.spend_coins(3)
        assert player.coins == 2

    def test_gain_income(self):
        player = Player(123, 'Wumpus')

        player.gain_income(3)
        assert player.coins == 5

    def test_lose_income(self):
        player = Player(123, 'Wumpus')

        player.lose_coins(1)
        assert player.coins == 1
        assert player.lose_coins(10) == 1
        assert player.coins == 0
    
    def test_is_alive(self):
        player = Player(123, 'Wumpus')

        assert not player.is_alive()
        player.gain_influence("Duke")
        assert player.is_alive()
        player.lose_influence()
        assert not player.is_alive()

