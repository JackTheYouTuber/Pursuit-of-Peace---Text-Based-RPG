# app/version.py
VERSION = "0.9.6"
VERSION_LABEL = f"v{VERSION}"

CHANGELOG = {
    "0.9.6": [
        "Player is no longer special — player and enemies use the same state dict shape "
        "and the same simples. Only their controllers differ.",
        "PlayerMgr: exclusive controller for the player. Calls simples directly. "
        "Handles city services, economy, year cycle.",
        "EntityMgr: exclusive controller for non-player entities (enemies, companions). "
        "Calls the same simples independently. No cross-delegation between managers.",
        "CombatMgr: coordinates PlayerMgr (player side) and EntityMgr (enemy side) "
        "symmetrically. Player action sent by human; enemy action decided by entity_ai.",
        "entity_ai.py (simple): pure function — entity state + combat context → action "
        "string. No imports. Primitively checks HP ratio to decide attack vs heal.",
        "New fragment simples extracted so both managers call shared logic independently: "
        "resolve_equip, resolve_unequip, apply_consumable, get_weapon_bonus, "
        "get_armor_defense, get_buff_bonus, get_effective_max_hp, get_buff_summary, "
        "is_alive, hp_ratio.",
        "Renamed: heal_player→heal_entity, damage_player→damage_entity, "
        "increment_kills→increment_stat (now general-purpose).",
        "Removed: item_mgr and buff_mgr — functionality absorbed into player_mgr "
        "and entity_mgr respectively, which each call simples directly.",
        "ViewBuilder uses fragment simples directly (get_buff_bonus, get_buff_summary) "
        "rather than going through a manager.",
    ],
    "0.9.5": [
        "Trinity architecture: Data / Logic / UI. Bureaucracy: Core → Complex → Simple.",
        "17 atomic simple units, 5 complex managers, 3 core orchestrators.",
    ],
    "0.9.4": [
        "Tier 1-3 gap closure: data-driven loot/gold, buff display, repair fix, "
        "durability bar, dead stub actions removed.",
    ],
}
