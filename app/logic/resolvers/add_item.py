"""add_item — place an item into the player's inventory."""
from app.logic.action_types import ActionContext, ActionResult
from app.logic.simple.add_item import add_item


def resolve(ctx: ActionContext) -> ActionResult:
    item_id = ctx.reference
    if not item_id:
        return ActionResult(
            new_player_state  = dict(ctx.player_state),
            new_dungeon_state = ctx.dungeon_state,
            messages          = ["add_item: no item_id in reference."],
        )
    new_ps = add_item(dict(ctx.player_state), item_id)
    # Try to get item name from data registry
    name = item_id
    if ctx.data_registry:
        item = ctx.data_registry.items.get(item_id)
        if item:
            name = item.get("name", item_id)
    return ActionResult(
        new_player_state  = new_ps,
        new_dungeon_state = ctx.dungeon_state,
        messages          = [f"Received: {name}."],
    )
