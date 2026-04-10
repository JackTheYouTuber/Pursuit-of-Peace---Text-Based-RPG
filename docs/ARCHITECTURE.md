# Architecture — Pursuit of Peace

## Overview

The project follows a layered MVC-adjacent architecture with a data-driven UI system. Game logic, state management, UI assembly, and data loading are cleanly separated into distinct modules. All game data lives in JSON files under `data/`; no content is hardcoded in Python source.

---

## Directory Structure

```
Pursuit of Peace/
│
├── main.pyw                        Entry point. Creates GameLogger, runs App.
├── DevTools.pyw                    Developer utilities: Pycache Cleaner, Audit Tool, Build Tool.
│
├── app/
│   ├── app.py                      Root application class. Wires all subsystems together.
│   ├── version.py                  VERSION constant and CHANGELOG dict.
│   │
│   ├── data_loader.py              Loads and caches all JSON data files at startup.
│   ├── dungeon_manager.py          Generates dungeon runs; manages room traversal.
│   ├── location_manager.py         Manages city navigation; exposes location metadata.
│   ├── profile_manager.py          Reads/writes/deletes player profiles from disk.
│   ├── game_engine.py              Orchestrator. Delegates to component subsystems.
│   ├── ui_assembler.py             Thin re-export of app.ui.assembler.UIAssembler.
│   ├── view_coordinator.py         Switches and refreshes active views.
│   ├── logger.py                   Structured session logger.
│   │
│   ├── init/
│   │   ├── engine_factory.py       Constructs GameEngine with all dependencies.
│   │   ├── profile_selector.py     Modal dialog for profile selection at startup.
│   │   └── ui_factory.py           Stub factory (reserved for future use).
│   │
│   ├── controllers/
│   │   ├── game_actions.py         Handles UI callbacks: city, dungeon, combat, inventory.
│   │   └── profile_actions.py      Handles File menu: save, load, new game, quit.
│   │
│   ├── components/
│   │   └── game_engine/
│   │       ├── combat_system.py    Combat state machine. Attack/flee, equipment scaling,
│   │       │                       durability decay, loot/gold awards on victory.
│   │       ├── dungeon_actions.py  Take-item, next-room, exit-dungeon actions.
│   │       ├── location_actions.py Rest, bath, fishing, tax, equip, repair, buy, sell.
│   │       ├── effect_resolver.py  Parses item effect strings; applies heals and buffs.
│   │       ├── buff_system.py      Manages active buffs: tick, expire, stat bonus queries.
│   │       ├── navigation.py       Player movement between city locations.
│   │       ├── state_manager.py    Holds and updates player and dungeon state.
│   │       └── view_builder.py     Constructs state dicts consumed by the UI layer.
│   │
│   └── ui/
│       ├── assembler.py            Data-driven view builder; reads layout JSON files.
│       ├── component_builder.py    Instantiates widget trees from layout descriptors.
│       ├── component_registry.py   Maps component type strings to widget classes.
│       ├── data_binder.py          Binds state dict paths to widget update methods.
│       ├── layout_loader.py        Reads and validates layout JSON files.
│       ├── main_window.py          Sidebar + content frame layout.
│       ├── menu.py                 Tkinter menubar (File menu).
│       ├── profile_dialogs.py      Profile selection dialog.
│       ├── style_manager.py        Applies ttk styles; exposes theme at runtime.
│       ├── theme.py                Loads theme JSON and resolves colour tokens.
│       ├── view_registry.py        Caches built view widgets; handles refresh.
│       ├── constants.py            Dynamic theme constant accessor (no hardcoded values).
│       │
│       └── components/
│           ├── basic/              Layer 1 widgets — zero project imports.
│           │   ├── text_display.py Scrollable read-only text area.
│           │   ├── menu_list.py    Clickable action-list widget.
│           │   ├── stat_bar.py     Label + value display row.
│           │   ├── action_button.py  Single styled button.
│           │   ├── dialog_box.py   Modal dialog helper.
│           │   └── input_field.py  Labelled entry field.
│           │
│           └── complex/            Layer 2 widgets — compose basic widgets.
│               ├── location_panel.py   TextDisplay + MenuList (city/dungeon views).
│               ├── combat_panel.py     Log display, enemy/player HP bars, action list.
│               ├── inventory_panel.py  Equipment summary with durability bars,
│               │                       item list, detail pane, Use/Equip/Sell buttons.
│               ├── lore_panel.py       Lore text display.
│               └── player_panel.py     HP, gold, level, gear (+dmg/+def with durability),
│                                       kill count, active effects sidebar panel.
│
├── data/
│   ├── city/
│   │   ├── locations.json          Location IDs, names, access conditions.
│   │   └── services.json           Per-location action lists and service config.
│   │
│   ├── dungeon/
│   │   ├── config.json             Min/max rooms, max depth per run.
│   │   ├── rooms/
│   │   │   └── room_templates.json Room type definitions (lore_key, has_enemy, has_item).
│   │   ├── enemies/
│   │   │   └── enemies.json        Enemy definitions: HP, damage range, depth range,
│   │   │                           gold_min/max, loot_chance, loot_count, loot_table.
│   │   └── items/
│   │       └── items.json          Item definitions: type, value, effect, source,
│   │                               stat_bonus (weapons/armour), durability (weapons/armour).
│   │
│   ├── economy/
│   │   ├── prices.json             Gold costs: rest, bath, tax, repair_per_point,
│   │   │                           sell_price_multiplier.
│   │   └── inventory_templates.json  (Reserved — not yet populated.)
│   │
│   ├── events/
│   │   └── events.json             (Reserved — Tier 5 event system, not yet populated.)
│   │
│   ├── lore/
│   │   └── *.json                  Per-location lore entries (description, ambient, rumor).
│   │
│   ├── player/
│   │   ├── defaults.json           Default player state for new profiles.
│   │   │                           Includes: hp, max_hp, gold, level, inventory,
│   │   │                           year, tax_paid, buffs, equipped_weapon,
│   │   │                           equipped_armor, kills, times_died.
│   │   └── profiles/               One JSON file per saved player profile.
│   │
│   └── ui/
│       ├── themes.json             Colour theme and font configuration.
│       └── layouts/                One JSON layout descriptor per view.
│           ├── city.json
│           ├── dungeon.json
│           ├── combat.json
│           ├── inventory.json
│           └── lore.json
│
├── docs/
│   ├── README.md                   Player-facing documentation.
│   ├── CONTRIBUTING.md             Developer guide: modding, tools, code style.
│   ├── ARCHITECTURE.md             This file.
│   ├── CHANGELOG.md                Full version history.
│   ├── ROADMAP.txt                 Feature tier plan with completion status.
│   ├── BUGFIXES.md                 Known bug resolutions.
│   ├── KNOWN_GAPS.md               Documented gaps not yet addressed.
│   ├── KNOWN_ISSUES.md             Open issues.
│   ├── DATA_SCHEMA.md              JSON field reference for modders.
│   └── LOGGER_FORMAT.txt           Log file format specification.
│
└── logs/
    └── session_*.log               Auto-created structured log per session.
```

---

## Data Flow

### Startup

```
main.pyw
  └─ App.__init__()
       ├─ DataLoader          — loads all JSON into memory
       ├─ ProfileManager      — lists profiles on disk
       ├─ ProfileSelector     — blocks until user picks/creates a profile
       ├─ MainWindow          — builds root Tkinter layout (sidebar + content)
       ├─ EngineFactory       — creates DungeonManager → LocationManager → GameEngine
       │                         (passes ProfileManager so engine can delete on death)
       ├─ UIAssembler         — data-driven view builder (reads layouts/*.json)
       ├─ ViewCoordinator     — manages which view is active
       ├─ GameActions         — wires UI callbacks to engine methods
       └─ ProfileActions      — wires File menu to profile save/load/new/quit
```

### Action Cycle (city example)

```
User clicks action button
  → MenuList._handle_select(action_id)
  → LocationPanel._handle_action(action_id)
  → UIAssembler callback → GameActions.on_location_action(action_id)
  → GameEngine.do_location_action(action_id)
       → LocationActions / Navigation (state mutation, returns new state)
       → StateManager.update_player(new_state)
  → ViewCoordinator.refresh_active_view()
  → UIAssembler.refresh_view(view_name, new_state)
  → Individual widgets updated via DataBinder bindings
```

### Inventory Action Cycle

```
User clicks item in inventory list
  → InventoryPanel._handle_select(item_id)
  → GameActions.on_inventory_select(item_id)
       → Builds detail text + action buttons (Use/Equip/Sell)
       → assembler.refresh_view("inventory", updated_state)

User clicks Use / Equip / Sell button
  → InventoryPanel._handle_action(action_id)   e.g. "use_item:item_bandage_01"
  → GameActions.on_inventory_action(action_id)
  → GameEngine.do_location_action(action_id)
       → LocationActions.use_item() / equip_item() / sell_item()
  → Inventory view refreshed, player panel updated
```

### Combat Cycle

```
enter_combat action
  → GameEngine.do_dungeon_action("enter_combat")
  → CombatSystem.start_combat(enemy, player_hp, equipped_weapon, equipped_armor)
  → Combat view shown

Each attack round
  → GameEngine.do_combat_action("attack", enemy)
  → CombatSystem.attack(base_damage + buff_bonus)
       → Player deals: base + weapon.stat_bonus.damage
       → Enemy deals: roll − armor.stat_bonus.defense  (min 1)
       → Weapon durability −1;  Armor durability −1
       → If either breaks: auto-unequip + log warning
  → BuffSystem.tick_turn_buffs()  — decrements turn-based buffs
  → On enemy death: _award_combat_rewards()
       → Gold from enemy.gold_min/gold_max
       → Loot drawn from enemy.loot_table with enemy.loot_chance probability

Player death
  → CombatSystem sets player_dead = True
  → GameEngine.end_combat(player_dead=True)
  → ProfileManager.delete_profile(current_profile)  — file deleted from disk
  → StateManager.init_player()  — in-memory state reset to defaults
```

### State Model

Player state is a plain Python `dict` held by `StateManager`. It is never mutated in place — all action methods receive a state dict, return a new dict, and the manager replaces its internal copy. Dungeon state follows the same pattern.

Key top-level fields:

| Field | Type | Description |
|---|---|---|
| `hp` / `max_hp` | int | Current and maximum health |
| `gold` | int | Current gold |
| `level` | int | Player level (cosmetic currently) |
| `inventory` | list[str] | Item IDs in the player's bag |
| `equipped_weapon` | dict\|null | `{item_id, item, current_durability, max_durability}` |
| `equipped_armor` | dict\|null | Same structure as weapon |
| `buffs` | list[dict] | Active buff objects with `id`, `stat_mods`, `duration` |
| `kills` | int | Total enemies defeated |
| `times_died` | int | Total deaths (profile not deleted on this field — it resets) |
| `year` | int | Current in-game year |
| `tax_paid` | bool | Whether tax has been paid this year |

---

## UI System

`UIAssembler` is a data-driven layout engine. Each view is described by a JSON file in `data/ui/layouts/`. The assembler reads the file, instantiates the correct widget class from its component registry, applies theme colours from `data/ui/themes.json`, connects data bindings (dot-path expressions like `"location.description"`), and caches the resulting widget tree. On refresh, `DataBinder` walks the bindings and calls the appropriate widget update methods.

### Dynamic Theming

All UI colours, fonts, and padding values are fetched at runtime from the active theme via `app.ui.constants`. The `constants` module uses a `__getattr__` delegator to a `_ThemeConstants` instance that reads from `StyleManager.get_theme()` on every access. Theme changes apply immediately without restarting.

```python
import app.ui.constants as const

label = tk.Label(self, bg=const.CARD_BG, fg=const.TEXT_FG, font=const.FONT_BODY)
```

---

## Key Design Decisions

- **No game logic in UI classes.** Widgets and panels only render data and emit action ID strings via callbacks. No engine state is read directly from within a widget.
- **No hardcoded content in Python.** All text, prices, item stats, enemy stats, location actions, buff definitions, and lore come from JSON. The engine is a rules interpreter; the data files are the game.
- **Immutable-style state transitions.** State dicts are copied at the top of every action method (`state = dict(player_state)`); the original is never mutated. This keeps state transitions traceable and testable without mocking.
- **Component layering.** Layer 1 widgets (`basic/`) have zero project imports. Layer 2 widgets (`complex/`) compose Layer 1 only. This prevents circular dependencies and keeps widgets portable.
- **Centralised logging.** All significant events flow through `GameLogger` with structured categories (`system`, `info`, `data`, `warn`, `error`). Never use `print()` in engine or UI code.
- **Parameterised action IDs.** Actions that require a target use a colon separator: `use_item:item_id`, `equip_item:item_id`, `sell_item:item_id`. The engine splits on `:` to extract parameters. This keeps the callback interface uniform — every action is a single string.
- **Death is permanent.** `ProfileManager.delete_profile()` is called on player death. The engine then resets to defaults in memory. There is no save-scumming path.
