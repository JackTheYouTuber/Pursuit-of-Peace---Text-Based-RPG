"""
add_gold — give gold to the player.

Does nothing else. Does not know why the player is receiving gold.
"""
from typing import Dict, Tuple


def add_gold(state: Dict, amount: int) -> Tuple[Dict, int]:
    """
    Add `amount` gold to player.

    Args:
        state:  Player state dict. Not mutated.
        amount: Gold to add. Must be positive.

    Returns:
        (new_state, new_gold_total)
    """
    s = dict(state)
    amount = max(0, amount)
    s["gold"] = s.get("gold", 0) + amount
    return s, s["gold"]
