# Contributing & Developer Guide — Pursuit of Peace  v1.0.0

---

## Adding a New Action (AAD Pattern)

Adding a new player action takes two files and zero engine changes.

### Step 1 — Create the action JSON

Create `data/actions/<action_id>.json`:

```json
{
  "id":          "pray_at_shrine",
  "resolver":    "location.pray",
  "cost":        {"gold": 5},
  "effects": [
    {"type": "heal_player", "entity_id": "0", "quantity": 3}
  ],
  "context_requirements": ["current_location_id"],
  "description": "Pray at the shrine for a small blessing."
}
```

**Required fields:** `id`, `resolver`  
**Optional fields:** `cost`, `effects`, `context_requirements`, `reference`, `description`

### Step 2 — Create the resolver

Create `app/logic/resolvers/location/pray.py`:

```python
from app.logic.action_types import ActionContext, ActionResult

def resolve(ctx: ActionContext) -> ActionResult:
    ps  = dict(ctx.player_state)
    reg = ctx.data_registry
    cost = 5
    if ps.get("gold", 0) < cost:
        return ActionResult(ps, ctx.dungeon_state,
                            [f"You cannot afford the {cost}g offering."])
    ps["gold"] -= cost
    ps["hp"]    = min(ps.get("hp", 0) + 3, ps.get("max_hp", 20))
    return ActionResult(ps, ctx.dungeon_state,
                        [f"You pray. A warmth settles over you. (+3 HP, -{cost}g)"])
```

**Rules for resolvers:**
- Export exactly one function: `resolve(ctx: ActionContext) -> ActionResult`.
- Never mutate `ctx.player_state` directly — always `dict(ctx.player_state)` first.
- Return a new `ActionResult`; never write to disk.
- Use `ctx.data_registry` for items, config, and lore lookups.

### Step 3 — Register nothing

The `ResolverRegistry` auto-discovers the file at startup. The `ActionDispatcher` picks up the JSON on next launch. No engine edits required.

### Step 4 — Add the action to a location (optional)

To make the action available at a city location, add its `id` to the `actions` array in `data/city/services.json`:

```json
"shrine": {
  "actions": ["pray_at_shrine", "go_city"]
}
```

---

## Adding a Shop to a Location

Add a `shop_inventory` array to the location's entry in `data/city/services.json`:

```json
"new_district": {
  "actions": ["buy_item", "sell_item", "go_city"],
  "shop_inventory": ["item_crude_knife_01", "item_bandage_01"]
}
```

The UI renders the shop section automatically. No Python changes needed.

---

## Developer Tools — DevTools.pyw

Run from the project root: `python DevTools.pyw`

### Tab 1 — Pycache Cleaner
Recursively deletes `__pycache__` folders. Use before packaging or after a refactor.

### Tab 2 — Audit Tool
Runs the engine in headless mode for N steps with an optional fixed seed. Reports crashes with full traceback and last 20 actions. Use after any engine change.

### Tab 3 — Build Tool
Wraps PyInstaller to produce a standalone distribution.

### Tab 4 — Validate Actions *(new in v1.0.0)*
Reads every JSON in `data/actions/`, validates against `data/schemas/action_schema.json`, and reports any missing required fields or type mismatches. Run this after adding action files to catch schema errors before launch.

### Tab 5 — Generate Resolver *(new in v1.0.0)*
Enter an action ID and resolver identifier. The tool scaffolds:
- `data/actions/<action_id>.json` with boilerplate fields.
- `app/logic/resolvers/<path>.py` with a stub `resolve` function.

---

## Debug Mode

```
python main.pyw --debug
```

Enables verbose console output: every dispatcher call prints the action ID, resolver name, and returned messages.

---

## Adding an Enemy

Add a new entry to `data/dungeon/enemies/enemies.json`. All fields are required:

```json
{
  "id":         "enemy_new_creature_01",
  "name":       "New Creature",
  "min_depth":  1,
  "max_depth":  4,
  "hp":         15,
  "damage_min": 2,
  "damage_max": 5,
  "gold_min":   3,
  "gold_max":   8,
  "loot_chance": 0.6,
  "loot_count":  1,
  "loot_table":  ["item_bone_shard_01"]
}
```

---

## Adding an Item

Add a new entry to `data/dungeon/items/items.json`:

```json
{
  "id":       "item_my_new_item_01",
  "name":     "My New Item",
  "type":     "consumable",
  "min_depth": 0,
  "value":    12,
  "effect":   "Restores 8 hp",
  "source":   null
}
```

`type` must be one of: `consumable`, `weapon`, `armor`, `misc`.  
Weapons and armors require `stat_bonus` and `durability` fields.

---

## Coding Conventions

- **Simples** (`app/logic/simple/`) — pure functions, no class, no imports from complex or core. One job each.
- **Resolvers** (`app/logic/resolvers/`) — one `resolve(ctx) → ActionResult` per file. No mutation of ctx. Use simples for atomic operations.
- **Managers** (`app/logic/complex/`) — coordinate multiple simples for complex multi-step operations (combat round, dungeon traversal). May hold session state.
- **Engine** (`app/logic/core/engine.py`) — routes actions, applies state changes, triggers year clock. No game-logic calculations.
- **UI** (`app/ui/`) — reads state dicts, renders widgets, fires callbacks. No game logic.
