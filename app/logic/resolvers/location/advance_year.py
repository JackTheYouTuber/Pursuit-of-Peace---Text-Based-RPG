"""location.advance_year — increment year; exile player if taxes unpaid."""
from app.logic.action_types import ActionContext, ActionResult
from app.logic.simple.set_year import set_year

def resolve(ctx: ActionContext) -> ActionResult:
    ps = dict(ctx.player_state)
    if not ps.get("tax_paid", False):
        return ActionResult(
            new_player_state  = ps,
            new_dungeon_state = ctx.dungeon_state,
            messages = ["Taxes unpaid. The guards escort you beyond the gates. "
                        "GAME OVER — Exiled for tax debt."],
        )
    ps = set_year(ps, ps.get("year", 1) + 1)
    return ActionResult(ps, ctx.dungeon_state,
                        [f"A new year begins. Year {ps['year']} tax is now due."])
