"""location.fish — cast a line; randomly catch a fishing item."""
import random
from app.logic.action_types import ActionContext, ActionResult
from app.logic.simple.add_item import add_item


def resolve(ctx: ActionContext) -> ActionResult:
    ps  = dict(ctx.player_state)
    reg = ctx.data_registry
    pool = reg.items.by_source("fishing") if reg else []
    if not pool:
        return ActionResult(ps, ctx.dungeon_state, ["Nothing bites today."])
    caught = random.choice(pool)
    ps = add_item(ps, caught["id"])
    return ActionResult(ps, ctx.dungeon_state, [f"You catch: {caught['name']}."])
