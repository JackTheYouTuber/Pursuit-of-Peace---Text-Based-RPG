# Data Schema Reference — Pursuit of Peace  v1.0.0-stable

All game content lives in JSON files under `data/`. This document describes every schema with a full example and an exhaustive field table.

---

## `data/actions/<action_id>.json`

One file per player action. 40 files exist in v1.0.0-stable.

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
  "reference":            null,
  "description":          "Soak in the public bath. Restores 5 HP and grants the Refreshed buff."
}
```

| Field | Type | Required | Default | Constraints |
|-------|------|----------|---------|-------------|
| `id` | string | ✓ | — | Must be unique. Must match the filename stem. |
| `resolver` | string | ✓ | — | Dotted path to resolver module (e.g. `"location.bath"`). Must exist in `ResolverRegistry`. |
| `cost` | object | — | `{}` | Advisory only. Keys: `"gold"` (int). Resolvers enforce actual costs. |
| `effects` | array | — | `[]` | Advisory documentation of intended effects. Resolvers decide execution. |
| `context_requirements` | array | — | `[]` | String keys that should be present in `ActionContext` for the action to be meaningful. Not enforced at runtime. |
| `reference` | any | — | `null` | Default value for `ActionContext.reference`. For nav actions: the destination `location_id`. For item actions: the `item_id`. |
| `description` | string | — | `""` | Human-readable description shown in DevTools Validate Actions tab. |

**Effect object schema** (advisory, within `effects` array):

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Effect type string (e.g. `"heal_player"`, `"add_buff"`, `"add_gold"`). |
| `entity_id` | string | `"0"` for player. |
| `quantity` | int | Amount for heal/gold effects. |
| `reference` | any | Item ID, buff dict, or slot name depending on `type`. |

---

## `data/city/locations.json`

Array of location display records. Controls what appears in the city navigation view.

```json
[
  {
    "id":          "tavern",
    "name":        "The Rusty Flagon",
    "description": "A dimly lit tavern that smells of ale and sawdust."
  }
]
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✓ | Must match a key in `services.json`. |
| `name` | string | ✓ | Display name shown as the location header. |
| `description` | string | ✓ | Flavour text shown below the name. |

---

## `data/city/services.json`

Object keyed by `location_id`. Defines available actions and optional shop/cost overrides.

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
  },
  "tavern": {
    "actions": ["rest", "hear_rumors", "go_city"],
    "rest_cost": 10
  }
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `actions` | string[] | ✓ | — | Action IDs rendered as buttons in the city view. Each must exist in `data/actions/`. |
| `shop_inventory` | string[] | — | `[]` | Item IDs for sale at this location. Triggers the shop panel in the UI. Items must exist in `items.json`. |
| `rest_cost` | int | — | `prices.rest` | Override rest price for this location only. |
| `repair_per_point` | int | — | `prices.repair_per_point` | Override repair cost per durability point. |

---

## `data/dungeon/enemies/enemies.json`

Array of enemy definitions. All 12 enemies in v1.0.0-stable have complete loot fields.

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

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `id` | string | ✓ | Unique | Convention: `enemy_<name>_<seq>`. |
| `name` | string | ✓ | — | Display name in combat. |
| `min_depth` | int | ✓ | 1–20 | Minimum dungeon floor for random placement. |
| `max_depth` | int | ✓ | ≥ min_depth | Maximum dungeon floor. |
| `hp` | int | ✓ | ≥ 1 | Starting hit points. |
| `damage_min` | int | ✓ | ≥ 0 | Minimum attack damage per round. |
| `damage_max` | int | ✓ | ≥ damage_min | Maximum attack damage per round. |
| `gold_min` | int | ✓ | ≥ 0 | Minimum gold on defeat. |
| `gold_max` | int | ✓ | ≥ gold_min | Maximum gold on defeat. |
| `loot_chance` | float | ✓ | 0.0–1.0 | Probability of dropping loot. |
| `loot_count` | int | ✓ | ≥ 0 | Number of items to roll when loot triggers. |
| `loot_table` | string[] | ✓ | Valid item IDs | Pool of item IDs for loot rolls. |

---

## `data/dungeon/items/items.json`

Array of item definitions. 24 items in v1.0.0-stable.

```json
{
  "id":        "item_crude_knife_01",
  "name":      "Crude Knife",
  "type":      "weapon",
  "min_depth": 0,
  "value":     8,
  "effect":    null,
  "source":    null,
  "stat_bonus": {"damage": 2},
  "durability": 20
}
```

| Field | Type | Required | Default | Constraints | Description |
|-------|------|----------|---------|-------------|-------------|
| `id` | string | ✓ | — | Unique | Convention: `item_<name>_<seq>`. |
| `name` | string | ✓ | — | — | Display name. |
| `type` | string | ✓ | — | `weapon`, `armor`, `consumable`, `misc` | Determines equip slot and inventory actions shown. |
| `min_depth` | int | ✓ | — | ≥ 0 | Minimum dungeon depth for random drops. 0 = available everywhere. |
| `value` | int | ✓ | — | ≥ 0 | Base price. Shops sell at face value; players sell at `sell_price_multiplier` (40%). |
| `effect` | string\|null | — | `null` | Consumable effect string. Format: `"heal:N"`, `"buff:<id>:<turns>"`. |
| `source` | string\|null | — | `null` | Flavour field. Unused by engine. |
| `stat_bonus` | object\|null | weapons/armor | `null` | Keys: `"damage"` (int) or `"defense"` (int). |
| `durability` | int\|null | weapons/armor | `null` | Max durability. Decays on hit; item breaks and auto-unequips at 0. |

**Effect string formats** (for consumables):

| Format | Example | Effect |
|--------|---------|--------|
| `"heal:N"` | `"heal:8"` | Restore N HP (capped at max_hp). |
| `"buff:<id>:<turns>"` | `"buff:strength:3"` | Apply named buff for N turns. |
| `"max_hp:N"` | `"max_hp:5"` | Permanently increase max_hp by N. |

---

## `data/dungeon/config.json`

Dungeon generation parameters.

```json
{
  "min_rooms":  5,
  "max_rooms": 12,
  "max_depth":  5
}
```

| Field | Type | Description |
|-------|------|-------------|
| `min_rooms` | int | Minimum number of rooms per dungeon. |
| `max_rooms` | int | Maximum number of rooms per dungeon. |
| `max_depth` | int | Maximum dungeon depth (floors). Controls which enemies can spawn. |

---

## `data/dungeon/rooms/room_templates.json`

Array of room type definitions used by `DungeonGen`.

```json
[
  {
    "type":        "enemy",
    "weight":      5,
    "description": "A dark room echoing with movement."
  },
  {
    "type":        "item",
    "weight":      3,
    "description": "A dusty alcove containing abandoned gear."
  },
  {
    "type":        "empty",
    "weight":      2,
    "description": "An unremarkable stone corridor."
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Room category: `enemy`, `item`, `empty`. Controls what is placed in the room. |
| `weight` | int | Relative probability weight for random room-type selection. |
| `description` | string | Flavour text shown when entering the room. |

---

## `data/economy/prices.json`

Global economy constants. Individual locations can override specific values.

```json
{
  "rest":                  10,
  "bath":                  15,
  "tax":                  100,
  "repair_per_point":       5,
  "sell_price_multiplier":  0.4
}
```

| Field | Type | Description |
|-------|------|-------------|
| `rest` | int | Default cost to rest at the tavern (restores full HP). |
| `bath` | int | Cost to take a public bath (HP heal + Refreshed buff). |
| `tax` | int | Annual tax owed at City Hall. Must be paid before year end. |
| `repair_per_point` | int | Gold cost per durability point when repairing gear. |
| `sell_price_multiplier` | float | Fraction of `value` awarded when selling items (0.4 = 40%). |

---

## `data/player/defaults.json`

Starting player state for new profiles.

```json
{
  "hp":        20,
  "max_hp":    20,
  "gold":      50,
  "level":     1,
  "inventory": [],
  "year":      1,
  "tax_paid":  false,
  "buffs":     [],
  "kills":     0,
  "current_location_id": "city_entrance",
  "equipped_weapon": null,
  "equipped_armor":  null
}
```

All fields are used at runtime. New profiles copy this dict then set `tax_paid = False`, `year = 1`, and `hp = max_hp`.

---

## `data/player/profiles/<name>.json`

Saved player profile.

```json
{
  "profile_name": "Jack",
  "last_saved":   "2025-08-01T14:32:01.123456",
  "player_state": { ... }
}
```

`player_state` is a full copy of the player state dict (same schema as `defaults.json`, extended with runtime fields). `ProfileMgr` is the only module that reads or writes these files.

---

## `data/economy/inventory_templates.json`

Named item bundles used for future shop restocking (v1.1.0). Currently informational.

```json
[
  {
    "id":    "bundle_fighter_starter",
    "items": ["item_crude_knife_01", "item_bandage_01"]
  }
]
```

---

## `data/lore/<location_id>.json`

Array of lore entries for one location. Used by `hear_rumors` and the Lore panel.

```json
[
  {
    "type":   "rumour",
    "text":   "They say a bandit lord hides in the deeper floors.",
    "source": "A nervous merchant"
  },
  {
    "type":   "history",
    "text":   "This hall was built two hundred years ago by the Guild of Hammers.",
    "source": null
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Entry category: `rumour`, `history`, `legend`. Used for filtering (future). |
| `text` | string | The lore text displayed to the player. |
| `source` | string\|null | Optional attribution shown in the UI. |

---

## `data/ui/themes.json`

Full colour and font theme. Auto-created on first launch from hardcoded defaults if missing.

```json
{
  "global": {
    "bg":          "#0f172a",
    "fg":          "#e2e8f0",
    "font_family": "Segoe UI",
    "font_size":   10,
    "card_bg":     "#1e293b"
  },
  "ActionButton": {"bg": "#3b82f6", "fg": "#ffffff"},
  "StatBar":      {"label_fg": "#94a3b8", "value_fg": "#fbbf24"},
  "TextDisplay":  {"bg": "#334155", "fg": "#e2e8f0"},
  "MenuList":     {"bg": "#1e293b"},
  "CombatPanel":  {"bg": "#1a0a0a", "header_fg": "#e94560"},
  "DialogBox":    {"bg": "#1e293b", "title_fg": "#fbbf24", "body_fg": "#e2e8f0",
                   "button_bg": "#3b82f6", "button_fg": "#ffffff"},
  "InventoryPanel": {"bg": "#16213e"},
  "LocationPanel":  {"bg": "#16213e"},
  "LorePanel":      {"bg": "#16213e"},
  "PlayerPanel":    {"bg": "#16213e"}
}
```

`StyleManager.init_styles()` reads this dict at startup and configures all ttk styles.

---

## `data/ui/layouts/<view_name>.json`

Layout descriptor for one game view. Defines the widget tree that `ComponentBuilder` assembles.

```json
{
  "type": "panel_grid",
  "panels": [
    {"id": "location",  "component": "LocationPanel",  "source": "city"},
    {"id": "player",    "component": "PlayerPanel",     "source": "player"},
    {"id": "lore",      "component": "LorePanel",       "source": "lore"}
  ]
}
```

The `source` key tells `DataBinder` which sub-dict of the view state to pass to each panel. Five layout files exist: `city.json`, `combat.json`, `dungeon.json`, `inventory.json`, `lore.json`.

---

## `data/schemas/action_schema.json`

JSON Schema used by the Validate Actions tab in DevTools to check action files.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["id", "resolver"],
  "properties": {
    "id":       {"type": "string"},
    "resolver": {"type": "string"}
  }
}
```

Only `id` and `resolver` are required at the schema level. All other fields are optional.

---

## `data/fish_pool.json`

Weighted fish catch pool for the fishing mini-loop (stub in v1.0.0-stable).

```json
[
  {"item_id": "item_carp_01",    "weight": 50},
  {"item_id": "item_pike_01",    "weight": 25},
  {"item_id": "item_eel_01",     "weight": 15},
  {"item_id": "item_old_boot",   "weight": 10}
]
```

`weight` is relative — higher values are more common. The fishing resolver randomly selects an item proportionally to its weight.
