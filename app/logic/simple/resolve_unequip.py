"""resolve_unequip — move equipped item back to inventory."""
from typing import Dict, Tuple
from app.logic.simple.add_item import add_item

def resolve_unequip(state: Dict, slot: str) -> Tuple[Dict, str, bool]:
    if slot not in ("equipped_weapon", "equipped_armor"):
        return state, "Invalid slot.", False
    s = dict(state)
    eq = s.get(slot)
    if not eq:
        return s, "Nothing equipped there.", False
    item_id = eq.get("item_id")
    name = eq.get("item", {}).get("name", item_id)
    s[slot] = None
    s = add_item(s, item_id)
    return s, f"Unequipped {name}.", True
