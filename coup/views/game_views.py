# game_views.py
import asyncio
import discord
import logging
from discord.ui import Select, Button, View
from coup.models import Action, Income, Foreign_Aid, Tax, Coup, Exchange, Assassinate, Steal

logger = logging.getLogger("coup")

# -----------------------
# Views
# -----------------------

def create_action_view(game):
    """Create and return a Discord UI View allowing current player to choose an action for their turn"""
    actions = [Income, Foreign_Aid, Coup, Tax, Exchange, Assassinate, Steal]
    options = [discord.SelectOption(label=a.name, value=a.name) for a in actions]
    mapping = {a.name: a for a in actions}
    select = Select(placeholder="Choose your action...", options=options, min_values=1, max_values=1)

    async def callback(interaction: discord.Interaction):
        user = interaction.user
        if user.id != game.current_player.user_id:
            await interaction.response.send_message("It is not your turn!", ephemeral=True)
            return
     
        choice = select.values[0]
        action_class: Action = mapping[choice]

        # Disable select immediately
        select.disabled = True
        await interaction.response.edit_message(view=view)

        # Send Update and Handle Action
        await game.send_update_msg(f"{user.name} chose {choice}!")
        await game.action_selected(action_class)

    select.callback = callback
    view = View(timeout=None)
    view.add_item(select)
    return view

def create_target_view(game, force_coup=False):
    """Create dropdown select for a targeted action."""
    current_player = game.current_player
    targets = [p for p in game.players if p.user_id != current_player.user_id]

    # Error Handling
    if not targets: 
        logger.error(f"{current_player} has no targets in {game}")
        return

    options = [
        discord.SelectOption(
            label=p.user_name,
            value=str(p.user_id)
        )
        for p in targets
    ]

    select = Select(
        placeholder=f"Choose a target for {game.current_action.name}...", 
        options=options, 
        min_values=1, 
        max_values=1
    )

    async def callback(interaction: discord.Interaction):
        user = interaction.user

        if user.id != game.current_player.user_id:
            await interaction.response.send_message("It is not your turn!", ephemeral=True)
            return

        target_id = int(select.values[0])
        target_player = game.get_player_by_id(target_id)

        # Disable select immediately
        select.disabled = True
        await interaction.message.edit(view=view)

        game.current_action.target = target_player

        await game.send_update_msg(
            f"{user.name} is attempting {game.current_action.name} on {target_player.user_name} (<@{target_id}>)!"
        )
        await interaction.response.defer()
        await game.target_selected()

    select.callback = callback
    view = View(timeout=None)
    view.add_item(select)
    return view

def create_response_view(game):
    """Creates a view for a message responding to an action"""
    view = View(timeout=None)
    action: Action = game.current_action

    if not action:
        logger.error("No action found.")
        return

    # Only add block buttons if not already blocked
    if action.blocked == False and action.blockable():
        logger.info("Adding Block Button to Response Message.")
        view.add_item(create_block_button(game))

    if isinstance(action, (Tax, Assassinate, Exchange, Steal)) or action.blocked:
        view.add_item(create_challenge_button(game))
        logger.info("Adding Challenge Button to Response Message.")
    
    return view

# -----------------------
# Embeds
# -----------------------

def create_action_embed(game):
    embed = discord.Embed(
        title=f"It is {game.current_player.user_name}'s turn.",
        description="Please choose an action for your turn"
    )
    return embed

def create_response_embed(game):
    # Build title depending on whether the action has a target and a response is occuring
    # TODO: Clean up the title
    embed = discord.Embed(
        description="If you would like to respond to this action, choose a response."
    )

    return embed

def create_target_embed(game):
    embed = discord.Embed(
        title=f"{game.current_player.user_id}, please choose a target for {game.current_action.name}:"
    )
    return embed

# -----------------------
# Buttons
# -----------------------

def create_block_button(game):
    """Generic Block Button"""
    button = Button(label="Block", style=discord.ButtonStyle.primary)

    async def callback(interaction: discord.Interaction):
        user = interaction.user
        action: Action = game.current_action

        # Validate that the user can block
        if user.id == action.actor.user_id or user.id not in game.get_turn_order_ids():
            await interaction.response.send_message("You cannot block!", ephemeral=True)
            return
        
        # Update Action
        action.blocking_role = None # TODO: Implement a way to choose (2 roles can block steal)
        action.blocked = True
        action.blocker = game.get_player_by_id(user.id)

        # Give chance to challenge
        await game.send_response_message()
    
    button.callback = callback
    return button

def create_challenge_button(game):
    button = Button(label="Challenge", style=discord.ButtonStyle.danger)

    async def callback(interaction: discord.Interaction):
        user = interaction.user
        action: Action = game.current_action

        if action.blocked:
            # Challenging the block
            if user.id == action.blocker.user_id or user.id not in game.get_player_ids():
                await interaction.response.send_message("You cannot challenge this block!", ephemeral=True)
                return
        else:
            # Challenging the Action
            if user.id not in game.get_turn_order_ids() or user.id == action.actor.user_id:
                await interaction.response.send_message("You cannot challenge this action!", ephemeral=True)
                return

        # Update Action object
        action.challenged = True
        action.challenger = game.get_player_by_id(user.id)

        # Send Update Message
        if game.current_action.blocked == False:
            await game.send_update_msg(f"{user.name} has challenged the action!")
        else:
            await game.send_update_msg(f"{user.name} has challenged the role block!")
        await interaction.response.defer()
        # Handle the Challenge
        await game.handle_challenge()

    button.callback = callback
    return button

# --------------
# Misc.
# --------------

async def update_response_timer(game, msg, embed, timeout):
    """Function that updates the response embed to show time left to respond"""
    print("entered update_response_timer func.")
    for remaining in range(timeout, 0, -1):
        # Edit the embed description to update countdown
        logger.info(f"{remaining} seconds left for a response.")
        embed.description = f"{remaining} seconds left to respond."

        try:
            await msg.edit(embed=embed)
        except Exception as e:
            logger.error(f"Error editing message: {e}")
            return
        
        await asyncio.sleep(1)

    # Time's Up
    await game.send_update_msg("No one responded. Proceeding...") # Should delete response message
    await game.no_response()