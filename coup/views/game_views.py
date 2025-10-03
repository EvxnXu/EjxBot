import discord
from discord.ui import Select, Button, View
from coup.models.action import Action

def create_action_view(game):
    options = [discord.SelectOption(label=a, value=a) for a in Action.turnActions]
    select = Select(placeholder="Choose your action...", options=options, min_values=1, max_values=1)

    async def callback(interaction: discord.Interaction):
        user = interaction.user
        if user.id != game.current_player.user_id:
            await interaction.response.send_message("It is not your turn!", ephemeral=True)
            return
        
        action = select.values[0]
        game.action_state.action = action
        select.disabled = True
        await game.send_update_msg(f"{user.name} chose {game.action_state.action}!")
        await interaction.response.defer()

        # if action has a no response or target(income), call function directly
        if action == "income":
            await game.take_income()
        # if action has a target , call target creation
        # if action has a no target, but a response, call response

    select.callback = callback
    view = View(timeout=None)
    view.add_item(select)
    print("action buttons created!")
    return view

def create_target_view(game, force_coup=False):
    targets = [p for p in game.players if p.user_id != game.current_player.user_id]
    options = [discord.SelectOption(label=p.user_name, value=str(p.user_id)) for p in targets]
    select = Select(placeholder="Choose a target...", options=options, min_values=1, max_values=1)

    async def callback(interaction: discord.Interaction):
        user = interaction.user
        if user.id != game.current_player.user_id:
            await interaction.response.send_message("It is not your turn!", ephemeral=True)
            return

        selected_id = int(select.values[0])
        game.action_state.target_id = selected_id
        action_name = "coup" if force_coup else game.action_state.action
        await game.send_update_msg(f"{user.name} is attempting {action_name} on <@{selected_id}>!")
        await interaction.response.defer()

    select.callback = callback
    view = View(timeout=None)
    view.add_item(select)
    return view

def create_block_view(game):
    view = View(timeout=None)
    action = game.action_state.action
    actor_id = game.current_player.user_id

    if action == "steal":
        view.add_item(captain_block_bt(game, actor_id))
        view.add_item(ambassador_block_bt(game, actor_id))
    elif action == "foreign_aid":
        view.add_item(duke_block_bt(game, actor_id))
    elif action == "assassinate":
        target_id = getattr(game.action_state, "target_id", None)
        if target_id:
            view.add_item(ambassador_block_bt(game, target_id))

    if action in Action.roleActions:
        view.add_item(challenge_bt(game, actor_id))

    return view

# -----------------------
# Block Buttons
# -----------------------
def captain_block_bt(game, actor_id: int):
    button = Button(label="Block as Captain", style=discord.ButtonStyle.primary)

    async def callback(interaction: discord.Interaction):
        user = interaction.user
        if user.id not in game.get_turn_order_ids() or user.id == actor_id:
            await interaction.response.send_message("You cannot block!", ephemeral=True)
            return
        game.action_state.blocked = True
        game.action_state.blocker = user.id
        await game.send_update_msg(f"{user.name} blocked the action as Captain!")
        await interaction.response.defer()

    button.callback = callback
    return button

def ambassador_block_bt(game, actor_id: int):
    button = Button(label="Block as Ambassador", style=discord.ButtonStyle.secondary)

    async def callback(interaction: discord.Interaction):
        user = interaction.user
        if user.id not in game.get_turn_order_ids() or user.id == actor_id:
            await interaction.response.send_message("You cannot block!", ephemeral=True)
            return
        game.action_state.blocked = True
        game.action_state.blocker = user.id
        await game.send_update_msg(f"{user.name} blocked the action as Ambassador!")
        await interaction.response.defer()

    button.callback = callback
    return button

def duke_block_bt(game, actor_id: int):
    button = Button(label="Block as Duke", style=discord.ButtonStyle.danger)

    async def callback(interaction: discord.Interaction):
        user = interaction.user
        if user.id not in game.get_turn_order_ids() or user.id == actor_id:
            await interaction.response.send_message("You cannot block!", ephemeral=True)
            return
        game.action_state.blocked = True
        game.action_state.blocker = user.id
        await game.send_update_msg(f"{user.name} blocked the action as Duke!")
        await interaction.response.defer()

    button.callback = callback
    return button

# -----------------------
# Challenge Button
# -----------------------
def challenge_bt(game, actor_id: int):
    button = Button(label="Challenge", style=discord.ButtonStyle.secondary)

    async def callback(interaction: discord.Interaction):
        user = interaction.user
        if user.id not in game.get_turn_order_ids() or user.id == actor_id:
            await interaction.response.send_message("You cannot challenge!", ephemeral=True)
            return
        game.action_state.challenged = True
        game.action_state.challenger = user.id
        await game.send_update_msg(f"{user.name} has challenged the action!")
        await interaction.response.defer()

    button.callback = callback
    return button

# -----------------------
# Action Embed
# -----------------------
def create_action_embed(game):
    current_player = game.current_player
    embed = discord.Embed(
        title="Coup Game",
        description=f"It is {current_player.user_name}'s turn."
    )
    print("action embed created!")
    return embed
