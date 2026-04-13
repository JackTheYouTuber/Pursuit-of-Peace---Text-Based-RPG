"""shop.buy — purchase an item from the current location's shop_inventory."""
from app.logic.action_types import ActionContext, ActionResult
from app.logic.simple.remove_gold import remove_gold
from app.logic.simple.add_item    import add_item


def resolve(ctx: ActionContext) -> ActionResult:
    ps      = dict(ctx.player_state)
    item_id = ctx.reference
    reg     = ctx.data_registry

    if not item_id:
        return ActionResult(ps, ctx.dungeon_state, ["buy: no item specified."])

    # Verify item is in this location's shop inventory
    shop_inv = (ctx.location_state or {}).get("shop_inventory", [])
    if shop_inv and item_id not in shop_inv:
        return ActionResult(ps, ctx.dungeon_state,
                            ["That item is not available here."])

    item = reg.items.get(item_id) if reg else None
    if item is None:
        return ActionResult(ps, ctx.dungeon_state, [f"Unknown item: {item_id}"])

    price = item.get("value", 0)
    if ps.get("gold", 0) < price:
        return ActionResult(ps, ctx.dungeon_state,
                            [f"Need {price}g to buy {item['name']} "
                             f"(you have {ps.get('gold', 0)}g)."])

    ps, _ = remove_gold(ps, price)
    ps    = add_item(ps, item_id)
    return ActionResult(ps, ctx.dungeon_state,
                        [f"Purchased {item['name']} for {price}g."])
