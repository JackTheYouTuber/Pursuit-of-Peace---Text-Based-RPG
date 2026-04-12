"""navigation.go — change the player's current location."""
from app.logic.action_types import ActionContext, ActionResult
from app.logic.simple.set_location import set_location

def resolve(ctx: ActionContext) -> ActionResult:
    dest = ctx.reference or ""
    if not dest:
        return ActionResult(dict(ctx.player_state), ctx.dungeon_state,
                            ["navigation.go: no destination in reference."])
    new_ps = set_location(dict(ctx.player_state), dest)
    return ActionResult(new_ps, ctx.dungeon_state, [])
