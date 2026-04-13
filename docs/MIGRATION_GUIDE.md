# Migration Guide — v1.0.0-alpha → v1.0.0-stable

This document covers changes that may affect saved profiles, modded data files, or custom resolvers when upgrading from the original v1.0.0-alpha release to v1.0.0-stable.

---

## Profile Files — No Action Required

Player profile files (`data/player/profiles/<n>.json`) are fully forward-compatible. The `player_state` schema has not changed between alpha and stable. Your saves will load without modification.

---

## Modded Action JSON Files

**Stable is fully backward-compatible.** Existing action JSON files with only `id` and `resolver` fields continue to work. Optional fields (`cost`, `effects`, `reference`, `description`) remain optional.

One behavioural change: the `ActionDispatcher` now logs a `WARNING` (not an error) when a resolver is unavailable at startup, and the game continues without that action. Previously, a missing resolver could cause a silent no-op without any log entry.

---

## Custom Resolver Modules

No changes to the resolver interface. `resolve(ctx: ActionContext) -> ActionResult` is identical. The `ActionContext` dataclass fields are the same. `ActionResult` fields are the same.

If you have custom resolvers under `app/logic/resolvers/`, they will be auto-discovered as before.

---

## Data Path Changes (Critical for `.exe` Distributions)

If you previously worked around the PyInstaller path bug by setting the working directory before launching the `.exe`, that workaround is no longer needed. `app/paths.py` now handles path resolution automatically in both script and frozen modes.

If you have any **custom scripts** that imported data by doing:

```python
# old pattern (breaks in .exe)
with open("data/dungeon/items/items.json") as f:
    ...
```

Update them to use the path resolver:

```python
# new pattern (works everywhere)
from app.paths import data_path
with open(data_path("dungeon", "items", "items.json")) as f:
    ...
```

---

## Removed Files

The following files were removed in the cleanup pass. If you imported from them in a custom script, update your imports:

| Removed | Replacement |
|---------|-------------|
| `app/controllers/game_actions.py` | `app/ui/core/game_actions.py` |
| `app/controllers/profile_actions.py` | `app/ui/core/profile_actions.py` |
| `app/init/profile_selector.py` | `app/data/init/profile_selector.py` |
| `app/init/engine_factory.py` | `app/data/init/engine_factory.py` |
| `app/ui/profile_dialogs.py` | `app/data/init/profile_selector.ProfileSelectorFrame` |
| `app/ui/simple/profile_dialogs.py` | (same as above) |
| `app/ui/constants.py` | `app/ui/simple/constants.py` |
| `app/ui_assembler.py` | `app/ui/complex/assembler.py` |
| `app/view_coordinator.py` | `app/ui/complex/coordinator.py` |

---

## Profile Selector Behaviour Change

The startup profile selector no longer opens a separate `Toplevel` window. It now fills the root window directly using `ProfileSelectorFrame`. If you had any code that called `ProfileSelector.select_or_create(root, ...)` and relied on the dialog being a separate window (e.g. to position it), that code will still work via the backward-compatible shim — it just won't open a separate window any more.

---

## Game Event Messages

In alpha, some game actions called `messagebox.showinfo()` to display results. In stable, all informational messages are routed to `MainWindow.post_message()` and shown in the inline message strip at the bottom of the window. `messagebox` is now only used for errors and the game-over warning.

If you have a custom UI that wraps `GameActions` and relied on intercepting `messagebox.showinfo` calls, update it to hook into `MainWindow.post_message()` instead.

---

## services.json and locations.json

No schema changes. Existing files from alpha are fully compatible.

---

## Summary

For most users (players and data modders), upgrading is transparent — copy your `data/player/profiles/` folder into the new release and play. For Python modders who imported from the old module paths, update your imports using the table above.
