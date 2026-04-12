"""heal_player — restore HP to the player, capped at effective max HP."""
from app.logic.action_types import ActionContext, ActionResult
from app.logic.simple.heal_entity import heal_entity


def resolve(ctx: ActionContext) -> ActionResult:
    amount = ctx.quantity or 10
    new_ps, gained = heal_entity(dict(ctx.player_state), amount)
    return ActionResult(
        new_player_state  = new_ps,
        new_dungeon_state = ctx.dungeon_state,
        messages          = [f"Healed {gained} HP."],
    )
