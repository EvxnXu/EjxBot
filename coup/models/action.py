class Action():
    """Base class for all actions in the game."""
    roleActions = ["Tax", "Assassinate", "Excahange", "Steal"]
    globalActions = ["Income", "Foreign Aid", "Coup"]
    responseActions = ["Block Foreign Aid", "Block Steal", "Block Assassination"]
    challengeActions = ["Challenge"]
    allActions = roleActions + globalActions + responseActions + challengeActions
        