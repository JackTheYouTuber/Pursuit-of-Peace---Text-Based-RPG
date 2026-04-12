"""dungeon.next_room — advance to the next dungeon room."""
from app.logic.action_types import ActionContext, ActionResult
from app.logic.simple.set_location    import set_location
from app.logic.simple.expire_run_buffs import expire_run_buffs

def resolve(ctx: ActionContext) -> ActionResult:
    ps = dict(ctx.player_state)
    ds = ctx.dungeon_state
    if not ds:
        return ActionResult(ps, ds, ["Not in a dungeon."])
    ds = dict(ds)
    current = ds.get("current_room", 0)
    total   = ds.get("total_rooms", 1)
    at_exit = (current + 1) >= total
    if at_exit:
        ps, _ = expire_run_buffs(ps)
        ps = set_location(ps, "city_entrance")
        return ActionResult(ps, None, ["You reach the dungeon exit and return to the city."])
    ds["current_room"] = current + 1
    room = ds.get("rooms", [{}])[ds["current_room"]]
    desc = room.get("description", "You enter the next room.")
    return ActionResult(ps, ds, [desc])
