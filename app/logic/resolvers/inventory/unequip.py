"""inventory.unequip — move item from equipment slot back to inventory."""
from app.logic.action_types import ActionContext, ActionResult
from app.logic.simple.resolve_unequip import resolve_unequip

def resolve(ctx: ActionContext) -> ActionResult:
    ps   = dict(ctx.player_state)
    slot = ctx.reference
    new_ps, msg, _ = resolve_unequip(ps, slot)
    return ActionResult(new_ps, ctx.dungeon_state, [msg])
