"""
add_item — place an item ID into the player's inventory.

Does not know what the item is. Does not check for duplicates.
Does not enforce inventory limits (not yet implemented).
"""
from typing import Dict


def add_item(state: Dict, item_id: str) -> Dict:
    """
    Append `item_id` to player inventory.

    Args:
        state:   Player state dict. Not mutated.
        item_id: String ID of the item to add.

    Returns:
        new_state
    """
    s = dict(state)
    inventory = list(s.get("inventory", []))
    inventory.append(item_id)
    s["inventory"] = inventory
    return s
