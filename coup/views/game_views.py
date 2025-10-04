import discord
from discord.ui import Select, Button, View
from coup.models.action import Action

# -----------------------
# Views
# -----------------------

def create_action_view(game):
    """Create a view object for a message allowing Player to choose their action for the turn"""
    options = [discord.SelectOption(label=a, value=a) for a in Action.turnActions]
    select = Select(placeholder="Choose your action...", options=options, min_values=1, max_values=1)

    async def callback(interaction: discord.Interaction):
        user = interaction.user
        if user.id != game.current_player.user_id:
            await interaction.response.send_message("It is not your turn!", ephemeral=True)
            return
        
        action = select.values[0]
        game.turn_info.action = action
        select.disabled = True
        await game.send_update_msg(f"{user.name} chose {game.turn_info.action}!")
        await interaction.response.defer()

        # if action has a no response or target(income), call function directly
        if action == "income":
            await game.take_income()
        # if action has a target , call target creation
        # if action has a no target, but a response, call response
        elif action in ["foreign_aid", "tax", "exchange"]:
            await game.create_response_message()


    select.callback = callback
    view = View(timeout=None)
    view.add_item(select)
    return view

def create_target_view(game, force_coup=False):
    """Create dropdown select for a targeted action."""
    targets = [p for p in game.players if p.user_id != game.current_player.user_id]
    options = [
        discord.SelectOption(
            label=p.user_name,
            value=f"{p.user_id}:{p.user_name}"   # pack both id and name
        )
        for p in targets
    ]
    select = Select(placeholder=f"Choose a target for {game.turn_info.action}...", options=options, min_values=1, max_values=1)

    async def callback(interaction: discord.Interaction):
        user = interaction.user
        if user.id != game.current_player.user_id:
            await interaction.response.send_message("It is not your turn!", ephemeral=True)
            return

        raw_value = select.values[0]
        selected_id_str, selected_name = raw_value.split(":", 1)
        selected_id = int(selected_id_str)

        game.turn_info.target_id = selected_id
        game.turn_info.target_name = selected_name

        action_name = "forced coup" if force_coup else game.turn_info.action
        await game.send_update_msg(
            f"{user.name} is attempting {action_name} on {selected_name} (<@{selected_id}>)!"
        )

        await interaction.response.defer()

    select.callback = callback
    view = View(timeout=None)
    view.add_item(select)
    return view


def create_response_view(game):
    """Creates a view for a message responding to an action"""
    view = View(timeout=None)
    action = game.turn_info.action
    # Only add block buttons if not already blocked
    if game.turn_info.blocked == False:
        if action == "steal":
            view.add_item(captain_block_bt(game))
            view.add_item(ambassador_block_bt(game))
        elif action == "foreign_aid":
            view.add_item(duke_block_bt(game))
        elif action == "assassinate":
            view.add_item(ambessa_block_bt(game))

    if action in Action.roleActions or game.turn_info.blocked:
        view.add_item(challenge_bt(game))

    return view

# -----------------------
# Embeds
# -----------------------
def create_action_embed(game):
    embed = discord.Embed(
        title=f"It is {game.current_player.user_name}'s turn.",
        description="Please choose a universal action or role action for your turn"
    )
    print("Action Embed Successfully Created!")
    return embed

def create_response_embed(game):
    # Build title depending on whether the action has a target and a response is occuring
    if game.turn_info.blocked:
        title = f"{game.turn_info.blocker_name} is attempting to block {game.current_player.user_name} from {game.turn_info.action}"
    elif game.turn_info.target_name:
        title = f"{game.current_player.user_name} is attempting to {game.turn_info.action} targeting {game.turn_info.target_name}"
    else:
        title = f"{game.current_player.user_name} is attempting to {game.turn_info.action}"
    # TODO: Clean up the title
    embed = discord.Embed(
        title=title,
        description="If you would like to respond to this action, choose a response."
    )
    print("Response Embed Successfully Created!")
    return embed


# -----------------------
# Role Block Buttons
# -----------------------
def captain_block_bt(game):
    button = Button(label="Block as Captain", style=discord.ButtonStyle.primary)

    async def callback(interaction: discord.Interaction):
        user = interaction.user
        if user.id not in game.get_turn_order_ids() or user.id == game.current_player.user_id:
            await interaction.response.send_message("You cannot block!", ephemeral=True)
            return
        # Update Game's Action State
        game.turn_info.blocked = True
        game.turn_info.blocker_id = user.id
        game.turn_info.blocker_name = user.name
        game.turn_info.blocking_role = "Ambassador"
        # Send Update Message Logging Block
        await game.send_update_msg(f"{user.name} blocked the action as Captain!")
        await interaction.response.defer()
        # Allow Challenge Chance against Block
        await game.create_response_message()

    button.callback = callback
    return button

def ambassador_block_bt(game):
    button = Button(label="Block as Ambassador", style=discord.ButtonStyle.secondary)

    async def callback(interaction: discord.Interaction):
        user = interaction.user
        if user.id not in game.get_turn_order_ids() or user.id == game.current_player.user_id:
            await interaction.response.send_message("You cannot block!", ephemeral=True)
            return
        # Update Game's Action State
        game.turn_info.blocked = True
        game.turn_info.blocker_id = user.id
        game.turn_info.blocker_name = user.name
        game.turn_info.blocking_role = "Ambassador"
        # Send Update Message Logging Block
        await game.send_update_msg(f"{user.name} blocked the action as Ambassador!")
        await interaction.response.defer()
        # Allow Challenge Chance against Block
        await game.create_response_message()

    button.callback = callback
    return button

def duke_block_bt(game):
    button = Button(label="Block as Duke", style=discord.ButtonStyle.danger)

    async def callback(interaction: discord.Interaction):
        user = interaction.user
        if user.id not in game.get_turn_order_ids() or user.id == game.current_player.user_id:
            await interaction.response.send_message("You cannot block!", ephemeral=True)
            return
        # Update Game's Action State
        game.turn_info.blocked = True
        game.turn_info.blocker_id = user.id
        game.turn_info.blocker_name = user.name
        game.turn_info.blocking_role = "Duke"
        # Send Update Message Logging Block
        await game.send_update_msg(f"{user.name} blocked the action as Duke!")
        await interaction.response.defer()
        # Allow Challenge Chance against Block
        await game.create_response_message()

    button.callback = callback
    return button

def ambessa_block_bt(game):
    button = Button(label="Block as Ambessa", )

# -----------------------
# Challenge Button
# -----------------------
def challenge_bt(game):
    button = Button(label="Challenge", style=discord.ButtonStyle.danger)

    async def callback(interaction: discord.Interaction):
        user = interaction.user
        # Check for valid user
        # Case: Challenging an Action
        if not game.turn_info.blocked:
            if user.id not in game.get_turn_order_ids() or user.id == game.current_player.user_id:
                await interaction.response.send_message("You cannot challenge!", ephemeral=True)
                return
        # Case: Challenging a Block
        else:
            if user.id == game.turn_info.blocker_id or user.id not in game.get_player_ids:
                await interaction.response.send_message("You cannot challenge!", ephemeral=True)
                return
        # Update Turn Info
        game.turn_info.challenged = True
        game.turn_info.challenger_id = user.id
        game.turn_info.challenger_name = user.name
        # Send Update Message
        if game.turn_info.blocked == False:
            await game.send_update_msg(f"{user.name} has challenged the action!")
        else:
            await game.send_update_msg(f"{user.name} has challenged the role block!")
        await interaction.response.defer()
        # Handle the Challenge
        game.handle_challenge()

    button.callback = callback
    return button

