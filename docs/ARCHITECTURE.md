# Architecture — Pursuit of Peace

## Overview

The project follows a layered MVC-adjacent architecture with a data-driven UI system. Game logic, state management, UI assembly, and data loading are cleanly separated into distinct modules. All game data lives in JSON files under `data/`; no content is hardcoded in Python source.

---

## Directory Structure

```
Pursuit of Peace - Text Based RPG/
│
├── main.pyw                        Entry point. Creates GameLogger, runs App.
├── audit.pyw                       Standalone log/audit viewer (separate tool).
│
├── app/
│   ├── app.py                      Root application class. Wires all subsystems together.
│   │
│   ├── data_loader.py              Loads and caches all JSON data files at startup.
│   ├── dungeon_manager.py          Generates dungeon runs; manages room traversal.
│   ├── location_manager.py         Manages city navigation; exposes location metadata.
│   ├── profile_manager.py          Reads/writes player profiles from disk.
│   ├── game_engine.py              Orchestrator. Delegates to component subsystems.
│   ├── ui_assembler.py             Data-driven UI builder. Reads layout JSON files.
│   ├── view_coordinator.py         Switches and refreshes active views.
│   ├── logger.py                   Structured session logger.
│   │
│   ├── init/
│   │   ├── engine_factory.py       Constructs GameEngine with all dependencies.
│   │   ├── profile_selector.py     Modal dialog for profile selection at startup.
│   │   └── ui_factory.py           Stub factory (not currently used by App).
│   │
│   ├── controllers/
│   │   ├── game_actions.py         Handles UI action callbacks (city, dungeon, combat).
│   │   └── profile_actions.py      Handles menu-level profile actions (save, load, new, quit).
│   │
│   ├── components/
│   │   └── game_engine/
│   │       ├── combat_system.py    Combat state machine and attack/flee logic.
│   │       ├── dungeon_actions.py  Take-item, next-room, exit-dungeon actions.
│   │       ├── location_actions.py Rest, rumor, bath, fishing, tax, dungeon-entry actions.
│   │       ├── navigation.py       Player movement between city locations.
│   │       ├── state_manager.py    Holds and mutates player + dungeon state.
│   │       └── view_builder.py     Constructs state dicts consumed by the UI.
│   │
│   └── ui/
│       ├── main_window.py          Sidebar + content frame layout.
│       ├── menu.py                 Tkinter menubar (File menu).
│       ├── profile_dialogs.py      Alternative profile dialog implementation (unused in main flow).
│       │
│       └── components/
│           ├── basic/              Layer 1 widgets — no project imports.
│           │   ├── text_display.py Scrollable read-only text widget.
│           │   ├── menu_list.py    Clickable action-list widget.
│           │   ├── stat_bar.py     Label + value display row.
│           │   ├── action_button.py Single styled button.
│           │   ├── dialog_box.py   Modal dialog helper.
│           │   └── input_field.py  Labelled entry field.
│           │
│           └── complex/            Layer 2 widgets — compose basic widgets.
│               ├── location_panel.py  TextDisplay + MenuList (city/dungeon views).
│               ├── combat_panel.py    Log + enemy HP bar + action list.
│               ├── inventory_panel.py Item list + detail pane.
│               ├── lore_panel.py      Lore text display.
│               └── player_panel.py   HP / gold / level sidebar panel.
│
├── data/
│   ├── city/
│   │   ├── locations.json          Location IDs, names, access conditions.
│   │   └── services.json           Per-location action lists and service config.
│   │
│   ├── dungeon/
│   │   ├── config.json             Min/max rooms, max depth.
│   │   ├── rooms/room_templates.json  Room type definitions (has_enemy, has_item, lore_key).
│   │   ├── enemies/enemies.json    Enemy definitions (HP, damage range, depth range, loot).
│   │   └── items/items.json        Item definitions (type, value, effect, source).
│   │
│   ├── economy/
│   │   ├── prices.json             Gold costs for services (rest, bath, tax, repair).
│   │   └── inventory_templates.json  (Stub — not yet populated.)
│   │
│   ├── events/
│   │   └── events.json             (Stub — not yet populated.)
│   │
│   ├── lore/
│   │   └── *.json                  Per-location lore entries (description, ambient, rumor).
│   │
│   ├── player/
│   │   ├── defaults.json           Default player state for new profiles.
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
       → LocationActions or Navigation (state mutation)
       → StateManager.update_player(new_state)
  → ViewCoordinator.refresh_active_view()
  → UIAssembler.refresh_view(view_name, new_state)
  → Individual widgets updated via bindings
```

### State Model

Player state is a plain Python `dict` held by `StateManager`. It is never mutated in place — all action methods receive a state dict, return a new dict, and the manager replaces its internal copy. Dungeon state follows the same pattern.

---

## UI System

The `UIAssembler` is a data‑driven layout engine. Each view is described by a JSON file in `data/ui/layouts/`. The assembler reads the file, instantiates the correct widget class from its component registry, applies theme colours from `data/ui/themes.json`, connects data bindings (dot‑path expressions like `"location.description"`), and caches the resulting widget tree.

### Dynamic Theming

All UI colours, fonts, and padding values are fetched **at runtime** from the active theme via `app.ui.constants`. The `constants` module uses a `__getattr__` delegator to a `_ThemeConstants` instance, which reads values from `StyleManager.get_theme()` on every access. This ensures that theme changes are applied immediately without restarting the game.

**Example usage inside a component:**

```
import app.ui.constants as const

label = tk.Label(self, bg=const.CARD_BG, fg=const.TEXT_FG, font=const.FONT_BODY)
```

---

## Key Design Decisions

- **No game logic in UI classes.** Widgets and panels only render data and emit action IDs via callbacks.
- **No hardcoded content in Python.** All text, prices, item stats, enemy stats, location actions, and lore come from JSON.
- **Immutable-style state transitions.** State dicts are copied before modification; the original is never mutated.
- **Component layering.** Layer 1 widgets (`basic/`) have zero project imports. Layer 2 widgets (`complex/`) compose Layer 1 only.
- **Centralised logging.** All significant events flow through `GameLogger` with structured categories (`system`, `info`, `data`, `warn`, `error`).
