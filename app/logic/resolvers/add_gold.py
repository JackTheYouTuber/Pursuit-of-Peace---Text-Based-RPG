"""add_gold — give the player gold."""
from app.logic.action_types import ActionContext, ActionResult
from app.logic.simple.add_gold import add_gold


def resolve(ctx: ActionContext) -> ActionResult:
    amount = ctx.quantity or 0
    new_ps, total = add_gold(dict(ctx.player_state), amount)
    return ActionResult(
        new_player_state  = new_ps,
        new_dungeon_state = ctx.dungeon_state,
        messages          = [f"Gained {amount} gold. (Total: {total}g)"],
    )
