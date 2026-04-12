"""location.view_debt — show current tax status."""
from app.logic.action_types import ActionContext, ActionResult

def resolve(ctx: ActionContext) -> ActionResult:
    ps  = dict(ctx.player_state)
    reg = ctx.data_registry
    tax = reg.config.prices().get("tax", 100) if reg else 100
    year = ps.get("year", 1)
    if ps.get("tax_paid"):
        msg = f"Year {year} taxes: PAID."
    else:
        msg = f"Year {year} taxes: {tax}g outstanding — due at year end."
    return ActionResult(ps, ctx.dungeon_state, [msg])
