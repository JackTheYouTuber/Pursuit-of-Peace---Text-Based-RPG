"""location.enter_dungeon — transition the player into the dungeon."""
from app.logic.action_types import ActionContext, ActionResult
from app.logic.simple.set_location import set_location

def resolve(ctx: ActionContext) -> ActionResult:
    ps  = dict(ctx.player_state)
    reg = ctx.data_registry
    dungeon = reg.dungeon.generate() if reg else {}
    ps = set_location(ps, "dungeon_entrance")
    return ActionResult(ps, dungeon, ["You descend into the darkness."])
