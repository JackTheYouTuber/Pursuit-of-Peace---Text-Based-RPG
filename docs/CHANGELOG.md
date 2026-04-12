# Pursuit of Peace — Changelog

---

## v1.0.0 — Active Action Dispatch & Tier 4 Complete

### Architecture — Active Action Dispatch (AAD)

- **ActionContext / ActionResult** (`app/logic/action_types.py`) — frozen and mutable dataclasses that form the contract between the dispatcher and every resolver. No resolver mutates its input context.
- **ResolverRegistry** (`app/logic/resolver_registry.py`) — auto-discovers every resolver module under `app/logic/resolvers/` at startup. No manual registration. Adding a resolver is a file drop.
- **ActionDispatcher** (`app/logic/dispatcher.py`) — reads all `data/actions/*.json`, validates against the required-field schema, maps each action to its resolver, and executes the full dispatch chain including recursive sub-actions.
- **40 action JSON files** created under `data/actions/` — one per player action. Navigation, city services, combat, dungeon, inventory, shop, and utility (heal, gold, loot) actions all defined.
- **30 resolver modules** created — zero unavailable at startup. All produce `ActionResult`; none mutate input state.
- **Engine rewrite** — `app/logic/core/engine.py` wired to route all city/shop/inventory/navigation actions through `ActionDispatcher._dispatch()`. Combat session state and dungeon traversal remain in `CombatMgr` / `DungeonMgr` because they require multi-round UI coordination.

### Tier 4 — Shop Economy

- **`shop_inventory`** arrays added to `marketplace` (11 items), `alchemy_hall` (8 items), and `blacksmiths_street` (7 items) in `data/city/services.json`.
- **`shop.buy` resolver** — validates item is in current location's `shop_inventory`, checks gold, deducts cost, adds item.
- **`shop.sell` resolver** — validates item in inventory and not equipped, awards `value × sell_price_multiplier` (40%).
- **Shop UI** — `LocationPanel` now includes a collapsible shop section rendered automatically when the location has `shop_inventory`. Clicking an item dispatches `buy_item:<item_id>`.
- City layout (`data/ui/layouts/city.json`) updated with `shop_source` binding. `DataBinder` updated to route shop state to the panel.

### Tier 4 — Data-Driven Loot

- All 12 enemies verified to have `loot_table`, `loot_chance`, `loot_count`, `gold_min`, `gold_max` fields.
- **`combat.award_loot` resolver** — rolls `loot_chance`, loops `loot_count` times, picks random items from `loot_table`, dispatches `add_item` and `add_gold` sub-actions.
- `award_loot.json` action file added; `award_loot` is dispatched as a sub-action by `combat.attack` on enemy death.

### Buffs (Step 8)

- `tick_buffs` resolver dispatched after every attack round in `CombatMgr`.
- `expire_run_buffs` called on dungeon exit and flee paths.
- `advance_year` resolver replaces the old direct `PlayerMgr.year_rollover()` call — year rollover now produces a `DATA` log event.

### Year Rollover (Step 8)

- `Engine._tick_year()` dispatches `advance_year` action every 30 non-navigation actions.
- Exile path calls `Engine._on_exile()`: profile deleted, state reset to defaults, clock reset.

### Fishing Stubs (Step 8)

- `data/fish_pool.json` created with weighted fish pool.
- `fishing.cast_line` and `fishing.fishing_tick` resolver stubs created. Structure in place for v1.1.0 implementation.

### Missing Simple Modules

Eight modules created to complete `PlayerMgr` import chain: `remove_buff`, `remove_gold`, `remove_item`, `resolve_equip`, `resolve_unequip`, `set_location`, `set_year`, `tick_buffs`.

### Developer Tools (Step 10)

- **Validate Actions tab** — reads all `data/actions/*.json`, validates against `data/schemas/action_schema.json`, reports errors in a scrollable log.
- **Generate Resolver tab** — scaffolds a new action JSON + stub resolver Python file from two text inputs.
- `--debug` flag added to `main.pyw` — enables verbose console output from the dispatcher.
- Startup validation in `ActionDispatcher.load_actions()` — unavailable actions logged as warnings, game continues.

---

## v0.9.0 — Tier 2 & Tier 3 Complete

### Tier 2 — Consumable & Effect System
- `EffectResolver` parses item effect strings; applies heal, damage-buff, and debuff-removal.
- `BuffSystem` manages `turns`, `one_run`, and `permanent` buff durations.
- Use button in inventory; use item mid-combat.
- Bath buff (+5 max HP, `one_run`); Strength potion (+3 damage, 3 turns).

### Tier 3 — Equipment & Combat Progression
- `equipped_weapon` / `equipped_armor` slots wired into combat damage and defense.
- Durability decay per hit; auto-unequip on break with warning message.
- Blacksmith repair action; cost = `(max − current) × repair_per_point`.
- Inventory panel shows equipment summary with durability bars.

---

## v0.7.0 — Tier 1 Complete

- Enemy counter-attack implemented.
- Player death deletes profile permanently (roguelike death).
- Year rollover + exile for unpaid taxes.
- Combat gold rewards (data-driven via `gold_min` / `gold_max`).
- Loot drops (data-driven via `loot_table` / `loot_chance`).
- Kill counter tracked and displayed.
