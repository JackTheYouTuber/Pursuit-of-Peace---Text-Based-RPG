"""
heal_entity — restore HP to any entity, capped at effective max HP.

Works for the player, an enemy, a companion — any state dict with
hp, max_hp, and buffs fields. Does not know who or why.
Returns the new state and the actual HP gained.
"""
from typing import Dict, Tuple


def heal_entity(state: Dict, amount: int) -> Tuple[Dict, int]:
    """
    Add `amount` HP to entity, capped at effective max HP
    (base max_hp + any max_hp buff bonuses).

    Args:
        state:  Entity state dict. Not mutated.
        amount: HP to restore. Must be positive.

    Returns:
        (new_state, actual_gained)
    """
    s = dict(state)
    old_hp = s.get("hp", 0)
    bonus_max = sum(
        b.get("stat_mods", {}).get("max_hp", 0)
        for b in s.get("buffs", [])
    )
    effective_max = s.get("max_hp", 20) + bonus_max
    new_hp = min(old_hp + amount, effective_max)
    s["hp"] = new_hp
    return s, new_hp - old_hp
