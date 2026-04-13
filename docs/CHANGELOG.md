# Pursuit of Peace — Changelog

---

## v1.0.0-stable — Stability, DevTools & UI Improvements

Building on v1.0.0-alpha (the AAD rewrite), this release fixes all known critical bugs, adds significant DevTools functionality, improves the UI to eliminate popups, and produces a fully documented codebase.

### Bug Fixes
- **Step 1 — `do_combat_action` ValueError**: `AuditRunner._do_combat_action()` in DevTools was unpacking 3 values from a method that returns 4. Fixed the unpack to `ended, msg, _fled, _dead`.
- **Step 2 — PyInstaller "Unknown or unavailable action"**: All 14 data-loading files used bare relative paths (`"data/..."`) that break when the `.exe` runs from a different working directory. Created `app/paths.py` with `get_base_dir()` / `data_path()` that resolve correctly in both script and frozen modes. Updated all loaders, `ActionDispatcher`, `ProfileMgr`, and the UI assemblers.

### DevTools Improvements (Steps 3–4, 6–7)
- **Build Tool**: Added UPX compression toggle, target-architecture selector (x86_64/x86/default), custom output-folder field, debug-symbols toggle, StatBar progress indicator, and concurrent-build guard. New "BUILD BOTH" button produces both game and DevTools executables in a single operation, placing them in a versioned `Build Output (v1.0.0-stable)/` folder with the `data/` folder copied once.
- **Audit Tool export**: Added `get_log_content()` helper that handles both `TextDisplay` and raw `tk.Text` widgets correctly.
- **JSON Workshop tab**: Visual form-based editor for items, enemies, services, and actions. Browse, create, duplicate, delete, and save entries without writing raw JSON. Enemy form includes a loot-table sub-widget. Action resolver field is a live dropdown populated from `ResolverRegistry`.
- **File Auditor tab**: Scans the project for `__pycache__`, `.pyc`, backup files, empty Python files, and files never imported anywhere (full AST analysis). Checkbox selection with inline Yes/No confirmation for batch deletion.
- **Widget theming (Step 7)**: Replaced `tk.Frame`, `tk.Label`, `tk.Button`, and `tk.Entry` with `ttk` equivalents throughout DevTools, eliminating hardcoded colour strings and making all tabs consistent with the game's dark theme.

### UI Improvements (Step 5)
- **No more profile popups**: Startup profile selection and in-game load/new-game now use `ProfileSelectorFrame` — an embedded `tk.Frame` overlaid directly on the root window. New-profile naming and delete confirmation both happen inline; no `Toplevel`, no `simpledialog`.
- **Inline message log**: `MainWindow` now has a message strip at the bottom of the window. All game-event results (rest, buy, sell, combat) stream to this strip via `post_message()`. `messagebox.showinfo` has been eliminated from all game-action callbacks.
- **Inline quit confirmation**: Quit uses an inline Yes/No bar (`show_confirm()`) rather than `messagebox.askokcancel`.

### Dead Code Removal (Step 6)
- Deleted 12 unreachable Python files and 3 empty directories identified by static import analysis. Removed all `__pycache__` and `.pyc` files from the repository.

### Documentation (Step 8)
- `ARCHITECTURE.md` expanded with a complete file-by-file breakdown, full data-flow diagram, exact method signatures for `ActionDispatcher.dispatch()`, `ResolverRegistry.get()`, and `Engine._dispatch()`.
- `CONTRIBUTING.md` expanded with full resolver example including buff awarding, complete field tables for items/enemies/locations, versioning scheme, debug mode, and headless audit instructions.
- `DATA_SCHEMA.md` rewritten with exhaustive field tables, constraints, and examples for all 13 data file types including buff schema, loot schema, and effect string formats.
- `README.md` updated to reflect all v1.0.0-stable features and link to new doc files.
- Four new documentation files added: `UI_SYSTEM.md`, `BUILD_PROCESS.md`, `DEVTOOLS_GUIDE.md`, `MIGRATION_GUIDE.md`.

---

## v1.0.0-alpha — Active Action Dispatch & Tier 4 Complete

### Architecture — Active Action Dispatch (AAD)
- **ActionContext / ActionResult** — frozen and mutable dataclasses forming the resolver contract.
- **ResolverRegistry** — auto-discovers all resolver modules at startup. No manual registration.
- **ActionDispatcher** — reads all `data/actions/*.json`, validates, maps, and executes dispatch chains including recursive sub-actions.
- **40 action JSON files** created under `data/actions/`.
- **30 resolver modules** — zero unavailable at startup.
- **Engine rewrite** — all city/shop/inventory/navigation actions route through `ActionDispatcher`.

### Tier 4 — Shop Economy
- `shop_inventory` arrays added to marketplace, alchemy hall, and blacksmiths street.
- `shop.buy` and `shop.sell` resolvers.
- Shop UI panel rendered automatically when `shop.items` is present in view state.

### Tier 4 — Data-Driven Loot
- All 12 enemies have full `loot_table`, `loot_chance`, `loot_count`, `gold_min`, `gold_max`.
- `combat.award_loot` resolver dispatches `add_item` and `add_gold` as sub-actions.

### Developer Tools
- Validate Actions tab.
- Generate Resolver tab.
- `--debug` flag for verbose dispatcher output.

---

## v0.9.0 — Tier 2 & Tier 3 Complete

- `EffectResolver` — parses item effect strings; applies heal, damage-buff, debuff-removal.
- `BuffSystem` — `turns`, `one_run`, `permanent` buff durations.
- Equipment slots (`equipped_weapon`, `equipped_armor`), durability decay, auto-unequip on break.
- Blacksmith repair action.
- Inventory panel with equipment summary and durability bars.

---

## v0.7.0 — Tier 1 Complete

- Enemy counter-attack.
- Permanent death (profile deleted on player death).
- Year rollover + exile for unpaid taxes.
- Data-driven combat gold and loot rewards.
- Kill counter tracked and displayed.

### Bug Fixes — Step 9 (Static Analysis & Audit)

- **BUG-019 — `shop.sell` crash when item equipped** (`shop/sell.py`): `eq.get("item_id")` was called unconditionally on the equipment slot value. Any non-dict value (legacy string format, direct test assignment) caused `AttributeError: 'str' object has no attribute 'get'`. Added `_equipped_id()` helper handling both dict and string slot formats.
- **BUG-020 — Equipment simples crash on non-dict slots** (`get_weapon_bonus.py`, `get_armor_defense.py`, `resolve_unequip.py`): All three simples called `.get()` on the raw slot value without type-checking. Fixed with `isinstance(ew, dict)` guards throughout.
- **BUG-021 — `view_builder.py` crashes rendering equipped items** (`view_builder.py`): `build_inventory`, `build_combat`, and `build_player_panel` all assumed equipment slots are dicts. Added `_as_equip_dict()` helper; all four equipment-reading sites now use it.
- **BUG-022 — Spurious `f` prefix on two string literals** (`attack.py`, `buy.py`): `f"⚠ Your weapon has broken!"` and `f"That item is not available here."` had unused `f` prefixes. Removed.
- **BUG-023 — 31 files with unused imports** (pyflakes): Removed unused `typing` symbols, `StyleManager` imports, `import shutil`, `import random`, `import tkinter as tk`, and superseded module imports across 31 files. No behaviour changes.
- **BUG-024 — Dead local variables in `ComponentBuilder`**: `theme` and `global_theme` were computed but never read in `build()`. Removed from both `app/ui/component_builder.py` and `app/ui/simple/component_builder.py`.

### Audit Results
- **10,000 steps × 5 seeds** on the AAD engine (actual game): all passed, zero crashes.
- **5,000 steps × 2 seeds** on the legacy GameEngine (DevTools AuditRunner): all passed, zero crashes.
- **7 targeted edge-case tests** (year-rollover exile, player death, duplicate buy, sell-equipped-item, sell-with-legacy-string-slot, dungeon flee, view_builder with malformed slot): all passed after fixes.
