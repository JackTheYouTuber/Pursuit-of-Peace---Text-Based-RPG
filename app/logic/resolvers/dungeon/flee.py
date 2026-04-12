"""dungeon.flee — exit the dungeon without completing it."""
from app.logic.action_types import ActionContext, ActionResult
from app.logic.simple.expire_run_buffs import expire_run_buffs
from app.logic.simple.set_location     import set_location

def resolve(ctx: ActionContext) -> ActionResult:
    ps = dict(ctx.player_state)
    ps, _ = expire_run_buffs(ps)
    ps = set_location(ps, "city_entrance")
    return ActionResult(ps, None, ["You flee back to the city gates."])
