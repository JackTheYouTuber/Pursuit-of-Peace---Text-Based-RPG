"""remove_buff — remove a buff from active effects by id."""
from typing import Dict

def remove_buff(state: Dict, buff_id: str) -> Dict:
    s = dict(state)
    s["buffs"] = [b for b in s.get("buffs", []) if b.get("id") != buff_id]
    return s
