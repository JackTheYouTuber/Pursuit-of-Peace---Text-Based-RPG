"""resolve_equip — validate and execute an equip action."""
from typing import Dict, Optional, Tuple
from app.logic.simple.equip_item import equip_item

def resolve_equip(state: Dict, item_id: str, item_data: Dict) -> Tuple[Dict, str, bool]:
    item_type = item_data.get("type")
    if item_type not in ("weapon", "armor"):
        return state, f"{item_data.get('name', item_id)} cannot be equipped.", False
    slot = "equipped_weapon" if item_type == "weapon" else "equipped_armor"
    if item_id not in state.get("inventory", []):
        return state, "You don't have that item.", False
    s, displaced = equip_item(state, item_id, item_data, slot)
    bonus = item_data.get("stat_bonus", {})
    bonus_str = ""
    if "damage" in bonus:
        bonus_str = f" (+{bonus['damage']} dmg)"
    elif "defense" in bonus:
        bonus_str = f" (+{bonus['defense']} def)"
    return s, f"Equipped {item_data.get('name', item_id)}{bonus_str}.", True
