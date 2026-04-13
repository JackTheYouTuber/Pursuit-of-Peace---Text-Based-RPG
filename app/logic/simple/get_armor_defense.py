"""
get_armor_defense — read the defense value from an entity's equipped armor.

Returns (defense: int, armor_name: str).
Returns (0, '') when nothing is equipped or durability is 0.
Does not know what entity this is.
"""
from typing import Dict, Tuple


def get_armor_defense(state: Dict) -> Tuple[int, str]:
    ea = state.get("equipped_armor")
    if ea and isinstance(ea, dict) and ea.get("current_durability", 0) > 0:
        val  = ea.get("item", {}).get("stat_bonus", {}).get("defense", 0)
        name = ea.get("item", {}).get("name", "armor")
        return val, name
    return 0, ""
