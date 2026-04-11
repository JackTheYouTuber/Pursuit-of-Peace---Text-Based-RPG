"""
entity_ai — primitive AI controller for non-player entities.

One job: given an entity's state and the current combat context,
return a single action string. That's all.

The AI does not execute anything. It does not mutate state.
It just observes and decides. The entity_mgr takes that decision
and makes it happen.

This is intentionally primitive. Later tiers can swap in smarter
AI by changing only this file (or swapping to a different one).
"""
from typing import Dict, Optional


def decide_combat_action(entity_state: Dict, combat_context: Dict) -> str:
    """
    Decide what action an entity takes this combat round.

    Current logic (primitive):
      - If HP < 30% of max and has a healing consumable → use it
      - Otherwise → attack

    Args:
        entity_state:   The entity's full state dict (hp, max_hp, inventory,
                        equipped_weapon, buffs, etc.)
        combat_context: Snapshot of the current combat round:
                        {
                          "opponent_hp":      int,
                          "opponent_max_hp":  int,
                          "round":            int,
                          "entity_hp":        int,
                          "entity_max_hp":    int,
                        }

    Returns:
        Action string — one of:
          "attack"
          "use_item:<item_id>"
          "flee"
    """
    hp      = entity_state.get("hp", 0)
    max_hp  = entity_state.get("max_hp", 1)
    ratio   = hp / max_hp if max_hp > 0 else 1.0

    # Try to heal if critically low
    if ratio < 0.30:
        heal_item = _find_heal_item(entity_state)
        if heal_item:
            return f"use_item:{heal_item}"

    return "attack"


def decide_loot_item(entity_state: Dict, available_items: list) -> Optional[str]:
    """
    Decide whether to pick up an available item.

    Current logic: always take the first item if inventory is not full.

    Returns:
        item_id to take, or None to leave it.
    """
    if not available_items:
        return None
    inventory = entity_state.get("inventory", [])
    if len(inventory) >= entity_state.get("max_inventory", 20):
        return None
    return available_items[0].get("id")


# -- Helpers ------------------------------------------------------------

def _find_heal_item(entity_state: Dict) -> Optional[str]:
    """Return the first consumable item_id that restores HP, or None."""
    inventory = entity_state.get("inventory", [])
    # Entity state carries item_ids only; we match by id prefix convention.
    # In production the item_mgr would pass item defs — here we use id heuristics
    # so this simple has zero external imports.
    for item_id in inventory:
        lower = item_id.lower()
        if "potion" in lower or "tonic" in lower or "bandage" in lower or "ration" in lower:
            return item_id
    return None
