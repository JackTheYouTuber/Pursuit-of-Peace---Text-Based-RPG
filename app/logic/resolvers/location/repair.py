"""location.repair — repair an equipped weapon or armor at the blacksmith."""
from app.logic.action_types import ActionContext, ActionResult
from app.logic.simple.remove_gold import remove_gold


def resolve(ctx: ActionContext) -> ActionResult:
    ps   = dict(ctx.player_state)
    slot = ctx.reference  # "equipped_weapon" or "equipped_armor"
    if slot not in ("equipped_weapon", "equipped_armor"):
        return ActionResult(ps, ctx.dungeon_state, ["Invalid repair slot."])
    equipped = ps.get(slot)
    if not equipped:
        return ActionResult(ps, ctx.dungeon_state, ["Nothing equipped there."])
    cur = equipped.get("current_durability", 0)
    mx  = equipped.get("max_durability", 1)
    if cur >= mx:
        return ActionResult(ps, ctx.dungeon_state, ["Already at full durability."])
    reg  = ctx.data_registry
    ppp  = reg.config.prices().get("repair_per_point", 5) if reg else 5
    cost = (mx - cur) * ppp
    if ps.get("gold", 0) < cost:
        return ActionResult(ps, ctx.dungeon_state,
                            [f"Need {cost}g to repair (have {ps.get('gold',0)}g)."])
    ps, _ = remove_gold(ps, cost)
    eq = dict(equipped)
    eq["current_durability"] = mx
    ps[slot] = eq
    name = equipped.get("item", {}).get("name", "item")
    return ActionResult(ps, ctx.dungeon_state, [f"Repaired {name} to full. Cost: {cost}g."])
