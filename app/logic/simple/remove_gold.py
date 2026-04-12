"""remove_gold — deduct gold from player. Does not check affordability."""
from typing import Dict, Tuple

def remove_gold(state: Dict, amount: int) -> Tuple[Dict, int]:
    s = dict(state)
    amount = max(0, amount)
    s["gold"] = max(0, s.get("gold", 0) - amount)
    return s, s["gold"]
