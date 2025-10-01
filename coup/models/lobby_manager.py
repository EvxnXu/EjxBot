from .lobby import Lobby

class LobbyManager:
    """Manages multiple game lobbies."""
    def __init__(self):
        self.lobbies = {} # lobby_id --> Lobby instance
        self.next_lobby_id = 1
    
    def create_lobby(self):
        lobby = Lobby(self.next_lobby_id)
        self.lobbies[self.next_lobby_id] = lobby
        self.next_lobby_id += 1
        return lobby
    
    def get_lobby(self, lobby_id: int):
        return self.lobbies.get(lobby_id)
    
    def delete_lobby(self, lobby_id: int):
        if lobby_id in self.lobbies:
            del self.lobbies[lobby_id]