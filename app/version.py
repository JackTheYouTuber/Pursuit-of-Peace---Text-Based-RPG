# app/version.py
VERSION = "0.9.5"
VERSION_LABEL = f"v{VERSION}"

CHANGELOG = {
    "0.9.5": [
        "Major restructuring: Trinity architecture (UI / Logic / Data).",
        "Logic Simple: 17 atomic single-job functions (heal_player, damage_player, "
        "add_gold, remove_gold, add_item, remove_item, equip_item, unequip_item, "
        "apply_buff, remove_buff, tick_buffs, expire_run_buffs, decay_durability, "
        "parse_effect, set_location, increment_kills, set_year).",
        "Logic Complex: 5 managers coordinating simples (buff_mgr, item_mgr, "
        "player_mgr, combat_mgr, dungeon_mgr). Each validates orders and returns "
        "(new_state, message). Never raises.",
        "Logic Core: engine, state, year_clock, router, view_builder. "
        "Engine delegates to managers — no game rules inline.",
        "Data layer split into loaders (item, enemy, lore, config — one file type each) "
        "and managers (profile_mgr, dungeon_gen, location_mgr). Wired by DataRegistry.",
        "UI reorganised into core (app, window, controllers), complex (assembler, "
        "coordinator), simple (widgets, binder, registry).",
        "Router maps action_id strings to intent — engine has zero if/elif chains "
        "for new action types.",
    ],
    "0.9.4": [
        "Tier 1 complete: enemies.json fully data-driven with gold_min/max, "
        "loot_chance, loot_count.",
        "Tier 2: buffs shown in player panel. sell_price_multiplier in prices.json.",
        "Tier 3: repair_equipment mismatch fixed. Durability bar in inventory.",
        "Dead stub actions removed from marketplace, alchemy, coliseum.",
    ],
    "0.9.0": [
        "Tier 2 & 3 complete: equipment slots, durability, consumable effects, "
        "buff system, inventory UI redesign.",
    ],
    "0.8.0": [
        "Tier 1 fixes: combat gold/loot rewards, profile deleted on death, "
        "kill counter.",
    ],
    "0.7.3": ["Year rollover. Dungeon lore text."],
    "0.7.0": ["Enemy counter-attack. Player death detection."],
}
