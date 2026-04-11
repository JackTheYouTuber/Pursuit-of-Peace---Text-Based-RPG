"""
equip_item — move an item from inventory into an equipment slot.

Does not validate item type compatibility — the caller must confirm
the item is a weapon or armour before calling this.
If the slot is already occupied, the old item is returned to inventory.
"""
from typing import Dict, Tuple, Optional


def equip_item(state: Dict, item_id: str, item_data: Dict,
               slot: str) -> Tuple[Dict, Optional[str]]:
    """
    Move `item_id` from inventory to `slot`. Return displaced item_id
    to inventory if slot was occupied.

    Args:
        state:     Player state dict. Not mutated.
        item_id:   ID of item being equipped.
        item_data: Full item dict from items.json (for stat_bonus, durability).
        slot:      "equipped_weapon" or "equipped_armor".

    Returns:
        (new_state, displaced_item_id_or_None)
    """
    s = dict(state)
    inventory = list(s.get("inventory", []))

    # Return currently equipped item to inventory
    displaced = None
    current = s.get(slot)
    if current:
        displaced = current.get("item_id")
        inventory.append(displaced)

    # Remove new item from inventory
    if item_id in inventory:
        inventory.remove(item_id)

    s["inventory"] = inventory
    s[slot] = {
        "item_id": item_id,
        "item": item_data,
        "current_durability": item_data.get("durability", 30),
        "max_durability": item_data.get("durability", 30),
    }
    return s, displaced
