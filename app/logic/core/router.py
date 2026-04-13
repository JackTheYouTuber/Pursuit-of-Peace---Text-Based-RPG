"""
router.py — maps action_id strings to (manager, method, args) triples.

The engine asks "what should I call for action_id X?".
The router answers without executing anything.
New action types are registered here — the engine never needs if/elif chains.
"""
from typing import Optional, Tuple


_NAV = {
    "go_tavern":            "tavern",
    "go_marketplace":       "marketplace",
    "go_alchemy_hall":      "alchemy_hall",
    "go_blacksmiths_street":"blacksmiths_street",
    "go_city_hall":         "city_hall",
    "go_coliseum":          "coliseum",
    "go_public_bath":       "public_bath",
    "go_the_river":         "the_river",
    "go_dungeon":           "dungeon_entrance",
    "go_city":              "city_entrance",
}


def is_nav(action_id: str) -> bool:
    return action_id in _NAV


def nav_target(action_id: str) -> Optional[str]:
    return _NAV.get(action_id)


# Parameterised action prefixes — split on first ":"
_PREFIXED = {
    "use_item",
    "equip_item",
    "unequip",
    "sell_item",
    "buy_item",
}


def is_prefixed(action_id: str) -> bool:
    return action_id.split(":", 1)[0] in _PREFIXED


def split_prefix(action_id: str) -> Tuple[str, str]:
    parts = action_id.split(":", 1)
    return parts[0], parts[1] if len(parts) > 1 else ""


# Simple keyword actions — just the string, no parameter
_CITY_ACTIONS = {
    "rest", "hear_rumors", "take_bath", "go_fishing",
    "pay_taxes", "view_debt", "enter_dungeon",
    "repair_weapon", "repair_armor",
}


def is_city_action(action_id: str) -> bool:
    return action_id in _CITY_ACTIONS
