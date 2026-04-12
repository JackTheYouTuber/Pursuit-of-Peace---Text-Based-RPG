"""location.pay_taxes — pay annual tax at city hall."""
from app.logic.action_types import ActionContext, ActionResult
from app.logic.simple.remove_gold import remove_gold


def resolve(ctx: ActionContext) -> ActionResult:
    ps  = dict(ctx.player_state)
    reg = ctx.data_registry
    if ps.get("tax_paid"):
        return ActionResult(ps, ctx.dungeon_state, ["Taxes already paid this year."])
    tax = reg.config.prices().get("tax", 100) if reg else 100
    if ps.get("gold", 0) < tax:
        return ActionResult(ps, ctx.dungeon_state,
                            [f"Need {tax}g to pay taxes. Return before year end or face exile."])
    ps, _ = remove_gold(ps, tax)
    ps["tax_paid"] = True
    return ActionResult(ps, ctx.dungeon_state, [f"Taxes paid. ({tax}g) You are clear until next year."])
