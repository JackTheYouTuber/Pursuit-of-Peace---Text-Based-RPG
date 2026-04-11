"""
increment_stat — add an integer amount to any numeric field in any entity state.

One job: s[field] += amount. Does not know what the field means.
Works for kills, deaths, steps_taken, items_crafted, or any future counter.
"""
from typing import Dict


def increment_stat(state: Dict, field: str, amount: int = 1) -> Dict:
    """
    Add `amount` to state[field]. Creates the field at 0 if absent.

    Args:
        state:  Entity state dict. Not mutated.
        field:  Key to increment (e.g. "kills", "deaths").
        amount: How much to add (default 1).

    Returns:
        new_state
    """
    s = dict(state)
    s[field] = s.get(field, 0) + amount
    return s
