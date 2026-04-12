"""combat.attack — player attacks the active enemy; enemy retaliates."""
import random
from app.logic.action_types import ActionContext, ActionResult
from app.logic.simple.get_weapon_bonus  import get_weapon_bonus
from app.logic.simple.get_armor_defense import get_armor_defense
from app.logic.simple.get_buff_bonus    import get_buff_bonus
from app.logic.simple.decay_durability  import decay_durability
from app.logic.simple.damage_entity     import damage_entity
from app.logic.simple.tick_buffs        import tick_buffs


def resolve(ctx: ActionContext) -> ActionResult:
    ps      = dict(ctx.player_state)
    ds      = ctx.dungeon_state
    msgs    = []
    dispatched = []

    # reference holds the enemy dict snapshot
    enemy = ctx.reference or {}

    # ── Player strikes ────────────────────────────────────────────────
    base_dmg   = random.randint(4, 8)
    buff_bonus = get_buff_bonus(ps, "damage_bonus")
    wpn_bonus, wpn_label = get_weapon_bonus(ps)
    total_dmg  = base_dmg + buff_bonus + wpn_bonus

    if wpn_bonus > 0:
        msgs.append(f"You strike the {enemy.get('name','enemy')} for {total_dmg} damage! "
                    f"({base_dmg}+{wpn_bonus} from {wpn_label})")
    else:
        msgs.append(f"You strike the {enemy.get('name','enemy')} for {total_dmg} damage!")

    # Decay weapon durability
    if ps.get("equipped_weapon"):
        ps, broke = decay_durability(ps, "equipped_weapon")
        if broke:
            name = ps.get("equipped_weapon", {}) or {}
            msgs.append(f"⚠ Your weapon has broken!")
            ps["equipped_weapon"] = None

    enemy_hp_remaining = enemy.get("_current_hp", enemy.get("hp", 10)) - total_dmg

    if enemy_hp_remaining <= 0:
        msgs.append(f"The {enemy.get('name','enemy')} falls.")
        dispatched.append(("award_loot", {"reference": enemy, "entity_id": ctx.entity_id}))
        return ActionResult(ps, ds, msgs, dispatched)

    # ── Enemy retaliates ──────────────────────────────────────────────
    raw_dmg  = random.randint(enemy.get("damage_min", 1), enemy.get("damage_max", 3))
    arm_def, arm_label = get_armor_defense(ps)
    taken    = max(1, raw_dmg - arm_def)

    if arm_def > 0:
        msgs.append(f"The {enemy.get('name','enemy')} strikes for {raw_dmg}! "
                    f"Your {arm_label} absorbs {arm_def}. You take {taken} HP.")
        ps, broke = decay_durability(ps, "equipped_armor")
        if broke:
            msgs.append("⚠ Your armor has broken!")
            ps["equipped_armor"] = None
    else:
        msgs.append(f"The {enemy.get('name','enemy')} strikes back for {taken} damage!")

    ps, dead = damage_entity(ps, taken)
    if dead:
        msgs.append("You collapse. Everything goes dark.")

    # Tick turn buffs after attack round
    ps, expired = tick_buffs(ps)
    for name in expired:
        msgs.append(f"Buff expired: {name}.")

    return ActionResult(ps, ds, msgs, dispatched)
