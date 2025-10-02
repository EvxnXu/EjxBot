# game_views.py
from discord.ui import Button, View
import discord

def create_action_view():
    """
    Create the action view with buttons for diffferent actions.
    """

    view = View(timeout=None)

    view.add_item(income_bt())
    view.add_item(foreign_aid_bt())
    view.add_item(coup_bt())
    view.add_item(tax_bt())
    view.add_item(assassinate_bt())
    view.add_item(exchange_bt())
    view.add_item(steal_bt())

    return view

def create_action_embed():
    """
    Create the action embed showing relevant game information.
    """
    embed = discord.Embed(
        title = "todo",
        description = "todo",
        # TODO: add relevant game info (player turn, coins, etc.)
    )

    return embed

def create_block_view(action, actor):
    """
    Create the block view with buttons to block using different roles.
    This view is shown to all 
    """
    view = View(timeout=None)

    if action == "steal":
        view.add_item(captain_block_bt())
        view.add_item(ambassador_block_bt())
    elif action == "foreign_aid_bt":
        view.add_item(duke_block_bt())
    elif action == "assassinate":
        view.add_item(ambessa_block_bt())
    else:
        raise ValueError("Action is not blockable")
    
    return view

# Buttons for different actions

def income_bt():
    return
def foreign_aid_bt():
    return
def coup_bt():
    return
def tax_bt():
    return
def assassinate_bt():
    return
def exchange_bt():
    return
def steal_bt():
    return
def captain_block_bt():
    """Create the Captain Block Button to block steal action.
    Any active player that is not the actor can interact with this button.
    """
    return
def ambassador_block_bt():
    """Create the Ambassador Block Button to block steal action.
    Any active player that is not the actor can interact with this button.
    """
    return
def duke_block_bt():
    """Create the Duke Block Button to block foreign aid action.
    Any active player that is not the actor can interact with this button.
    """
    return
def ambessa_block_bt():
    """Create the Ambessa Block Button to block assassinate action.
    Only the target player can interact with this button.
    """
    return
