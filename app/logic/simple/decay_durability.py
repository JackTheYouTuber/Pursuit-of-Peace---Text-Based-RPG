"""
Reduce durability of one equipped slot by 1.
Returns (new_state, item_broke: bool).
Does not unequip. Does not send messages. Does not care why.
"""
from typing import Dict, Tuple


def decay_durability(state: Dict, slot: str) -> Tuple[Dict, bool]:
    """
    Subtract 1 from the current_durability of the equipped item in `slot`.

    Args:
        state: Player state dict. Not mutated.
        slot:  "equipped_weapon" or "equipped_armor".

    Returns:
        (new_state, broke)  where broke=True when durability just reached 0.
    """
    s = dict(state)
    equipped = s.get(slot)
    if not equipped:
        return s, False

    eq = dict(equipped)
    cur = eq.get("current_durability", 0) - 1
    broke = cur <= 0
    eq["current_durability"] = max(0, cur)
    s[slot] = eq
    return s, broke
