"""
damage_entity — subtract HP from any entity, floor at 0.

Works for the player, an enemy, a companion — any state dict with
an hp field. Does not know the source of damage. Does not delete
profiles or trigger any consequence. Returns dead=True when HP=0.
"""
from typing import Dict, Tuple


def damage_entity(state: Dict, amount: int) -> Tuple[Dict, bool]:
    """
    Subtract `amount` HP from entity. HP cannot go below 0.

    Args:
        state:  Entity state dict. Not mutated.
        amount: Damage to deal. Must be positive.

    Returns:
        (new_state, is_dead)
    """
    s = dict(state)
    amount = max(0, amount)
    new_hp = max(0, s.get("hp", 0) - amount)
    s["hp"] = new_hp
    return s, new_hp <= 0
