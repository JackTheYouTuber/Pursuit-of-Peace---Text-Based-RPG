"""dungeon.take_item — pick up the item in the current room."""
from app.logic.action_types import ActionContext, ActionResult
from app.logic.simple.add_item import add_item

def resolve(ctx: ActionContext) -> ActionResult:
    ps = dict(ctx.player_state)
    ds = ctx.dungeon_state
    if not ds:
        return ActionResult(ps, ds, ["Not in a dungeon."])
    room = ds.get("rooms", [{}])[ds.get("current_room", 0)]
    item_id = room.get("item")
    if not item_id:
        return ActionResult(ps, ds, ["No item here."])
    ps = add_item(ps, item_id)
    ds = dict(ds)
    rooms = list(ds.get("rooms", []))
    r = dict(rooms[ds["current_room"]])
    r["item"] = None
    rooms[ds["current_room"]] = r
    ds["rooms"] = rooms
    reg = ctx.data_registry
    name = item_id
    if reg:
        item = reg.items.get(item_id)
        if item:
            name = item.get("name", item_id)
    return ActionResult(ps, ds, [f"You pick up: {name}."])
