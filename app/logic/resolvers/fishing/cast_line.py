"""fishing.cast_line — [stub v1.0.0] set fishing_active=True."""
from app.logic.action_types import ActionContext, ActionResult

def resolve(ctx: ActionContext) -> ActionResult:
    ps = dict(ctx.player_state)
    ps["fishing_active"] = True
    return ActionResult(ps, ctx.dungeon_state,
                        ["[Stub] You cast your line. (Fishing mini-loop coming in v1.1.0)"])
