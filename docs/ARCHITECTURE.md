# Architecture — Pursuit of Peace  v1.0.0

## Overview

The project uses a strict three-layer architecture (Data → Logic → UI) centred on the **Active Action Dispatch (AAD)** system. Every player-initiated action is described as a JSON file, routed through a central dispatcher, and executed by a pure-function resolver. No game logic lives in the UI; no UI logic lives in the engine.

---

## Directory Structure

```
Pursuit of Peace/
│
├── main.pyw                        Entry point. Creates GameLogger, runs App.
├── DevTools.pyw                    Developer tools: Cleaner, Audit, Build, Validate Actions, Generate Resolver.
│
├── app/
│   ├── app.py                      Root wiring class. Assembles Data + Logic + UI.
│   ├── version.py                  VERSION_LABEL constant.
│   │
│   ├── data/
│   │   ├── init/
│   │   │   ├── registry.py         DataRegistry — builds all loaders/managers once at startup.
│   │   │   ├── engine_factory.py   Creates Engine with a DataRegistry.
│   │   │   └── profile_selector.py Profile selection dialog (blocking).
│   │   ├── loaders/                ItemLoader, EnemyLoader, LoreLoader, ConfigLoader.
│   │   └── managers/               ProfileMgr, DungeonGen, LocationMgr.
│   │
│   ├── logic/
│   │   ├── action_types.py         ActionContext (frozen) and ActionResult dataclasses.
│   │   ├── resolver_registry.py    Auto-scans app/logic/resolvers/ at startup; no manual registration.
│   │   ├── dispatcher.py           ActionDispatcher — load_actions() + dispatch().
│   │   │
│   │   ├── resolvers/              One file per resolver. Each exports resolve(ctx) → ActionResult.
│   │   │   ├── heal_player.py
│   │   │   ├── add_gold.py / remove_gold.py
│   │   │   ├── add_item.py  / remove_item.py
│   │   │   ├── equip_item.py / tick_buffs.py
│   │   │   ├── location/           rest, bath, fish, pay_taxes, repair, hear_rumors,
│   │   │   │                       view_debt, advance_year, enter_dungeon
│   │   │   ├── combat/             attack, flee, award_loot
│   │   │   ├── shop/               buy, sell
│   │   │   ├── inventory/          use_item, unequip
│   │   │   ├── dungeon/            take_item, next_room, enter_combat, flee
│   │   │   ├── navigation/         go  (handles all go_* actions)
│   │   │   └── fishing/            cast_line, fishing_tick  (stubs, v1.1.0)
│   │   │
│   │   ├── simple/                 ~25 atomic pure functions (add_gold, heal_entity, …).
│   │   ├── complex/                PlayerMgr, EntityMgr, CombatMgr, DungeonMgr.
│   │   └── core/
│   │       ├── engine.py           Primary orchestrator. Routes all actions through AAD.
│   │       ├── state.py            Single source of truth for player + dungeon state.
│   │       ├── year_clock.py       Action counter; fires advance_year on rollover.
│   │       ├── router.py           Maps action_id strings (nav, prefixed, city).
│   │       └── view_builder.py     Builds UI state dicts from game state.
│   │
│   └── ui/
│       ├── core/                   MainWindow, GameActions controller, ProfileActions controller.
│       ├── complex/                UIAssembler, ViewCoordinator.
│       └── simple/                 Widgets, panels, data_binder, layout_loader, view_registry.
│
├── data/
│   ├── actions/                    40 action JSON files — the AAD action catalogue.
│   ├── city/                       locations.json, services.json (with shop_inventory).
│   ├── dungeon/                    enemies.json (full loot fields), items.json, room_templates.json.
│   ├── economy/                    prices.json, inventory_templates.json.
│   ├── player/                     defaults.json, profiles/.
│   ├── fish_pool.json              Fish item pool for the fishing mini-loop.
│   └── ui/                         layouts/, themes.json.
│
└── docs/
```

---

## Active Action Dispatch (AAD)

### The Problem It Solves

Before v1.0.0, `engine.py` contained a long `if/elif` chain for every possible action string. Adding a new action required editing the engine. Actions had no formal schema; their effects were scattered across multiple methods.

### How AAD Works

Every action is described in a small JSON file under `data/actions/`:

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

At startup `ActionDispatcher.load_actions()` reads every JSON, validates it, and resolves the `resolver` string against the `ResolverRegistry`. If the resolver module is missing or broken the action is marked unavailable and skipped — the game continues without it.

### Message-Passing Flow

```
UI widget click
  → GameActions.on_city_action("take_bath")
    → Engine.do_city_action("take_bath")
      → Engine._dispatch("take_bath")
        → ActionDispatcher.dispatch("take_bath", player_state, dungeon_state, location_state)
          → ResolverRegistry.get("location.bath")
            → location/bath.resolve(ActionContext) → ActionResult
          ← ActionResult(new_player_state, messages=[…], dispatched_actions=[])
        ← state applied; messages logged
      ← (changed=True, msg)
    ← refresh UI
```

Sub-actions in `ActionResult.dispatched_actions` are chained recursively inside `ActionDispatcher.dispatch()`.

### ActionContext

```python
@dataclass(frozen=True)
class ActionContext:
    player_state:   Dict
    dungeon_state:  Optional[Dict]
    location_state: Optional[Dict]   # current services.json entry
    entity_id:      str              # "0" = player
    quantity:       int
    reference:      Any              # item_id, buff dict, slot name, …
    action_id:      str
    data_registry:  Any              # read-only DataRegistry
```

### ActionResult

```python
@dataclass
class ActionResult:
    new_player_state:   Dict
    new_dungeon_state:  Optional[Dict]
    messages:           List[str]
    dispatched_actions: List[Tuple[str, Dict]]   # (action_id, context_overrides)
```

### Entity ID Scheme

| Prefix | Meaning | Example |
|--------|---------|---------|
| `"0"` | Player | `entity_id = "0"` |
| `"n_<name_hash>"` | Named NPC | `"n_a3f7"` (future) |
| `"e_<uuid>"` | Generated enemy instance | `"e_8b2c1d"` (future) |

---

## ResolverRegistry

`app/logic/resolver_registry.py` — scans `app/logic/resolvers/` recursively on startup. Any `.py` file that is not an `__init__` and exports a callable `resolve` is registered automatically. The resolver name is derived from the file's path relative to `resolvers/`:

```
resolvers/location/bath.py  →  "location.bath"
resolvers/combat/attack.py  →  "combat.attack"
resolvers/heal_player.py    →  "heal_player"
```

No manual registration is required. Adding a new resolver is a file drop.

---

## State Management

`app/logic/core/state.py` (`State`) is the single in-memory source of truth. The dispatcher never writes to disk. Only `ProfileMgr` touches the filesystem.

---

## Year Clock

`YearClock` in `app/logic/core/year_clock.py` counts non-navigation actions. Every 30 actions it signals the engine to `dispatch("advance_year", {})`. The `advance_year` resolver checks `tax_paid`; if unpaid it returns an exile message and the engine deletes the profile and resets state.

---

## Shop Economy (Tier 4)

Locations with a `shop_inventory` array in `data/city/services.json` display a shop panel in the city view. Clicking an item dispatches `buy_item:<item_id>`. The `shop.buy` resolver verifies the item is in `location_state["shop_inventory"]`, checks affordability, deducts gold, and adds the item. `shop.sell` verifies the item is in inventory and not equipped before awarding sell price (`value × sell_price_multiplier`).
