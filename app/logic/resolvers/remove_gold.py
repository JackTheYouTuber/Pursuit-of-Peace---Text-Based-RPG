"""remove_gold — deduct gold from the player (used for costs)."""
from app.logic.action_types import ActionContext, ActionResult
from app.logic.simple.remove_gold import remove_gold


def resolve(ctx: ActionContext) -> ActionResult:
    amount = ctx.quantity or 0
    ps = dict(ctx.player_state)
    if ps.get("gold", 0) < amount:
        return ActionResult(
            new_player_state  = ps,
            new_dungeon_state = ctx.dungeon_state,
            messages          = [f"Not enough gold (need {amount}g)."],
        )
    new_ps, remaining = remove_gold(ps, amount)
    return ActionResult(
        new_player_state  = new_ps,
        new_dungeon_state = ctx.dungeon_state,
        messages          = [f"Spent {amount}g. (Remaining: {remaining}g)"],
    )
