# game_views.py
import asyncio
import discord
import logging
from discord.ui import Select, Button, View
from coup.models import Action, Income, Foreign_Aid, Tax, Coup, Exchange, Assassinate, Steal

logger = logging.getLogger("coup")

# === HELPERS === 

class InteractionLock:
    """Prevents race conditions on interactions"""
    def __init__(self):
        self.processing = False

    def acquire(self):
        """Attempt to acquire lock. Returns True if acquired"""
        if self.processing:
            return False
        self.processing = True
        return True
    
    def release(self):
        """Release the lock"""
        self.processing = False
    
    def is_processing(self):
        """Check if currently processing"""
        return self.processing
    
class PlayerChoice:
    """Helper for waiting on player choices"""

# === VIEWS ===

def create_action_view(game):
    """Create and return a Discord UI View allowing current player to choose an action for their turn"""
    view = View(timeout=None)
    view.add_item(create_action_select(game, view))
    return view


def create_target_view(game, force_coup=False):
    """Create dropdown select for a targeted action."""
    view = View(timeout=None)
    view.add_item(create_target_select(game, view))
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
        view.add_item(create_block_button(game))
        logger.info("Adding Block Button to Response Message.")

    # Only add challenge button if action is blockable or action has been role blocked
    if isinstance(action, (Tax, Assassinate, Exchange, Steal)) or action.blocked:
        view.add_item(create_challenge_button(game))
        logger.info("Adding Challenge Button to Response Message.")
    
    return view


def create_prompt_view(target, future):
    """Creates a prompt button to choose influence to lose"""
    view = View(timeout=None)
    view.add_item(create_prompt_button(target, future))
    return view


def create_hand_view(game):
    """Creates a prompt allowing players to see their hand/coins"""
    view = View(timeout=None)
    view.add_item(create_hand_button(game))
    return view

# === EMBEDS ===

def create_action_embed(game):
    return discord.Embed(
        title=f"It is {game.current_player.name}'s turn.",
        description="Please choose an action for your turn."
    )


def create_response_embed(game):
    action = game.current_action
    title = ""
    if action.blocked:
        title += f"{action.blocker.name}, as {action.blocking_role}, is attempting to block "
        title += f"{action.blocker.name}, as {action.blocking_role}, is attempting to block "
    title += f"{action.actor.name} attempting to {action.name}."

    return discord.Embed(
        title=title,
        description="If you would like to respond, choose a response."
    )


def create_target_embed(game):
    return discord.Embed(
        title=f"{game.current_player.name}, Choose a target for {game.current_action.name}:"
    )


def create_prompt_embed(target, mode: str):
    descriptions = {
        "lose": f"{target.name}: Choose an influence card to lose:",
        "examine": f"{target.name}: Choose an influence card to be examined:"
    }
    description = descriptions.get(mode)

    return discord.Embed(description=description)


def create_influence_select_embed():
    return discord.Embed(
        description="Choose influence to lose:"
    )


def create_turn_start_embed(game):
    embed = discord.Embed(
        title=f"{game.current_player.name}'s Turn Has Begun!",
        description=f"{game.current_player.name} - Influence: {game.current_player.num_influence()}; Coins: {game.current_player.coins}"
    )
    values = []
    for player in game.turn_order:
        string = f"{player.name} - Influence: {player.num_influence()}; Coins: {player.coins}"
        values.append(string)
    embed.add_field(
        name="Turn Order",
        value='\n'.join(values)
    )
    embed.add_field(
        name=f"Revealed Cards",
        value=f"Cards in Deck: {game.deck.deck_size()}\n" + '\n'.join(game.deck.revealed)
    )
    return embed

# === SELECT MENUS ===

def create_action_select(game, view):
    actions = [Income, Foreign_Aid, Coup, Tax, Exchange, Assassinate, Steal]
    options = [discord.SelectOption(label=a.name, value=a.name) for a in actions]
    mapping = {a.name: a for a in actions}
    select = Select(placeholder="Choose your action...", options=options, min_values=1, max_values=1)

    lock = InteractionLock()

    async def callback(interaction: discord.Interaction):
        # Check lock
        if lock.is_processing():
            return
        
        # Validate User
        user = interaction.user
        if user.id != game.current_player.id:
            await interaction.response.send_message("It is not your turn!", ephemeral=True)
            return
        
        # Acquire lock
        if not lock.acquire():
            return
        
        # Set result
        choice = select.values[0]
        action_class: Action = mapping[choice]

        # Disable select immediately
        select.disabled = True
        await interaction.message.edit(view=view)

        # Send Update if respondable
        if action_class not in (Income, Coup):
            await game.send_update_msg(f"{game.current_player.name} is attempting to {choice}!")

        # Handle Action
        await game.action_selected(action_class)

        # Release lock
        lock.release()

    select.callback = callback
    return select


def create_target_select(game, view):
    targets = [p for p in game.players if p.id != game.current_player.id]
    options = [discord.SelectOption(label=p.name, value=str(p.id)) for p in targets]
    select = Select(placeholder=f"Choose a target for {game.current_action.name}...", options=options)

    lock = InteractionLock()

    async def callback(interaction: discord.Interaction):
        # Check lock
        if lock.is_processing():
            return
        
        # Validate User
        user = interaction.user
        if user.id != game.current_player.id:
            await interaction.response.send_message("It is not your turn!", ephemeral=True)
            return

        # Acquire lock
        if not lock.acquire():
            return
        
        # Set Result
        target_id = int(select.values[0])
        target_player = game.get_player_by_id(target_id)

        # Disable Select
        select.disabled = True
        await interaction.message.edit(view=view)

        game.current_action.target = target_player

        await game.send_update_msg(
            f"{game.get_player_by_id(user.id).name} is attempting {game.current_action.name} on {target_player.name} (<@{target_id}>)!"
        )

        await game.target_selected()

        # Release lock
        lock.release()

    select.callback = callback
    return select


def create_influence_select(player, future):
    cards = [card for card in player.hand]
    options = [discord.SelectOption(label=card, value=card) for card in cards]
    select = Select(placeholder="Choose role to lose...", options=options)

    lock = InteractionLock()

    async def callback(interaction: discord.Interaction):
        # Check lock
        if lock.is_processing():
            return
        
        # Acquire lock
        if not lock.acquire():
            return

        # Set Result
        future.set_result(select.values[0])

        # Disable Select
        select.disabled = True
        await interaction.message.edit(view=select.view)

        # Release lock
        lock.release()

    select.callback = callback
    return select


def choose_captain_inquisitor_select(player, future):
    options = [discord.SelectOption(label=card, value=card) for card in ["Captain", "Inquisitor"]]
    select = Select(placeholder="Choose role to block with...", options=options)

    lock = InteractionLock()

    async def callback(interaction: discord.Interaction):
        # Check lock
        if lock.is_processing():
            return

        # Validate User
        if interaction.user.id != player.id:
            await interaction.response.send_message("Not Your Choice!", ephemeral = True)
            return
        
        # Acquire lock
        if not lock.acquire():
            return

        # Set result
        future.set_result(select.values[0])

        # Disable the Select to Show Choice Made
        select.disabled = True
        await interaction.response.send_message(view=select.view)

        # Release Lock
        lock.release()

    select.callback = callback
    return select

def choose_captain_inquisitor_select(player, future):
    options = [discord.SelectOption(label=card, value=card) for card in ["Captain", "Inquisitor"]]

    view = View(timeout=None)
    select = Select(
        placeholder="Choose role to block with...",
        options=options
    )

    async def callback(interaction: discord.Interaction):
        user = interaction.user
        if user.id != player.id:
            await interaction.resopnse.send_message(
                "Not Your Choice!", ephemeral = True
            )

        future.set_result(select.values[0])

        # Disable the Select to Show Choice Made
        select.disabled = True
        await interaction.response.send_message(view=select.view)

    select.callback = callback
    return select

def choose_captain_inquisitor_select(player, future):
    options = [discord.SelectOption(label=card, value=card) for card in ["Captain", "Inquisitor"]]

    select = Select(
        placeholder="Choose role to block with...",
        options=options
    )

    async def callback(interaction: discord.Interaction):
        user = interaction.user
        if user.id != player.id:
            await interaction.resopnse.send_message(
                "Not Your Choice!", ephemeral = True
            )

        future.set_result(select.values[0])

        # Disable the Select to Show Choice Made
        select.disabled = True
        await interaction.response.send_message(view=select.view)

    select.callback = callback
    return select

# -----------------------
# Buttons
# -----------------------

def create_block_button(game):
    """Generic Block Button"""
    button = Button(label="Block", style=discord.ButtonStyle.danger)

    lock = InteractionLock()

    async def callback(interaction: discord.Interaction):
        # Check lock
        if lock.is_processing():
            return
        
        # Validate User
        user = interaction.user
        action: Action = game.current_action

        if user.id == action.actor.id or user.id not in game.get_turn_order_ids():
            await interaction.response.send_message("You cannot block!", ephemeral=True)
            return
        
        # Acquire Lock
        if not lock.acquire():
            return

        # Update Action
        action.blocked = True
        action.blocker = game.get_player_by_id(user.id)

        # If Action is Steal, Choose to block as Captain or Inquisitor
        if action.name == "Steal":
            future = asyncio.get_event_loop().create_future()

            view = View(timeout=None)
            view.add_item(choose_captain_inquisitor_select(action.blocker, future))

            await interaction.response.send_message(
                content="Choose how to block:",
                view=view,
                ephemeral=True
            )
            # Await Response
            action.blocking_role = await future
        
        # Otherwise, map action blocked to role (only one choice)
        else:
            mapping = {"Collect Foreign Aid": "Duke", "Assassinate": "Contessa"}
            action.blocking_role = mapping[action.name]

        # Give chance to challenge
        await game.send_response_message()

        # Release lock
        lock.release()
    
    button.callback = callback
    return button


def create_challenge_button(game):
    button = Button(label="Challenge", style=discord.ButtonStyle.danger)

    lock = InteractionLock()

    async def callback(interaction: discord.Interaction):
        # Check lock
        if lock.is_processing():
            return
        
        # Validate User
        user = interaction.user
        action: Action = game.current_action

        if action.blocked:
            # Challenging the block
            if user.id == action.blocker.id or user.id not in game.get_player_ids():
                await interaction.response.send_message(
                    "You cannot challenge this block!", 
                    ephemeral=True
                )
                return
        else:
            # Challenging the Action
            if user.id not in game.get_turn_order_ids() or user.id == action.actor.id:
                await interaction.response.send_message(
                    "You cannot challenge this action!", 
                    ephemeral=True
                )
                return
            
        # Acquire lock
        if not lock.acquire():
            return

        # Update Action object
        action.challenged = True
        action.challenger = game.get_player_by_id(user.id)

        # Send Update Message
        if game.current_action.blocked == False:
            await game.send_update_msg(f"{action.challenger.name} has challenged the action!")
        else:
            await game.send_update_msg(f"{action.challenger.name} has challenged the role block!")
        await interaction.response.defer()
        # Handle the Challenge
        await game.handle_challenge()

        # Release lock
        lock.release()

    button.callback = callback
    return button


def create_prompt_button(target, future):
    button = Button(label="Choose", style=discord.ButtonStyle.danger)

    lock = InteractionLock()

    async def callback(interaction: discord.Interaction):
        # Check lock
        if lock.is_processing():
            return
        
        # Validate User
        if interaction.user.id != target.id:
            await interaction.response.send_message("You are not the player losing influence!", ephemeral=True)
            return
        
        # Acquire lock
        if not lock.acquire():
            return
        
        # Send Prompt
        view = View(timeout=None)
        view.add_item(create_influence_select(target, future))
        await interaction.response.send_message(
            view=view,
            embed=create_influence_select_embed(),
            ephemeral=True
        )

        # Release lock
        lock.release()

    button.callback = callback
    return button


def create_hand_button(game):
    button = Button(label="Check Hand", style=discord.ButtonStyle.blurple)

    async def callback(interaction: discord.Interaction):
        user = interaction.user

        if user.id not in game.get_player_ids():
            await interaction.response.send_message(
                "You are not in this game!", ephemeral=True
            )
        else:
            player = game.get_player_by_id(user.id)
            await interaction.response.send_message(
                f"Hand: {player.hand}",
                ephemeral=True
            )

    button.callback = callback
    return button

# === MISC ===

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