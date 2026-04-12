"""fishing.fishing_tick — [stub v1.0.0] 60% chance to catch a random fish."""
import random
from app.logic.action_types import ActionContext, ActionResult
from app.logic.simple.add_item import add_item

def resolve(ctx: ActionContext) -> ActionResult:
    ps  = dict(ctx.player_state)
    reg = ctx.data_registry
    ps["fishing_active"] = False
    if random.random() < 0.6:
        pool = reg.items.by_source("fishing") if reg else []
        if pool:
            caught = random.choice(pool)
            ps = add_item(ps, caught["id"])
            return ActionResult(ps, ctx.dungeon_state, [f"You catch: {caught['name']}."])
    return ActionResult(ps, ctx.dungeon_state, ["Nothing bites."])
