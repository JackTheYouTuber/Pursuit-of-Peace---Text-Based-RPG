"""equip_item — move an item from inventory into weapon/armor slot."""
from app.logic.action_types import ActionContext, ActionResult
from app.logic.simple.resolve_equip import resolve_equip


def resolve(ctx: ActionContext) -> ActionResult:
    item_id = ctx.reference
    if not item_id:
        return ActionResult(dict(ctx.player_state), ctx.dungeon_state, ["equip_item: no item_id."])
    reg = ctx.data_registry
    item_data = reg.items.get(item_id) if reg else None
    if item_data is None:
        return ActionResult(dict(ctx.player_state), ctx.dungeon_state, [f"Unknown item: {item_id}"])
    new_ps, msg, ok = resolve_equip(dict(ctx.player_state), item_id, item_data)
    return ActionResult(new_ps, ctx.dungeon_state, [msg])
