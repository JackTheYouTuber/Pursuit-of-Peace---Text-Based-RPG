"""remove_item — remove one copy of an item from the player's inventory."""
from app.logic.action_types import ActionContext, ActionResult
from app.logic.simple.remove_item import remove_item


def resolve(ctx: ActionContext) -> ActionResult:
    item_id = ctx.reference
    if not item_id:
        return ActionResult(
            new_player_state  = dict(ctx.player_state),
            new_dungeon_state = ctx.dungeon_state,
            messages          = ["remove_item: no item_id in reference."],
        )
    new_ps, removed = remove_item(dict(ctx.player_state), item_id)
    if not removed:
        return ActionResult(
            new_player_state  = new_ps,
            new_dungeon_state = ctx.dungeon_state,
            messages          = [f"Item '{item_id}' not in inventory."],
        )
    return ActionResult(
        new_player_state  = new_ps,
        new_dungeon_state = ctx.dungeon_state,
        messages          = [],
    )
