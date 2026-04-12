"""shop.sell — sell an item from inventory at sell_price_multiplier of its value."""
from app.logic.action_types import ActionContext, ActionResult
from app.logic.simple.remove_item import remove_item
from app.logic.simple.add_gold    import add_gold

def resolve(ctx: ActionContext) -> ActionResult:
    ps      = dict(ctx.player_state)
    item_id = ctx.reference
    reg     = ctx.data_registry
    if not item_id:
        return ActionResult(ps, ctx.dungeon_state, ["sell: no item_id specified."])
    if item_id not in ps.get("inventory", []):
        return ActionResult(ps, ctx.dungeon_state, ["You don't have that item."])
    for slot in ("equipped_weapon", "equipped_armor"):
        eq = ps.get(slot)
        if eq and eq.get("item_id") == item_id:
            return ActionResult(ps, ctx.dungeon_state,
                                ["That item is equipped. Unequip it first."])
    item = reg.items.get(item_id) if reg else None
    if item is None:
        return ActionResult(ps, ctx.dungeon_state, [f"Unknown item: {item_id}"])
    mult  = reg.config.prices().get("sell_price_multiplier", 0.4) if reg else 0.4
    price = max(1, int(item.get("value", 0) * mult))
    ps, _ = remove_item(ps, item_id)
    ps, _ = add_gold(ps, price)
    return ActionResult(ps, ctx.dungeon_state,
                        [f"Sold {item['name']} for {price}g."])
