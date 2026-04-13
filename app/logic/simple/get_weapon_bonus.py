"""
get_weapon_bonus — read the damage bonus from an entity's equipped weapon.

Returns (bonus: int, weapon_name: str).
Returns (0, 'bare hands') when nothing is equipped or durability is 0.
Does not know what entity this is.
"""
from typing import Dict, Tuple


def get_weapon_bonus(state: Dict) -> Tuple[int, str]:
    ew = state.get("equipped_weapon")
    if ew and isinstance(ew, dict) and ew.get("current_durability", 0) > 0:
        bonus = ew.get("item", {}).get("stat_bonus", {}).get("damage", 0)
        name  = ew.get("item", {}).get("name", "weapon")
        return bonus, name
    return 0, "bare hands"
