"""location.hear_rumors — fetch a random rumor from tavern lore."""
import random
from app.logic.action_types import ActionContext, ActionResult

def resolve(ctx: ActionContext) -> ActionResult:
    ps  = dict(ctx.player_state)
    reg = ctx.data_registry
    rumors = reg.lore.by_type("tavern", "rumor") if reg else []
    if not rumors:
        return ActionResult(ps, ctx.dungeon_state, ["The tavern is quiet tonight."])
    return ActionResult(ps, ctx.dungeon_state, [random.choice(rumors).get("text", "")])
