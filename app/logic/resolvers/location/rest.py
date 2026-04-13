"""location.rest — pay to rest at a tavern; restore full HP."""
from app.logic.action_types import ActionContext, ActionResult
from app.logic.simple.remove_gold import remove_gold
from app.logic.simple.get_effective_max_hp import get_effective_max_hp


def resolve(ctx: ActionContext) -> ActionResult:
    ps = dict(ctx.player_state)
    reg = ctx.data_registry
    cost = reg.config.prices().get("rest", 10) if reg else 10
    if ps.get("gold", 0) < cost:
        return ActionResult(ps, ctx.dungeon_state, [f"You need {cost}g to rest."])
    ps, _ = remove_gold(ps, cost)
    ps["hp"] = get_effective_max_hp(ps)
    return ActionResult(ps, ctx.dungeon_state, [f"You rest. HP fully restored. ({cost}g)"])
