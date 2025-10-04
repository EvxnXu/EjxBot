# coup/models/action.py
class Action:
    turnActions = ["income", "foreign_aid", "coup", "tax", "steal", "assassinate", "exchange"]
    roleActions = ["tax", "steal", "assassinate", "exchange"]
    roleDict = {"tax": "Duke", 
                "steal": "Captain",
                "assassinate": "Assassin",
                "exchange": "Ambassador",
                }
    
    def __init__(self):
        self.action = None # Current Action
        # Info Regarding an Action being blocked
        self.blocked = False
        self.blocker_id = None
        self.blocker_name = None
        self.blocking_role = None
        # Info Regarding a role action being challenged
        self.challenged = False
        self.challenger_id = None
        self.challenger_name = None
        # Info Regarding Action Target
        self.target_id = None
        self.target_name = None

    def getRole(self, action):
        """Takes an action and returns the associated role"""
        return self.roleDict[action]