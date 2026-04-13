# Architecture — Pursuit of Peace  v1.0.0-stable

## Overview

Pursuit of Peace uses a strict three-layer architecture (**Data → Logic → UI**) centred on the **Active Action Dispatch (AAD)** system. Every player-initiated action is described as a JSON file, routed through a central dispatcher, and executed by a pure-function resolver. No game logic lives in the UI; no UI logic lives in the engine.

The project also ships `DevTools.pyw`, a seven-tab developer utility that runs against the same codebase without requiring the game to be open.

---

## Directory Structure

```
PursuitOfPeace/
│
├── main.pyw                        Entry point. Creates GameLogger, runs App.
├── DevTools.pyw                    Developer utility (7 tabs). Runs independently.
│
├── app/
│   ├── app.py                      Root wiring class. Assembles Data + Logic + UI.
│   ├── paths.py                    get_base_dir() / data_path() — works in scripts
│   │                               and PyInstaller frozen builds.
│   ├── version.py                  VERSION = "1.0.0", VERSION_LABEL = "v1.0.0".
│   ├── logger.py                   GameLogger — structured log to rotating file.
│   │
│   ├── data/                       Data-layer package.
│   │   ├── init/
│   │   │   ├── registry.py         DataRegistry — builds all loaders/managers once.
│   │   │   ├── engine_factory.py   Creates Engine with a DataRegistry.
│   │   │   └── profile_selector.py ProfileSelectorFrame (embedded) + ProfileSelector
│   │   │                           shim. No Toplevel; uses root.wait_variable().
│   │   ├── loaders/
│   │   │   ├── config_loader.py    Loads prices, services, locations, dungeon config,
│   │   │   │                       room templates, player defaults, themes.
│   │   │   ├── item_loader.py      Loads data/dungeon/items/items.json.
│   │   │   ├── enemy_loader.py     Loads data/dungeon/enemies/enemies.json.
│   │   │   └── lore_loader.py      On-demand lore loading with in-memory cache.
│   │   └── managers/
│   │       ├── profile_mgr.py      ProfileMgr — read/write/delete profile files.
│   │       ├── dungeon_gen.py      DungeonGen — procedural room graph generator.
│   │       └── location_mgr.py     LocationMgr — resolves current location service.
│   │
│   ├── logic/                      Logic-layer package.
│   │   ├── action_types.py         ActionContext (frozen dataclass) and ActionResult.
│   │   ├── resolver_registry.py    Auto-scans app/logic/resolvers/ at startup.
│   │   ├── dispatcher.py           ActionDispatcher — load_actions() + dispatch().
│   │   │
│   │   ├── resolvers/              One .py file per resolver. Each exports resolve(ctx).
│   │   │   ├── add_gold.py         Add gold to player state.
│   │   │   ├── remove_gold.py      Remove gold (with floor check).
│   │   │   ├── add_item.py         Add item to inventory.
│   │   │   ├── remove_item.py      Remove item from inventory.
│   │   │   ├── heal_player.py      Heal player by quantity (capped at max_hp).
│   │   │   ├── equip_item.py       Equip weapon or armor; return old item to inventory.
│   │   │   ├── tick_buffs.py       Decrement turn-based buff durations; expire finished.
│   │   │   ├── combat/
│   │   │   │   ├── attack.py       Player attack round: damage, enemy counter, loot chain.
│   │   │   │   ├── award_loot.py   Roll loot_table and dispatch add_item sub-actions.
│   │   │   │   └── flee.py         Combat flee: mark fled, clear combat session.
│   │   │   ├── dungeon/
│   │   │   │   ├── enter_combat.py Build initial combat state dict.
│   │   │   │   ├── flee.py         Dungeon flee: expire one_run buffs, clear dungeon.
│   │   │   │   ├── next_room.py    Advance to next dungeon room.
│   │   │   │   └── take_item.py    Pick up item from current room floor.
│   │   │   ├── fishing/
│   │   │   │   ├── cast_line.py    Stub: set fishing_active flag.
│   │   │   │   └── fishing_tick.py Stub: resolve catch after tick (v1.1.0).
│   │   │   ├── inventory/
│   │   │   │   ├── unequip.py      Unequip item, return to inventory.
│   │   │   │   └── use_item.py     Apply consumable effect (heal, buff).
│   │   │   ├── location/
│   │   │   │   ├── advance_year.py Year rollover: tax check, exile if unpaid.
│   │   │   │   ├── bath.py         Public bath: heal + Refreshed buff.
│   │   │   │   ├── enter_dungeon.py Generate new dungeon via DungeonGen.
│   │   │   │   ├── fish.py         Instant fish catch (full loop in v1.1.0).
│   │   │   │   ├── hear_rumors.py  Draw random lore entry for current location.
│   │   │   │   ├── pay_taxes.py    Deduct tax cost, set tax_paid = True.
│   │   │   │   ├── repair.py       Repair weapon or armor at cost per durability point.
│   │   │   │   ├── rest.py         Tavern rest: restore full HP.
│   │   │   │   └── view_debt.py    Show current year tax debt.
│   │   │   ├── navigation/
│   │   │   │   └── go.py           All go_* actions: set current_location_id.
│   │   │   └── shop/
│   │   │       ├── buy.py          Validate shop_inventory, deduct gold, add item.
│   │   │       └── sell.py         Validate inventory + unequipped, award sell price.
│   │   │
│   │   ├── simple/                 ~25 atomic pure functions; no class, no side effects.
│   │   │   ├── add_gold.py         add_gold(ps, amount) → ps
│   │   │   ├── remove_gold.py      remove_gold(ps, amount) → ps
│   │   │   ├── add_item.py         add_item(ps, item_id) → ps
│   │   │   ├── remove_item.py      remove_item(ps, item_id) → ps
│   │   │   ├── heal_entity.py      heal_entity(ps, amount) → ps
│   │   │   ├── damage_entity.py    damage_entity(ps, amount) → ps
│   │   │   ├── apply_buff.py       apply_buff(ps, buff_dict) → ps
│   │   │   ├── remove_buff.py      remove_buff(ps, buff_id) → ps
│   │   │   ├── tick_buffs.py       tick_buffs(ps) → (ps, expired_names[])
│   │   │   ├── expire_run_buffs.py expire_run_buffs(ps) → ps
│   │   │   ├── apply_consumable.py parse effect string and apply heal/buff.
│   │   │   ├── decay_durability.py decay_durability(item, amount) → item
│   │   │   ├── equip_item.py       resolve_equip logic (slot detection).
│   │   │   ├── resolve_equip.py    Full equip flow: slot detection, swap.
│   │   │   ├── resolve_unequip.py  Full unequip flow: return item, clear slot.
│   │   │   ├── get_weapon_bonus.py Read damage bonus from equipped weapon.
│   │   │   ├── get_armor_defense.py Read defense from equipped armor.
│   │   │   ├── get_buff_bonus.py   Sum damage bonus from active buffs.
│   │   │   ├── get_buff_summary.py Return list of buff display strings.
│   │   │   ├── get_effective_max_hp.py max_hp + permanent buff bonus.
│   │   │   ├── increment_stat.py   increment_stat(ps, key, amount) → ps
│   │   │   ├── parse_effect.py     Parse item effect strings ("heal:8").
│   │   │   ├── set_location.py     set_location(ps, location_id) → ps
│   │   │   ├── set_year.py         set_year(ps, year) → ps
│   │   │   ├── is_alive.py         is_alive(ps) → bool
│   │   │   ├── hp_ratio.py         hp_ratio(ps) → float
│   │   │   └── entity_ai.py        Simple enemy AI for combat turn.
│   │   │
│   │   └── complex/                Stateful managers for multi-step operations.
│   │       ├── combat_mgr.py       CombatMgr — owns the combat session state.
│   │       ├── dungeon_mgr.py      DungeonMgr — room traversal, enemy placement.
│   │       ├── entity_mgr.py       EntityMgr — player + enemy stat lookups.
│   │       └── player_mgr.py       PlayerMgr — compound player-state operations.
│   │
│   │   └── core/                   Engine and orchestration.
│   │       ├── engine.py           Primary orchestrator. Routes all actions via AAD.
│   │       ├── state.py            State — single in-memory source of truth.
│   │       ├── year_clock.py       YearClock — counts actions; fires advance_year.
│   │       ├── router.py           Module-level functions: is_nav(), nav_target(), is_prefixed(),
│   │       │                       split_prefix(), is_city_action(). Classifies action strings.
│   │       └── view_builder.py     ViewBuilder — builds UI state dicts from game state.
│   │
│   ├── ui/                         UI-layer package.
│   │   ├── core/
│   │   │   ├── window.py           MainWindow — sidebar, content frame, message strip,
│   │   │   │                       inline confirm bar. post_message() / show_confirm().
│   │   │   ├── game_actions.py     GameActions — routes widget callbacks to engine.
│   │   │   └── profile_actions.py  ProfileActions — save/load/new/quit via inline UI.
│   │   ├── complex/
│   │   │   ├── assembler.py        UIAssembler — build/cache/refresh view widgets.
│   │   │   └── coordinator.py      ViewCoordinator — show_view(), refresh_active_view().
│   │   └── simple/
│   │       ├── basic/
│   │       │   ├── text_display.py TextDisplay — scrollable read-only text widget.
│   │       │   ├── stat_bar.py     StatBar — label + value display (themed).
│   │       │   ├── menu_list.py    MenuList — scrollable button list.
│   │       │   ├── action_button.py ActionButton — themed action button.
│   │       │   ├── input_field.py  InputField — themed entry + submit button.
│   │       │   └── dialog_box.py   DialogBox — themed modal dialog widget.
│   │       ├── panels/
│   │       │   ├── player_panel.py Player stats sidebar (HP, gold, level, buffs).
│   │       │   ├── location_panel.py City location view with optional shop section.
│   │       │   ├── combat_panel.py Combat UI: HP bars, action buttons.
│   │       │   ├── inventory_panel.py Item list + detail + action buttons.
│   │       │   └── lore_panel.py   Lore/rumour display panel.
│   │       ├── style_manager.py    StyleManager — initialises all ttk styles from theme.
│   │       ├── theme.py            load_theme() — loads + merges themes.json.
│   │       ├── constants.py        _ThemeConstants proxy — runtime theme values.
│   │       ├── data_binder.py      DataBinder — maps state dicts to widget calls.
│   │       ├── layout_loader.py    load_layout() — reads data/ui/layouts/*.json.
│   │       ├── component_builder.py Builds widget trees from layout dicts.
│   │       ├── component_registry.py Maps component type strings to builder functions.
│   │       ├── menu.py             GameMenu — top menu bar (File: save/load/quit).
│   │       └── view_registry.py    ViewRegistry — get_or_build() / refresh() views.
│   │
│   ├── components/game_engine/     Legacy engine components (used by DevTools AuditRunner
│   │   ├── buff_system.py          and the old GameEngine). Kept for backward compat.
│   │   ├── combat_system.py
│   │   ├── dungeon_actions.py
│   │   ├── effect_resolver.py
│   │   ├── location_actions.py
│   │   ├── navigation.py
│   │   ├── state_manager.py
│   │   └── view_builder.py
│   │
│   ├── game_engine.py              Legacy GameEngine class — used by DevTools AuditRunner.
│   ├── dungeon_manager.py          Legacy DungeonManager — used by DevTools AuditRunner.
│   ├── location_manager.py         Legacy LocationManager — used by DevTools AuditRunner.
│   ├── data_loader.py              Legacy DataLoader — used by DevTools AuditRunner.
│   └── profile_manager.py          Legacy ProfileManager — used by DevTools AuditRunner.
│
├── data/
│   ├── actions/                    40 action JSON files — the AAD catalogue.
│   ├── city/
│   │   ├── locations.json          Location display metadata (id, name, description).
│   │   └── services.json           Location services: actions, shop_inventory, costs.
│   ├── dungeon/
│   │   ├── config.json             min_rooms, max_rooms, max_depth.
│   │   ├── enemies/enemies.json    12 enemies with full loot fields.
│   │   ├── items/items.json        24 items (weapons, armor, consumables, misc).
│   │   └── rooms/room_templates.json  Room type definitions.
│   ├── economy/
│   │   ├── prices.json             rest, bath, tax, repair_per_point, sell_price_multiplier.
│   │   └── inventory_templates.json  Named item bundles for future shop restocking.
│   ├── events/events.json          Event stubs for the v1.2.0 event system.
│   ├── fish_pool.json              Weighted catch pool for the fishing mini-loop.
│   ├── lore/                       12 lore JSON files, one per location.
│   ├── player/
│   │   ├── defaults.json           Starting player state (hp, gold, level, …).
│   │   └── profiles/               Player save files (<name>.json).
│   ├── schemas/action_schema.json  JSON Schema for validating action files.
│   └── ui/
│       ├── layouts/                5 layout JSON files (city, combat, dungeon, inventory, lore).
│       └── themes.json             Full colour + font theme, auto-created from defaults.
│
└── docs/                           All documentation (this file + 9 others).
```

---

## Active Action Dispatch (AAD)

### The Problem It Solves

Before v1.0.0, `engine.py` contained long `if/elif` chains for every possible action. Adding any new action required editing the engine. The AAD system removes all hardcoded action logic from the engine.

### How AAD Works

Every action is described in a small JSON file under `data/actions/`. Example:

```json
{
  "id":                   "take_bath",
  "resolver":             "location.bath",
  "cost":                 {"gold": 15},
  "effects": [
    {"type": "heal_player", "entity_id": "0", "quantity": 5}
  ],
  "context_requirements": ["current_location_id"],
  "description":          "Soak in the public bath."
}
```

At startup `ActionDispatcher.load_actions()` reads every JSON, validates that `id` and `resolver` are present, and checks the resolver against `ResolverRegistry`. Actions with missing or broken resolvers are skipped with a warning — the game continues.

### Full Dispatch Call Chain

```
UI widget click
  → GameActions.on_city_action("take_bath")
    → Engine.do_city_action("take_bath")
      → Engine._dispatch("take_bath")
        → ActionDispatcher.dispatch(
              action_id       = "take_bath",
              player_state    = {...},
              dungeon_state   = None,
              location_state  = {"actions": [...], "rest_cost": 10},
              context_overrides = {}
          )
            → builds ActionContext from merged state + overrides
            → ResolverRegistry.get("location.bath") → resolve callable
            → location/bath.resolve(ctx) → ActionResult
            → chain any dispatched_actions recursively
          ← ActionResult(new_player_state, messages=["You soak..."])
        ← applies new_player_state to State; logs messages
      ← (changed=True, "You soak...")
    ← window.post_message("You soak...")
    ← GameActions.refresh()
```

### ActionDispatcher.dispatch() — Full Signature

```python
def dispatch(
    self,
    action_id:         str,
    player_state:      Dict,
    dungeon_state:     Optional[Dict] = None,
    location_state:    Optional[Dict] = None,
    context_overrides: Optional[Dict] = None,
) -> ActionResult:
```

`context_overrides` is merged last and wins over all other sources. Used to inject `entity_id`, `quantity`, and `reference` for sub-actions.

### ResolverRegistry.get() — Full Signature

```python
def get(self, resolver_name: str) -> Optional[Callable[[ActionContext], ActionResult]]:
```

Returns the `resolve` callable from the matching module, or `None` if unavailable. Unavailable resolvers are recorded in `self._unavailable` at startup.

### Engine._dispatch() — Full Signature

```python
def _dispatch(
    self,
    action_id: str,
    overrides: Optional[Dict] = None,
) -> ActionResult:
```

Internal helper that reads current state from `self._state`, builds the `location_state` from `services.json`, and calls `self._dispatcher.dispatch(...)`.

---

## ActionContext

```python
@dataclass(frozen=True)
class ActionContext:
    player_state:   Dict           # copy of current player state dict
    dungeon_state:  Optional[Dict] # copy of current dungeon state, or None
    location_state: Optional[Dict] # current services.json entry for location
    entity_id:      str            # "0" = player; "e_<uuid>" = enemy instance (future)
    quantity:       int            # gold cost, heal amount, etc.
    reference:      Any            # item_id, buff dict, slot name, location_id, …
    action_id:      str            # the action being dispatched
    data_registry:  Any            # read-only DataRegistry for lookups
```

**Rule:** resolvers must never mutate `ctx.player_state` directly. Always `ps = dict(ctx.player_state)` first.

---

## ActionResult

```python
@dataclass
class ActionResult:
    new_player_state:   Dict
    new_dungeon_state:  Optional[Dict]
    messages:           List[str]
    dispatched_actions: List[Tuple[str, Dict]]  # (action_id, context_overrides)
```

Sub-actions in `dispatched_actions` are chained recursively by `ActionDispatcher.dispatch()` after the main resolver returns. Each sub-action receives the *updated* player state from the previous step.

---

## ResolverRegistry Auto-Discovery

`app/logic/resolver_registry.py` scans `app/logic/resolvers/` recursively at startup. Any `.py` file that is not an `__init__` and exports a top-level `resolve` callable is registered. The resolver name is the file's dotted path relative to `resolvers/`:

```
resolvers/location/bath.py    →  "location.bath"
resolvers/combat/attack.py    →  "combat.attack"
resolvers/heal_player.py      →  "heal_player"
```

No manual registration is ever required. Adding a new resolver is a single file drop.

---

## State Management

`app/logic/core/state.py` (`State`) holds two dicts in memory:
- `_player` — the full player state (hp, gold, inventory, buffs, year, …)
- `_dungeon` — the current dungeon graph, or `None` when in the city

The dispatcher never writes to disk. `ProfileMgr.save()` is the only path to the filesystem. State is immutable from the resolver's perspective — every resolver receives a copy and returns a new copy.

---

## Year Clock

`YearClock` (`app/logic/core/year_clock.py`) counts non-navigation actions. Every 30 actions it signals the engine to `_dispatch("advance_year")`. The `location.advance_year` resolver:
1. Checks `player_state["tax_paid"]`.
2. If paid: increments year, resets `tax_paid = False`.
3. If unpaid: returns exile message → engine deletes profile, resets state.

---

## UI Architecture

```
App.__init__()
  ├── DataRegistry          — builds all loaders/managers once
  ├── ProfileSelectorFrame  — embedded in root window, blocks via wait_variable()
  ├── EngineFactory.create()— instantiates Engine with DataRegistry
  ├── MainWindow            — sidebar + content_frame + message strip + confirm bar
  ├── UIAssembler           — builds/caches view widgets in content_frame
  ├── ViewCoordinator       — show_view(), refresh_active_view()
  ├── GameActions           — routes callbacks → engine → post_message()
  └── ProfileActions        — save/load/new/quit → inline selector overlay
```

`UIAssembler.get_or_build_view(view_name, state)` creates a view widget on first call and caches it. `refresh_view(view_name, state)` calls `DataBinder.bind(state, widget)` to update all bound sub-widgets without recreating the tree.

View layout is defined in `data/ui/layouts/<view_name>.json`. `layout_loader.load_layout()` reads these files using `data_path()`, so they resolve correctly in both script and frozen `.exe` modes.

---

## Path Resolution

`app/paths.py` provides two public functions used by every loader:

```python
def get_base_dir() -> Path:
    # Frozen (PyInstaller): Path(sys.executable).parent
    # Script:               Path(__file__).parent.parent  (project root)

def data_path(*parts: str) -> Path:
    return get_base_dir() / "data" / Path(*parts)
```

Every data loader and the `ActionDispatcher` use `data_path()` instead of bare relative strings, ensuring the game finds its data folder whether run as `python main.pyw` or as a compiled `.exe`.

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        UI Layer                              │
│  MainWindow ← GameActions ← ViewCoordinator ← UIAssembler   │
│       ↓ post_message()          ↑ get_view_state()           │
│       ↓ callbacks               │                            │
└───────┼─────────────────────────┼────────────────────────────┘
        │ on_city_action()        │
        ↓                         │
┌─────────────────────────────────────────────────────────────┐
│                      Logic Layer                             │
│  Engine._dispatch() → ActionDispatcher.dispatch()            │
│          ↓                      ↓                            │
│    ResolverRegistry         ActionContext                    │
│          ↓                      ↓                            │
│    resolver.resolve(ctx) → ActionResult                     │
│          ↓                                                   │
│    State.set_player() / State.set_dungeon()                  │
└───────┼──────────────────────────────────────────────────────┘
        │ data_path() reads
        ↓
┌─────────────────────────────────────────────────────────────┐
│                       Data Layer                             │
│  data/actions/*.json   data/dungeon/   data/city/           │
│  data/player/profiles/ data/ui/        data/economy/        │
└─────────────────────────────────────────────────────────────┘
```
