# Data Schema Reference — Pursuit of Peace  v1.0.0

All game content lives in JSON files under `data/`. This document describes every schema.

---

## `data/actions/<action_id>.json`  *(new in v1.0.0)*

The AAD action catalogue. One file per player action.

```json
{
  "id":                   "take_bath",
  "resolver":             "location.bath",
  "cost":                 {"gold": 15},
  "effects": [
    {"type": "heal_player", "entity_id": "0", "quantity": 5},
    {"type": "add_buff",    "entity_id": "0", "reference": "buff_refreshed"}
  ],
  "context_requirements": ["current_location_id"],
  "description":          "Soak in the public bath. Gain Refreshed buff for this run."
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✓ | Unique action identifier. Must match filename stem. |
| `resolver` | string | ✓ | Dot-path to resolver module (e.g. `"location.bath"`). |
| `cost` | object | — | Optional gold/resource cost hint for UI display. |
| `effects` | array | — | Declarative sub-effects (informational; resolvers decide execution). |
| `context_requirements` | array | — | Keys that must be present in ActionContext for this action to be valid. |
| `reference` | any | — | Default value for `ActionContext.reference` if not overridden by caller. |
| `description` | string | — | Human-readable description for developer tools. |

`id` and `resolver` are the only two fields validated at startup. All others are advisory.

---

## `data/city/services.json`

Location service definitions. Each key is a `location_id`.

```json
{
  "marketplace": {
    "actions": ["buy_item", "sell_item", "go_city"],
    "shop_inventory": [
      "item_sword_iron_01",
      "item_armor_leather_01",
      "item_bandage_01"
    ]
  },
  "blacksmiths_street": {
    "actions": ["repair_weapon", "repair_armor", "go_city"],
    "repair_per_point": 5,
    "shop_inventory": ["item_sword_iron_01", "item_armor_chain_01"]
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `actions` | string[] | Action IDs available at this location. Rendered as buttons in the city view. |
| `shop_inventory` | string[] | *(new v1.0.0)* Item IDs for sale here. Triggers shop panel in UI. Optional. |
| `rest_cost` | int | Override rest price for this location. |
| `repair_per_point` | int | Override repair cost per durability point. |

---

## `data/dungeon/enemies/enemies.json`

Enemy definitions array.

```json
{
  "id":          "enemy_bloat_rat_01",
  "name":        "Bloated Rat",
  "min_depth":   1,
  "max_depth":   2,
  "hp":          10,
  "damage_min":  1,
  "damage_max":  3,
  "gold_min":    2,
  "gold_max":    5,
  "loot_chance": 0.55,
  "loot_count":  1,
  "loot_table":  ["item_bone_shard_01", "item_tattered_cloth_01"]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✓ | Unique enemy ID. |
| `name` | string | ✓ | Display name. |
| `min_depth` / `max_depth` | int | ✓ | Dungeon depth range for random spawning. |
| `hp` | int | ✓ | Starting hit points. |
| `damage_min` / `damage_max` | int | ✓ | Attack damage range per round. |
| `gold_min` / `gold_max` | int | ✓ | Gold reward range on defeat. |
| `loot_chance` | float (0–1) | ✓ | Probability of dropping loot. |
| `loot_count` | int | ✓ | Number of items to roll when loot triggers. |
| `loot_table` | string[] | ✓ | Pool of item IDs to draw from. |

---

## `data/dungeon/items/items.json`

Item definitions array.

```json
{
  "id":         "item_sword_iron_01",
  "name":       "Iron Sword",
  "type":       "weapon",
  "min_depth":  0,
  "value":      40,
  "effect":     null,
  "source":     null,
  "stat_bonus": {"damage": 5},
  "durability": 50
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique item ID. |
| `name` | string | Display name. |
| `type` | string | `"weapon"`, `"armor"`, `"consumable"`, `"misc"`. |
| `min_depth` | int | Minimum dungeon depth for loot spawning. |
| `value` | int | Base gold value. Used for buy price; sell = `value × sell_price_multiplier`. |
| `effect` | string\|null | Effect text for consumables. Parsed by `apply_consumable`. |
| `source` | string\|null | `"fishing"` tags items as catchable at the river. |
| `stat_bonus` | object | `{"damage": N}` for weapons; `{"defense": N}` for armors. |
| `durability` | int | Base durability (weapons and armors only). |

---

## `data/economy/prices.json`

```json
{
  "rest":                   10,
  "bath":                   15,
  "tax":                    100,
  "repair_per_point":       5,
  "sell_price_multiplier":  0.4
}
```

| Field | Description |
|-------|-------------|
| `rest` | Gold cost to rest at the tavern. |
| `bath` | Gold cost for the public bath. |
| `tax` | Annual tax due at year end. |
| `repair_per_point` | Gold per missing durability point at the blacksmith. |
| `sell_price_multiplier` | Fraction of item `value` returned on sale (0.4 = 40%). |

---

## `data/player/defaults.json`

Loaded for every new profile.

```json
{
  "hp":             20,
  "max_hp":         20,
  "gold":           50,
  "level":          1,
  "inventory":      [],
  "year":           1,
  "tax_paid":       false,
  "buffs":          [],
  "equipped_weapon": null,
  "equipped_armor":  null,
  "kills":          0,
  "times_died":     0
}
```

---

## `data/fish_pool.json`  *(new in v1.0.0)*

Weighted pool for the fishing mini-loop (stub; active in v1.1.0).

```json
[
  {"id": "item_fish_common_01", "name": "River Perch",    "weight": 50},
  {"id": "item_fish_bony_01",   "name": "Bony Grey Carp", "weight": 30},
  {"id": "item_fish_bloated_01","name": "Bloated Mudfish", "weight": 20}
]
```

---

## `data/schemas/action_schema.json`  *(new in v1.0.0)*

JSON Schema used by the Validate Actions developer tool.

```json
{
  "type": "object",
  "required": ["id", "resolver"],
  "properties": {
    "id":       {"type": "string"},
    "resolver": {"type": "string"},
    "cost":     {"type": "object"},
    "effects":  {"type": "array"},
    "context_requirements": {"type": "array", "items": {"type": "string"}},
    "reference": {},
    "description": {"type": "string"}
  },
  "additionalProperties": true
}
```

---

## Buff Object Schema

Stored in `player_state["buffs"]` as an array of dicts.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique buff type. Same-id buffs replace each other (no stacking). |
| `label` | string | Display name. |
| `stat_mods` | object | `{"max_hp": 5}`, `{"damage_bonus": 3}`, `{"defense_bonus": 2}`. |
| `duration` | string | `"turns"`, `"one_run"`, or `"permanent"`. |
| `duration_remaining` | int | Turn count remaining (only when `duration == "turns"`). |
