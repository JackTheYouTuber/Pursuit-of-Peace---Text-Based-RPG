"""tick_buffs — decrement turn-based buffs; remove expired ones."""
from typing import Dict, List, Tuple

def tick_buffs(state: Dict) -> Tuple[Dict, List[str]]:
    s = dict(state)
    remaining, expired = [], []
    for buff in s.get("buffs", []):
        b = dict(buff)
        if b.get("duration") == "turns":
            rem = b.get("duration_remaining", 1) - 1
            if rem <= 0:
                expired.append(b.get("label", b.get("id")))
                continue
            b["duration_remaining"] = rem
        remaining.append(b)
    s["buffs"] = remaining
    return s, expired
