# Data Schema Reference — Pursuit of Peace

All game content is stored as JSON files under `data/`. This document describes the schema for each file.

---

## `data/player/defaults.json`

Default state applied to every new profile.

```json
{
  "hp":        20,
  "max_hp":    20,
  "gold":      50,
  "level":     1,
  "inventory": [],
  "year":      1,
  "tax_paid":  false,
  "buffs":     []
}
```

| Field | Type | Description |
|---|---|---|
| `hp` | int | Current hit points |
| `max_hp` | int | Maximum hit points |
| `gold` | int | Current gold |
| `level` | int | Player level (currently cosmetic) |
| `inventory` | string[] | List of `item_id` strings |
| `year` | int | Current in-game year |
| `tax_paid` | bool | Whether tax has been paid this year |
| `buffs` | object[] | Active buff/debuff list (see services schema) |

---

## `data/player/profiles/<name>.json`

One file per saved profile.

```json
{
  "profile_name": "Jack",
  "last_saved":   "2026-04-08T14:09:00",
  "player_state": { ... }
}
```

`player_state` matches the defaults schema above.

---

## `data/city/locations.json`

Array of location definitions.

```json
[
  {
    "id":            "tavern",
    "name":          "Tavern",
    "access":        "always",
    "condition_ref": null
  }
]
```

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique location identifier |
| `name` | string | Display name |
| `access` | string | `"always"` or a condition key (future use) |
| `condition_ref` | string\|null | Key into a conditions table (not yet used) |

---

## `data/city/services.json`

Object mapping `location_id` → service config. Drives all action menus.

```json
{
  "tavern": {
    "actions":   ["rest", "hear_rumors", "go_city"],
    "rest_cost": 10
  },
  "public_bath": {
    "actions":    ["take_bath", "go_city"],
    "bath_cost":  15,
    "bath_buff": {
      "stat":     "max_hp",
      "amount":   5,
      "duration": "one_run",
      "label":    "Refreshed"
    }
  }
}
```

The `actions` array is the canonical list of action IDs shown to the player at that location. Extra keys are service-specific config consumed by action handlers.

---

## `data/economy/prices.json`

Flat map of service costs.

```json
{
  "rest":            10,
  "bath":            15,
  "tax":             100,
  "repair_per_point": 5
}
```

---

## `data/dungeon/config.json`

```json
{
  "min_rooms": 5,
  "max_rooms": 10,
  "max_depth": 5
}
```

| Field | Type | Description |
|---|---|---|
| `min_rooms` | int | Minimum rooms per dungeon run |
| `max_rooms` | int | Maximum rooms per dungeon run |
| `max_depth` | int | Maximum depth level (affects enemy scaling) |

---

## `data/dungeon/rooms/room_templates.json`

Array of room type definitions.

```json
[
  {
    "id":        "room_enemy_01",
    "has_enemy": true,
    "has_item":  false,
    "lore_key":  "lore_room_enemy_01"
  }
]
```

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique template identifier |
| `has_enemy` | bool | Whether this room type spawns an enemy |
| `has_item` | bool | Whether this room type contains an item |
| `lore_key` | string | Key into `data/lore/dungeon.json` for room description text |

---

## `data/dungeon/enemies/enemies.json`

Array of enemy definitions.

```json
[
  {
    "id":          "enemy_bloat_rat_01",
    "name":        "Bloated Rat",
    "min_depth":   1,
    "max_depth":   2,
    "hp":          10,
    "damage_min":  1,
    "damage_max":  3,
    "loot_table":  ["item_bone_shard_01", "item_tattered_cloth_01"]
  }
]
```

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique enemy identifier |
| `name` | string | Display name |
| `min_depth` | int | Minimum dungeon depth at which this enemy can spawn |
| `max_depth` | int | Maximum depth (use 99 for no cap) |
| `hp` | int | Starting hit points |
| `damage_min` | int | Minimum damage per attack (not yet used — see ISSUE-001) |
| `damage_max` | int | Maximum damage per attack (not yet used — see ISSUE-001) |
| `loot_table` | string[] | Item IDs that can drop on defeat (not yet used) |

---

## `data/dungeon/items/items.json`

Array of item definitions.

```json
[
  {
    "id":        "item_bandage_01",
    "name":      "Cloth Bandage",
    "type":      "consumable",
    "min_depth": 0,
    "value":     6,
    "effect":    "Restores 5 hp",
    "source":    null
  }
]
```

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique item identifier |
| `name` | string | Display name |
| `type` | string | `"weapon"`, `"armor"`, `"consumable"`, `"misc"` |
| `min_depth` | int | Minimum dungeon depth for this item to appear |
| `value` | int | Gold value (buy/sell price reference) |
| `effect` | string\|null | Human-readable effect description |
| `source` | string\|null | `"fishing"` for river-only items; `null` for dungeon items |

---

## `data/lore/<location_id>.json`

Array of lore entries for a location.

```json
[
  {
    "id":   "lore_key_01",
    "type": "description",
    "text": "The tavern smells of smoke and stale ale."
  }
]
```

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique key (used by `lore_key` in room templates) |
| `type` | string | `"description"`, `"ambient"`, `"rumor"` |
| `text` | string | The lore text to display |

**Type behaviour:**
- `description` — shown as the main location description text.
- `ambient` — fallback if no description entry exists.
- `rumor` — shown when player uses `hear_rumors` at the Tavern.

---

## `data/ui/themes.json`

Theme configuration for the `UIAssembler`.

```json
{
  "global": {
    "bg":          "#0d1b2a",
    "fg":          "#d4c9a8",
    "font_family": "Courier",
    "font_size":   11
  },
  "TextDisplay": { "bg": "#1a1a2e" },
  "LocationPanel": { "bg": "#16213e" }
}
```

Keys at the top level are either `"global"` (applied as defaults) or a component type name matching the `UIAssembler._COMPONENT_REGISTRY`.

---

## `data/ui/layouts/<view_name>.json`

A layout descriptor that the `UIAssembler` reads to build a view. Uses dot-path notation (`"combat.log"`) to bind widget data to state dict fields returned by `GameEngine.get_view_state()`.

```json
{
  "type":      "CombatPanel",
  "name":      "combat_panel",
  "data": {
    "log_source":         "combat.log",
    "enemy_name_source":  "combat.enemy_name",
    "enemy_hp_source":    "combat.enemy_hp",
    "actions_source":     "combat.actions"
  },
  "on_action": "combat_action"
}
```

| Field | Type | Description |
|---|---|---|
| `type` | string | Component class name (must be in `UIAssembler._COMPONENT_REGISTRY`) |
| `name` | string | Identifier used in the component cache |
| `data` | object | Key→dot-path bindings for data sources |
| `on_action` / `on_select` | string | Callback key looked up in the assembler's `_callbacks` dict |
| `children` | object[] | Optional child components (for container types) |
| `layout` | string | `"vertical"` (default) or `"horizontal"` for containers |
