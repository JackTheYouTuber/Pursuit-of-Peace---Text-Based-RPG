"""inventory.use_item — consume an item; apply its effect."""
from app.logic.action_types import ActionContext, ActionResult
from app.logic.simple.remove_item     import remove_item
from app.logic.simple.apply_consumable import apply_consumable

def resolve(ctx: ActionContext) -> ActionResult:
    ps      = dict(ctx.player_state)
    item_id = ctx.reference
    reg     = ctx.data_registry
    if not item_id:
        return ActionResult(ps, ctx.dungeon_state, ["use_item: no item_id."])
    if item_id not in ps.get("inventory", []):
        return ActionResult(ps, ctx.dungeon_state, ["You don't have that item."])
    item = reg.items.get(item_id) if reg else None
    if item is None:
        return ActionResult(ps, ctx.dungeon_state, [f"Unknown item: {item_id}"])
    if item.get("type") != "consumable":
        return ActionResult(ps, ctx.dungeon_state,
                            [f"{item.get('name', item_id)} isn't usable — try Equip."])
    ps, _ = remove_item(ps, item_id)
    ps, msg, _ = apply_consumable(ps, item.get("name", item_id), item.get("effect") or "")
    return ActionResult(ps, ctx.dungeon_state, [msg])
