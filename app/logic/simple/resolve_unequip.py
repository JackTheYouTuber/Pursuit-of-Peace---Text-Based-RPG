"""resolve_unequip — move equipped item back to inventory."""
from typing import Dict, Tuple
from app.logic.simple.add_item import add_item

def resolve_unequip(state: Dict, slot: str) -> Tuple[Dict, str, bool]:
    if slot not in ("equipped_weapon", "equipped_armor"):
        return state, "Invalid slot.", False
    s  = dict(state)
    eq = s.get(slot)
    if not eq:
        return s, "Nothing equipped there.", False
    # Handle both dict format (current engine) and legacy plain-string format
    if isinstance(eq, dict):
        item_id = eq.get("item_id")
        name    = eq.get("item", {}).get("name", item_id)
    else:
        item_id = str(eq)
        name    = item_id
    s[slot] = None
    if item_id:
        s = add_item(s, item_id)
    return s, f"Unequipped {name}.", True
