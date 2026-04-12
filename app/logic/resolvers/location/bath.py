"""location.bath — pay for a bath; gain one_run max_hp buff."""
from app.logic.action_types import ActionContext, ActionResult
from app.logic.simple.remove_gold import remove_gold
from app.logic.simple.apply_buff  import apply_buff


def resolve(ctx: ActionContext) -> ActionResult:
    ps  = dict(ctx.player_state)
    reg = ctx.data_registry
    cost = reg.config.prices().get("bath", 15) if reg else 15
    if ps.get("gold", 0) < cost:
        return ActionResult(ps, ctx.dungeon_state, [f"You need {cost}g for a bath."])
    ps, _ = remove_gold(ps, cost)
    buff = {"id": "refreshed", "label": "Refreshed",
            "stat_mods": {"max_hp": 5}, "duration": "one_run"}
    ps = apply_buff(ps, buff)
    return ActionResult(ps, ctx.dungeon_state,
                        [f"You bathe. Max HP +5 for this dungeon run. ({cost}g)"])
