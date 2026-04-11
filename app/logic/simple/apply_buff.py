"""
apply_buff — add a buff to the player's active effects list.

If a buff with the same id already exists it is replaced (no stacking
by default). Does not know the source of the buff or what triggered it.
"""
from typing import Dict


def apply_buff(state: Dict, buff: Dict) -> Dict:
    """
    Add `buff` to player_state["buffs"], replacing any existing buff
    with the same id.

    Args:
        state: Player state dict. Not mutated.
        buff:  Buff dict with keys: id, label, stat_mods, duration,
               and optionally duration_remaining.

    Returns:
        new_state
    """
    s = dict(state)
    buffs = [b for b in s.get("buffs", []) if b.get("id") != buff.get("id")]
    buffs.append(dict(buff))
    s["buffs"] = buffs
    return s
