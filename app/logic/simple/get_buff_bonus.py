"""
get_buff_bonus — sum one stat_mods field across all active buffs.

One job: given a state dict and a field name, return the total bonus
from all active buffs that provide that modifier.

Works for any entity. Does not know what the field means.
"""
from typing import Dict


def get_buff_bonus(state: Dict, field: str) -> int:
    """
    Sum state['buffs'][*]['stat_mods'][field] across all active buffs.

    Args:
        state: Entity state dict.
        field: Key in stat_mods (e.g. 'damage_bonus', 'max_hp', 'defense_bonus').

    Returns:
        Total integer bonus (0 if no buffs or field absent).
    """
    return sum(b.get("stat_mods", {}).get(field, 0) for b in state.get("buffs", []))
