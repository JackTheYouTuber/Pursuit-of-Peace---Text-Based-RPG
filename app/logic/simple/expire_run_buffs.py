"""Remove all one_run buffs. Called when player exits the dungeon."""
from typing import Dict, List, Tuple


def expire_run_buffs(state: Dict) -> Tuple[Dict, List[str]]:
    """
    Strip every buff whose duration == "one_run".
    Returns (new_state, list_of_expired_labels).
    """
    s = dict(state)
    kept, expired = [], []
    for b in s.get("buffs", []):
        if b.get("duration") == "one_run":
            expired.append(b.get("label", b.get("id", "?")))
        else:
            kept.append(b)
    s["buffs"] = kept
    return s, expired
