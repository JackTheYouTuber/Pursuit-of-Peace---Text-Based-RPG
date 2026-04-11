"""
hp_ratio — compute current HP as a fraction of max HP for any entity.

One job. Returns 0.0 on a dead or uninitialised entity.
Does not know what entity this is.
"""
from typing import Dict


def hp_ratio(state: Dict) -> float:
    mx = state.get("max_hp", 1)
    return state.get("hp", 0) / mx if mx > 0 else 0.0
