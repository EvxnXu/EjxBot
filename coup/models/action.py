# coup/models/action.py
class Action:
    turnActions = ["income", "foreign_aid", "coup", "tax", "steal", "assassinate", "exchange"]
    roleActions = ["tax", "steal", "assassinate", "exchange"]
    
    def __init__(self):
        self.action = None
        self.blocked = False
        self.blocker = None
        self.challenged = False
        self.challenger = None
        self.target_id = None
