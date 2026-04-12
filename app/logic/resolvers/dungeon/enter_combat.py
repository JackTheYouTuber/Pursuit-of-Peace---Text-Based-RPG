"""dungeon.enter_combat — transition to combat with the current room's enemy."""
from app.logic.action_types import ActionContext, ActionResult

def resolve(ctx: ActionContext) -> ActionResult:
    # This resolver signals the UI layer to switch to combat view.
    # Actual combat state initialisation is handled by CombatMgr.
    ps = dict(ctx.player_state)
    ds = ctx.dungeon_state
    if not ds:
        return ActionResult(ps, ds, ["Not in a dungeon."])
    room = ds.get("rooms", [{}])[ds.get("current_room", 0)]
    enemy = room.get("enemy")
    if not enemy:
        return ActionResult(ps, ds, ["No enemy in this room."])
    return ActionResult(ps, ds, [f"A {enemy.get('name','creature')} bars your path!"])
