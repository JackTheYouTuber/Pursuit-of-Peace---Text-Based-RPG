# UI System — Pursuit of Peace  v1.0.0-stable

This document describes the UI architecture: how views are built, how data is bound to widgets, and how to add a new view or panel.

---

## Architecture Overview

```
App
├── MainWindow          Sidebar + content_frame + message strip + confirm bar
├── UIAssembler         Builds and caches view widgets inside content_frame
├── ViewCoordinator     show_view() / refresh_active_view()
├── GameActions         Widget callbacks → Engine → post_message()
└── ProfileActions      Profile operations → inline overlay
```

The content area is a single `ttk.Frame` (`content_frame`) in the centre of the window. All game views are built as children of this frame, stacked on top of each other. `widget.tkraise()` brings the active view to the front without destroying others.

---

## MainWindow (`app/ui/core/window.py`)

`MainWindow` manages the top-level layout:

- **Column 0** — Sidebar (`ttk.Frame`, 200px wide): player panel + nav buttons.
- **Column 1, row 0** — Content frame (`ttk.Frame`, expands to fill): game views stacked here.
- **Column 1, row 1** — Message strip (80px tall `tk.Frame`): inline `TextDisplay` log of game events.

### Key Methods

| Method | Description |
|--------|-------------|
| `get_content_frame()` | Returns the content `ttk.Frame` where views are gridded. |
| `add_nav_button(key, label, command)` | Adds a nav button to the sidebar. |
| `highlight_nav_button(key, active)` | Applies `Active.TButton` style to the active nav button. |
| `set_player_panel_data(data, logger)` | Updates the `PlayerPanel` with a new state dict. |
| `post_message(msg)` | Appends a game-event message to the inline message strip. |
| `show_confirm(prompt, on_yes, on_no)` | Shows an inline Yes/No bar between content and message strip. |
| `hide_confirm()` | Hides the confirmation bar. |

---

## UIAssembler (`app/ui/complex/assembler.py`)

`UIAssembler` builds, caches, and refreshes view widgets.

```python
assembler = UIAssembler(
    root        = window.get_content_frame(),
    callbacks   = {"location_action": fn, "combat_action": fn, ...},
    logger      = logger,
)
```

### Key Methods

| Method | Description |
|--------|-------------|
| `get_or_build_view(view_name, state)` | Returns the cached widget, or builds it from the layout JSON. |
| `refresh_view(view_name, state)` | Calls `DataBinder.bind(state, widget)` to update bound sub-widgets. |
| `destroy_view(view_name)` | Removes a view from cache and destroys its widget. |

---

## ViewCoordinator (`app/ui/complex/coordinator.py`)

`ViewCoordinator` is the public API for switching views.

```python
coordinator.show_view("city")       # switch to city view
coordinator.refresh_active_view()   # refresh whatever is currently shown
coordinator.refresh_view("combat")  # refresh a specific view without switching
```

`show_view()` calls `get_view_state(view_name)` on the engine, then calls `assembler.get_or_build_view()`, then `widget.tkraise()`.

---

## View State Dicts

Every view is driven by a state dict returned by `engine.get_view_state(view_name)`. The structure must match what the layout JSON and `DataBinder` expect.

**City view state example:**
```python
{
  "city": {
    "location_name": "The Rusty Flagon",
    "description":   "A dimly lit tavern.",
    "actions": [
      {"id": "rest",       "label": "Rest (10g)"},
      {"id": "hear_rumors","label": "Hear Rumors"},
      {"id": "go_city",    "label": "Back to City"}
    ],
    "shop": {"items": [...]},   # only present when location has shop_inventory
  },
  "player": {
    "hp": 18, "max_hp": 20, "gold": 120, "level": 1,
    "equipped_weapon": "Crude Knife", "equipped_armor": null,
    "buffs": ["Refreshed (one_run)"]
  },
  "lore": [
    {"type": "rumour", "text": "...", "source": "A merchant"}
  ]
}
```

---

## Layout Files (`data/ui/layouts/`)

Each view has a layout JSON that `ComponentBuilder` uses to construct the widget tree.

```json
{
  "type": "panel_grid",
  "panels": [
    {"id": "location", "component": "LocationPanel", "source": "city"},
    {"id": "player",   "component": "PlayerPanel",   "source": "player"},
    {"id": "lore",     "component": "LorePanel",     "source": "lore"}
  ]
}
```

The `source` key tells `DataBinder` which sub-dict of the view state to pass to each panel when refreshing.

Five layout files exist: `city.json`, `combat.json`, `dungeon.json`, `inventory.json`, `lore.json`.

---

## DataBinder (`app/ui/simple/data_binder.py`)

`DataBinder` maps view state keys to widget update calls. On `bind(state, root_widget)` it iterates the registered bindings and calls the appropriate setter on each sub-widget.

---

## Theme and Styling

`StyleManager.init_styles(root, theme_dict)` configures all `ttk` styles at startup from `data/ui/themes.json`. After this call, all `ttk.Frame`, `ttk.Label`, `ttk.Button`, and `ttk.Entry` widgets automatically use the dark theme colours without any explicit `bg`/`fg` arguments.

Widgets that need custom colours (canvas inner frames, accent labels, confirmation bars) use raw `tk.*` widgets with explicit colour arguments. This is the intended pattern.

---

## How to Add a New View

**1. Create a layout file** `data/ui/layouts/<view_name>.json`:

```json
{
  "type": "panel_grid",
  "panels": [
    {"id": "my_panel", "component": "LocationPanel", "source": "my_data"}
  ]
}
```

**2. Add a `get_view_state` case** in `app/logic/core/engine.py`:

```python
if view_name == "my_view":
    return {"my_data": {...}, "player": self._view.build_player(ps)}
```

**3. Add a nav button** in `app/app.py`:

```python
self._window.add_nav_button("my_view", "  My View", lambda: self._show("my_view"))
```

**4. Wire the callback** in `app/app.py`:

```python
self._assembler._callbacks["my_action"] = self._game.on_city_action
```

That is all. `UIAssembler.get_or_build_view("my_view", state)` reads the layout, builds the widget tree, and caches it automatically.

---

## How to Add a New Panel

**1. Create the panel class** in `app/ui/simple/panels/<name>_panel.py`:

```python
import tkinter as tk
from tkinter import ttk

class MyPanel(ttk.Frame):
    def __init__(self, parent, data: dict, callbacks: dict, logger=None):
        super().__init__(parent)
        self._callbacks = callbacks
        self._build(data)

    def _build(self, data: dict):
        ttk.Label(self, text=data.get("title", "")).pack()

    def update(self, data: dict):
        # called by DataBinder on refresh
        ...
```

**2. Register the component** in `app/ui/simple/component_registry.py`:

```python
from app.ui.simple.panels.my_panel import MyPanel
_REGISTRY["MyPanel"] = MyPanel
```

**3. Use it in a layout file** by setting `"component": "MyPanel"`.

---

## Widgets (`app/ui/simple/basic/`)

| Class | Usage |
|-------|-------|
| `TextDisplay` | Scrollable read-only text area. `append(text)` / `set_content(text)` / `get_content()`. |
| `StatBar` | Label + value display. `set_value(v)` / `set_label(l)`. |
| `MenuList` | Scrollable list of buttons. Each fires a callback with the item ID. |
| `ActionButton` | Styled action button with tooltip support. |
| `InputField` | Entry + submit button; fires `on_submit(text)` callback. |
| `DialogBox` | Themed modal-style frame with title, body, and button row. |
