"""
apply_consumable — parse an item's effect string and apply it to any entity.

Does not remove the item from inventory — the caller handles that.
Does not know whether the entity is a player or an enemy.
Returns (new_state, message, applied: bool).
"""
from typing import Dict, Tuple
from app.logic.simple.parse_effect  import parse_effect
from app.logic.simple.heal_entity   import heal_entity
from app.logic.simple.apply_buff    import apply_buff
from app.logic.simple.remove_buff   import remove_buff


def apply_consumable(state: Dict, item_name: str,
                     effect_text: str) -> Tuple[Dict, str, bool]:
    """
    Parse `effect_text` and mutate `state` accordingly.

    Args:
        state:       Entity state dict. Not mutated.
        item_name:   Display name (used in messages only).
        effect_text: Raw effect string from items.json.

    Returns:
        (new_state, message, applied)
        applied=False means the effect text was unrecognised.
    """
    parsed = parse_effect(effect_text)
    if parsed is None:
        return state, f"Used {item_name}. (No effect.)", False

    kind = parsed.get("type")

    if kind == "heal":
        s, gained = heal_entity(state, parsed["value"])
        hp  = s.get("hp", 0)
        mhp = s.get("max_hp", 20)
        return s, f"Used {item_name}. HP +{gained} ({hp}/{mhp}).", True

    if kind == "buff_damage":
        amount, turns = parsed["value"], parsed.get("turns", 3)
        buff = {
            "id": "strength_boost",
            "label": f"Strength +{amount}",
            "stat_mods": {"damage_bonus": amount},
            "duration": "turns",
            "duration_remaining": turns,
        }
        s = apply_buff(state, buff)
        return s, f"Used {item_name}. Damage +{amount} for {turns} turns.", True

    if kind == "remove_debuff":
        target = parsed.get("target", "")
        had = any(b.get("id") == target for b in state.get("buffs", []))
        s = remove_buff(state, target)
        msg = f"{target.capitalize()} cleansed." if had else f"Not {target}."
        return s, f"Used {item_name}. {msg}", True

    return state, f"Used {item_name}.", False
