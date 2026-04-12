"""remove_item — remove one copy of item_id from inventory."""
from typing import Dict, Tuple

def remove_item(state: Dict, item_id: str) -> Tuple[Dict, bool]:
    s = dict(state)
    inv = list(s.get("inventory", []))
    if item_id not in inv:
        return s, False
    inv.remove(item_id)
    s["inventory"] = inv
    return s, True
