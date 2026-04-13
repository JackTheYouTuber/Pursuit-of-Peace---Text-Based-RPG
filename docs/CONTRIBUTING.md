# Contributing & Developer Guide — Pursuit of Peace  v1.0.0-stable

---

## Quick Reference

| Task | Files to create/edit |
|------|----------------------|
| Add a new action | `data/actions/<id>.json` + `app/logic/resolvers/<path>.py` |
| Add an item | `data/dungeon/items/items.json` |
| Add an enemy | `data/dungeon/enemies/enemies.json` |
| Add a city location | `data/city/locations.json` + `data/city/services.json` + lore file |
| Add a shop | `data/city/services.json` (add `shop_inventory` to existing location) |
| Modify prices | `data/economy/prices.json` |

No engine edits are needed for any of the above.

---

## Adding a New Action (Full Example)

The AAD system means adding a new action is always two files and zero engine changes.

### Step 1 — Create the action JSON

Create `data/actions/pray_at_shrine.json`:

```json
{
  "id":          "pray_at_shrine",
  "resolver":    "location.pray",
  "cost":        {"gold": 5},
  "effects": [
    {"type": "heal_player", "entity_id": "0", "quantity": 3}
  ],
  "context_requirements": ["current_location_id"],
  "reference":   null,
  "description": "Pray at the shrine for a small blessing. Costs 5g, restores 3 HP."
}
```

**Required fields:** `id`, `resolver`
**Optional fields:** `cost`, `effects`, `context_requirements`, `reference`, `description`

The `effects` array is advisory — it documents intent but resolvers are free to implement however they like. Only `id` and `resolver` are validated at startup.

### Step 2 — Create the resolver module

Create `app/logic/resolvers/location/pray.py`:

```python
"""
location.pray — resolver for the pray_at_shrine action.

Costs 5 gold, heals 3 HP (capped at max_hp).
Fails silently if the player cannot afford the offering.
"""
from app.logic.action_types import ActionContext, ActionResult


def resolve(ctx: ActionContext) -> ActionResult:
    ps   = dict(ctx.player_state)   # always copy first — never mutate ctx
    cost = 5
    heal = 3

    if ps.get("gold", 0) < cost:
        return ActionResult(
            new_player_state  = ps,
            new_dungeon_state = ctx.dungeon_state,
            messages          = [f"You cannot afford the {cost}g offering."],
        )

    ps["gold"] -= cost
    ps["hp"]    = min(ps.get("hp", 0) + heal, ps.get("max_hp", 20))

    return ActionResult(
        new_player_state  = ps,
        new_dungeon_state = ctx.dungeon_state,
        messages          = [
            f"You kneel at the shrine. A warmth settles over you. (+{heal} HP, -{cost}g)"
        ],
    )
```

**Rules for resolvers:**
- Export exactly one callable: `resolve(ctx: ActionContext) -> ActionResult`.
- Always `ps = dict(ctx.player_state)` before any mutation.
- Return a new `ActionResult`; never write to disk or call external I/O.
- Use `ctx.data_registry` for item/enemy/config lookups — never import loaders directly.
- Keep resolvers small. Delegate atomic operations to `app/logic/simple/` functions.

### Step 3 — Register nothing

`ResolverRegistry` auto-discovers the file on next startup. `ActionDispatcher` picks up the JSON automatically. Zero engine or registry edits needed.

### Step 4 — Wire to a location (optional)

To show the action as a button in a city location, add its `id` to `data/city/services.json`:

```json
"shrine": {
  "actions": ["pray_at_shrine", "go_city"]
}
```

To add the location itself, also add an entry to `data/city/locations.json`:

```json
{
  "id":          "shrine",
  "name":        "Shrine of Stillness",
  "description": "A quiet stone shrine in the city's east quarter."
}
```

And create a lore file at `data/lore/shrine.json` (optional):

```json
[
  {
    "type":    "rumour",
    "text":    "They say the shrine was built before the walls, when the city was just a camp.",
    "source":  "An old priest"
  }
]
```

---

## Adding a Buff

Buffs are dicts attached to the player's `buffs` list. To award a buff from a resolver:

```python
from app.logic.simple.apply_buff import apply_buff

buff = {
    "id":       "buff_blessed",
    "name":     "Blessed",
    "duration": "one_run",    # "turns" | "one_run" | "permanent"
    "turns":    0,            # only used when duration == "turns"
    "effects":  [{"stat": "damage", "bonus": 2}]
}
ps = apply_buff(ps, buff)
```

Duration semantics:
- `"turns"` — decremented by `tick_buffs` after each attack; expires at 0.
- `"one_run"` — expires when the player leaves the dungeon (flee or completion).
- `"permanent"` — persists across sessions (saved in profile).

---

## Adding an Item

Add to `data/dungeon/items/items.json`:

```json
{
  "id":        "item_iron_sword_01",
  "name":      "Iron Sword",
  "type":      "weapon",
  "min_depth": 2,
  "value":     40,
  "effect":    null,
  "source":    null,
  "stat_bonus": {"damage": 5},
  "durability": 30
}
```

| Field | Required | Notes |
|-------|----------|-------|
| `id` | ✓ | Convention: `item_<name>_<seq>`. Must be unique. |
| `name` | ✓ | Display name. |
| `type` | ✓ | `weapon`, `armor`, `consumable`, or `misc`. |
| `value` | ✓ | Base sell price. Shops sell at face value; players sell at 40%. |
| `min_depth` | ✓ | Minimum dungeon depth for random loot drops. 0 = available everywhere. |
| `stat_bonus` | weapons/armor | `{"damage": N}` or `{"defense": N}`. |
| `durability` | weapons/armor | Max durability. Decays per hit; breaks at 0. |
| `effect` | consumables | Effect string: `"heal:8"`, `"buff:strength:3"`. |
| `source` | — | Flavour field. Unused by engine. |

---

## Adding an Enemy

Add to `data/dungeon/enemies/enemies.json`:

```json
{
  "id":          "enemy_iron_golem_01",
  "name":        "Iron Golem",
  "min_depth":   5,
  "max_depth":   10,
  "hp":          60,
  "damage_min":  8,
  "damage_max":  14,
  "gold_min":    20,
  "gold_max":    40,
  "loot_chance": 0.75,
  "loot_count":  2,
  "loot_table":  ["item_iron_sword_01", "item_armor_chain_01"]
}
```

All fields are required. `min_depth`/`max_depth` control which dungeon floors the enemy can appear on. `loot_table` entries must be valid item IDs.

---

## Adding a City Location

**1. Add display metadata** to `data/city/locations.json`:

```json
{
  "id":          "guild_hall",
  "name":        "Adventurers' Guild",
  "description": "A rowdy hall where contracts are pinned to a board."
}
```

**2. Add service definition** to `data/city/services.json`:

```json
"guild_hall": {
  "actions": ["take_contract", "go_city"]
}
```

**3. Add the navigation action** `data/actions/go_guild_hall.json`:

```json
{
  "id":       "go_guild_hall",
  "resolver": "navigation.go",
  "reference": "guild_hall",
  "description": "Navigate to the Adventurers' Guild."
}
```

**4. Wire the link from city entrance** — add `"go_guild_hall"` to the `actions` array of `"city_entrance"` in `services.json`.

---

## Adding a Shop to a Location

Add `shop_inventory` to any location in `services.json`:

```json
"guild_hall": {
  "actions": ["buy_item", "sell_item", "go_city"],
  "shop_inventory": ["item_iron_sword_01", "item_bandage_01", "item_antidote_01"]
}
```

The UI renders the shop panel automatically whenever `shop.items` is present in the view state. No Python changes needed.

---

## Versioning Scheme

`app/version.py` contains:

```python
VERSION       = "1.0.0"        # semantic version: MAJOR.MINOR.PATCH
VERSION_LABEL = f"v{VERSION}"  # e.g. "v1.0.0"
```

The DevTools Build Tool reads `VERSION_LABEL` to name the versioned output folder (`Build Output (v1.0.0)/`). Update `VERSION` when making a release.

Version naming convention for this project:
- `v1.0.0-alpha` — original public release with the AAD rewrite.
- `v1.0.0-stable` — this build; adds JSON Workshop, File Auditor, embedded profile UI, path fix for `.exe`, documentation.
- `v1.1.0` — planned fishing mini-loop, dynamic shop restocking, NPC merchants.

---

## Coding Conventions

**Simples** (`app/logic/simple/`) — pure functions, no class, no imports from `complex` or `core`. One responsibility each. Input → output, no side effects.

**Resolvers** (`app/logic/resolvers/`) — one `resolve(ctx) → ActionResult` per file. Use simples for atomic state mutations. Never import UI or engine modules.

**Complex managers** (`app/logic/complex/`) — stateful classes that coordinate multiple simples for multi-step operations (a full combat round, dungeon traversal). May hold session-level state (e.g. `CombatMgr._cs` for combat snapshot).

**Engine** (`app/logic/core/engine.py`) — routes actions, applies state changes from `ActionResult`, triggers the year clock. Contains no game-logic calculations — delegates entirely to the dispatcher and resolvers.

**UI** (`app/ui/`) — reads state dicts, renders widgets, fires callbacks to `GameActions` or `ProfileActions`. Contains no game logic and does not import from `app/logic/` except `action_types`.

---

## Debug Mode

```
python main.pyw --debug
```

Enables verbose console output. Every dispatcher call logs the action ID, resolver name, context overrides, and returned messages to both the console and the log file.

---

## Running the Audit Tool

The headless audit runner (`DevTools.pyw` → Audit Tool tab) simulates random game actions to stress-test the engine. To run a short audit from the command line:

```python
# headless_audit.py
from app.data_loader import DataLoader
from app.dungeon_manager import DungeonManager
from app.location_manager import LocationManager
from app.game_engine import GameEngine
import random, logging

loader   = DataLoader()
loc_mgr  = LocationManager(loader)
dun_mgr  = DungeonManager(loader)
engine   = GameEngine(loader, loc_mgr, dun_mgr)
engine.start_new_game("AuditProfile")

for step in range(1000):
    state = engine.get_view_state("city")
    actions = state.get("city", {}).get("actions", [])
    if actions:
        action_id = random.choice(actions)["id"]
        engine.do_location_action(action_id)
print("Audit complete, no crash.")
```
