# app/version.py
"""
Central version definition for Pursuit of Peace.
Bump this file when cutting a release.
"""

VERSION = "0.9.0"
VERSION_LABEL = f"v{VERSION}"

CHANGELOG = {
    "0.9.0": [
        "Tier 3 complete: weapon/armor equipment slots, combat damage scaling, "
        "durability decay, blacksmith repair.",
        "Tier 2 complete: consumable Use button in inventory and mid-combat, "
        "EffectResolver parses item effect text, BuffSystem tracks turn/run/permanent buffs.",
        "Public Bath grants Refreshed buff (+5 max HP, expires on dungeon exit).",
        "Inventory panel redesigned: equipment summary, Use/Equip/Unequip/Sell buttons.",
        "Player panel now shows gear bonuses and kill count.",
        "Tier 4 groundwork: buy_item / sell_item (40% return) wired through engine.",
    ],
    "0.8.0": [
        "Tier 1 fixes applied: enemies now drop gold and loot on defeat.",
        "Death handling corrected: player profile is deleted on death (not just reset).",
        "items.json updated with stat_bonus and durability fields for all weapons/armor.",
        "player/defaults.json updated with equipped_weapon/armor slots and stat tracking.",
        "Kill counter (player_state['kills']) now persisted.",
    ],
    "0.7.3": [
        "Year rollover trigger implemented (ISSUE-008).",
        "Dungeon lore text populated (ISSUE-009).",
    ],
    "0.7.0": [
        "Enemy counter-attack implemented (ISSUE-001).",
        "Player death detection (ISSUE-002).",
    ],
}
