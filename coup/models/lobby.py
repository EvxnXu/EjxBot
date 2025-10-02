class Lobby:
    """Model representing the state of a game lobby."""
    def __init__(self, lobby_id: int):
        self.lobby_id = lobby_id
        self.players = {} # user_id -> user_name
        self.game = None # Game State Object
    
    def add_player(self, user):
        self.players[user.id] = user.name

    def remove_player(self, user):
        self.players.pop(user.id, None)
    
    def is_full(self):
        return len(self.players) >= 6

    def is_empty(self):
        return len(self.players) == 0
    
    def can_start(self):
        return len(self.players) >= 2
    
    def start_game(self):
        """Initialize game instance"""
        if not self.can_start():
            raise ValueError("Not enough players to start the game.")
        self.game = "Game Started" # TODO: Replace with actual game instance
    
    def end_game(self):
        """Ends the current game and resets the lobby"""
        self.game = None
        # TODO: Saves game data to database/logs
        self.players.clear()
