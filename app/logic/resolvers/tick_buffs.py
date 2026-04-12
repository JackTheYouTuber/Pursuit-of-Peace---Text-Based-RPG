"""tick_buffs — decrement turn-based buffs, remove expired ones."""
from app.logic.action_types import ActionContext, ActionResult
from app.logic.simple.tick_buffs import tick_buffs


def resolve(ctx: ActionContext) -> ActionResult:
    new_ps, expired = tick_buffs(dict(ctx.player_state))
    msgs = [f"Buff expired: {name}." for name in expired]
    return ActionResult(new_ps, ctx.dungeon_state, msgs)
