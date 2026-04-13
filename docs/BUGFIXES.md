# Bug Fix Log — Pursuit of Peace

All bugs identified and fixed during development. Listed by severity.

---

## Fixed in v1.0.0 (AAD Transition)

---

### BUG-010 — Hardcoded if/elif Action Chains (Architecture)

**File:** `app/game_engine.py` (pre-v1.0.0)
**Severity:** Architecture — made every new feature require engine edits

**Description:**
`do_location_action`, `do_dungeon_action`, and `do_combat_action` each contained long `if/elif` chains that matched action strings. Adding any new action required touching the engine directly. Broken resolver modules caused silent no-ops with no logging.

**Fix:**
All action dispatch now routes through `ActionDispatcher`. Actions are described in `data/actions/*.json`. Resolvers are auto-discovered by `ResolverRegistry`. If a resolver module is missing or broken at startup the action is marked unavailable and logged as a warning — the game continues without it. The engine contains zero action-string comparisons for dispatched actions.

---

### BUG-011 — Missing Simple Modules Referenced by PlayerMgr

**File:** `app/logic/complex/player_mgr.py`
**Severity:** Critical — ImportError on startup

**Description:**
`player_mgr.py` imported eight simple modules that did not exist: `remove_buff`, `remove_gold`, `remove_item`, `resolve_equip`, `resolve_unequip`, `set_location`, `set_year`, `tick_buffs`. The game would fail to start with `ModuleNotFoundError`.

**Fix:**
All eight modules created under `app/logic/simple/`. Each follows the single-responsibility pattern of the existing simples.

---

### BUG-012 — Shop Actions Were Stubs (Tier 4)

**File:** `data/city/services.json`, `app/logic/`
**Severity:** High — buy/sell had no implementation

**Description:**
`marketplace` and `alchemy_hall` listed `sell_item` in their `actions` arrays but had no `shop_inventory`, no resolver, and no transaction logic. Clicking sell would trigger a no-op or an unhandled action warning.

**Fix:**
- `shop_inventory` arrays added to marketplace, alchemy hall, and blacksmiths street in `services.json`.
- `shop.buy` resolver validates item is in `location_state["shop_inventory"]`, checks affordability, deducts gold, adds item.
- `shop.sell` resolver validates inventory ownership and unequipped status before awarding sell price.
- `LocationPanel` renders a collapsible shop section automatically whenever `shop.items` is present in state.

---

### BUG-013 — Buff tick_buffs Not Called Consistently

**File:** `app/logic/complex/combat_mgr.py`
**Severity:** Medium — turn-based buffs never expired

**Description:**
`tick_buffs` was imported but only called in some combat paths. Buffs with `duration: "turns"` could persist indefinitely.

**Fix:**
`tick_buffs` is called in `CombatMgr._resolve_player_action()` after every attack round for both the player and enemy. It is also dispatched via the AAD chain whenever the `tick_buffs` action is used directly.

---

### BUG-014 — advance_year Not Triggered via Dispatcher

**File:** `app/logic/core/engine.py`
**Severity:** Medium — year rollover was bypassing AAD

**Description:**
Year rollover called `PlayerMgr.year_rollover()` directly, bypassing the dispatcher and producing no `DATA` log event.

**Fix:**
`Engine._tick_year()` now calls `self._dispatch("advance_year")`. The `location.advance_year` resolver handles the tax check, exile logic, and year increment. Every rollover produces a `DATA` log event via the dispatcher.

---

## Fixed in Earlier Versions (Retained for Reference)

---

### BUG-001 — Double `end_combat()` Call (v0.7, Critical)
`GameActions.on_combat_action()` called `end_combat()` a second time after the engine had already called it internally. Removed the duplicate call.

### BUG-002 — Call to Non-Existent `_build_combat_state()` (v0.7, Critical)
Reference to a method that was renamed. Updated to use `get_view_state("combat")`.

### BUG-003 — `ProfileSelector` Root Leak (v0.8, High)
Temporary Tk root created inside `ProfileSelector` was not destroyed, leaving an orphaned window. Fixed by using `wm_withdraw` and proper destroy sequencing.

### BUG-004 — Inventory `sell_item` Not Routed (v0.8, High)
`on_inventory_action()` did not forward `sell_item:x` to `do_location_action()`. Fixed by routing all inventory actions through `do_city_action()`.

### BUG-005 — `repair_armor` Missing from Engine (v0.9, Medium)
`repair_armor` action existed in `services.json` but had no handler in the engine. Added alongside `repair_weapon`.

### BUG-006 — Durability Could Go Below Zero (v0.9, Low)
`decay_durability` clamped to `max(0, cur)` fix applied.

### BUG-007 — `get_effective_max_hp` Not Used in Rest (v0.9, Low)
Rest was restoring `max_hp` without including buff bonuses. Fixed to use `get_effective_max_hp()`.

---

## Fixed in v1.0.0-stable

---

### BUG-015 — `do_combat_action` ValueError: too many values to unpack

**File:** `DevTools.pyw` → `AuditRunner._do_combat_action()`
**Severity:** High — crash in the Audit Tool during any combat step

**Description:**
`GameEngine.do_combat_action()` returns 4 values `(ended, msg, fled, player_dead)`, but the Audit Tool was unpacking only 3 (`ended, msg, _`). This caused `ValueError: too many values to unpack (expected 3)` every time the audit runner entered combat.

**Fix:** Changed the unpack to `ended, msg, _fled, _dead = self.engine.do_combat_action(...)`.

---

### BUG-016 — "Unknown or unavailable action" in PyInstaller Build

**File:** All data loader files, `app/logic/dispatcher.py`
**Severity:** Critical — all city actions broken in the packaged `.exe`

**Description:**
Every data loader used bare relative paths (`os.path.join("data", ...)`, `pathlib.Path("data/actions")`). When the game runs as a PyInstaller executable, the working directory is not guaranteed to be the project root. The `ActionDispatcher` loaded zero actions, causing every button click to return `"Unknown or unavailable action: 'go_tavern'"`.

**Fix:** Created `app/paths.py` with `get_base_dir()` (returns `Path(sys.executable).parent` when frozen, project root otherwise) and `data_path(*parts)`. Updated all 16 affected files to use `data_path()`.

---

### BUG-017 — Profile Selector Opened a Separate Toplevel Window

**File:** `app/data/init/profile_selector.py`
**Severity:** Medium — inconsistent UX; window could be lost behind the main window

**Description:**
The profile selector at startup (and when loading a profile in-game) opened a `tk.Toplevel` window that the player had to interact with separately. On some platforms this window appeared behind the main window.

**Fix:** Replaced with `ProfileSelectorFrame` — a `tk.Frame` that fills the root window using `place(relwidth=1, relheight=1)`. A `BooleanVar` is used with `root.wait_variable()` to block until a selection is made, without the need for a separate window.

---

### BUG-018 — `messagebox.showinfo` Interrupting Gameplay with Popups

**File:** `app/ui/core/game_actions.py`, `app/ui/core/profile_actions.py`
**Severity:** Low — disruptive UX; popups interrupted game flow

**Description:**
Every game action (rest, buy, sell, combat result, save) called `messagebox.showinfo()`, opening a modal dialog that the player had to dismiss before continuing. This was particularly disruptive during rapid combat.

**Fix:** Added `MainWindow.post_message(msg)` which appends messages to an inline `TextDisplay` strip at the bottom of the window. Replaced all 10 `showinfo` call sites in game/profile actions. `messagebox` is now only used for errors and the game-over warning.

---

### BUG-019 — `shop.sell` Crashes with `AttributeError` When Item Is Equipped

**File:** `app/logic/resolvers/shop/sell.py`
**Severity:** High — crash any time the player attempted to sell an item while anything was equipped

**Description:**
`shop/sell.py` called `eq.get("item_id")` directly on the equipment slot value, assuming it was always a dict. The AAD engine stores equipment as a dict (`{"item_id": "...", "item": {...}, "current_durability": N, "max_durability": N}`), but any path that stored a plain item-ID string in the slot (legacy save files, tests, direct state assignment) triggered `AttributeError: 'str' object has no attribute 'get'`. This crash occurred silently via the dispatcher's exception handler, returning an error message rather than crashing the game outright — but the sell action was completely broken.

**Fix:** Added a `_equipped_id(slot_value)` helper in `sell.py` that handles both dict format and legacy plain-string format. Applied the same `isinstance(ew, dict)` guard to `get_weapon_bonus.py`, `get_armor_defense.py`, `resolve_unequip.py`, and all four equipment-reading sites in `view_builder.py`.

---

### BUG-020 — Equipment Simples Crash on Non-Dict Slot Values

**Files:** `app/logic/simple/get_weapon_bonus.py`, `app/logic/simple/get_armor_defense.py`, `app/logic/simple/resolve_unequip.py`
**Severity:** High — crash in any combat round or unequip action if slot held a non-dict value

**Description:**
All three simples called `.get()` on the raw equipment slot value without checking `isinstance(value, dict)`. Same root cause as BUG-019 — any non-dict value (string, None-derived, legacy format) would crash. `get_weapon_bonus` is called every combat round; a crash here would break the entire combat loop.

**Fix:** Added `isinstance(ew, dict)` guards to all three files before any `.get()` call.

---

### BUG-021 — `view_builder.py` Equipment Rendering Crashes on Non-Dict Slot Values

**File:** `app/logic/core/view_builder.py`
**Severity:** Medium — crash when building inventory, combat, or player-panel views with malformed equipped slot

**Description:**
`build_inventory`, `build_combat`, and `build_player_panel` all called `.get()` on equipment slot values without type-checking. Any non-dict value in `equipped_weapon` or `equipped_armor` would crash view rendering, making the inventory and combat panels inaccessible.

**Fix:** Introduced `_as_equip_dict(value)` module-level helper (returns `None` for non-dict values, the dict unchanged for valid values). All four equipment-reading sites now use it.

---

### BUG-022 — Spurious `f` Prefix on Two Plain String Literals

**Files:** `app/logic/resolvers/combat/attack.py:38`, `app/logic/resolvers/shop/buy.py:19`
**Severity:** Low — no runtime impact but pyflakes warning; indicates untested literal paths

**Description:**
`f"⚠ Your weapon has broken!"` and `f"That item is not available here."` had the `f` prefix with no `{}` placeholders. Pyflakes flagged these as `f-string is missing placeholders`. While harmless at runtime, the `f` prefix suggests the author intended to include a variable that was never added.

**Fix:** Removed the `f` prefix from both literals.

---

### BUG-023 — 31 Files With Unused Imports (pyflakes)

**Files:** Multiple (see list below)
**Severity:** Low — no runtime impact; reduces code clarity and maintainability

**Description:**
pyflakes identified 31 files with unused imports — mostly `typing` symbols (`Any`, `Optional`, `List`, `Dict`, `Callable`, `Tuple`) that were added during development but are no longer referenced after refactors, and `StyleManager` imports in UI widget files that are no longer used directly. Also: `import shutil` in `profile_manager.py`, `import random` in `entity_mgr.py`, `import tkinter as tk` in `component_registry.py` and `menu_list.py`, and module-level imports for `heal_entity`, `set_location`, `get_effective_max_hp` that were superseded.

**Fix:** Removed all 31 unused imports. All files re-parsed cleanly. No behaviour changed.

**Files fixed:** `app/profile_manager.py`, `app/game_engine.py`, `app/logic/dispatcher.py`, `app/logic/core/router.py`, `app/logic/complex/entity_mgr.py`, `app/logic/complex/dungeon_mgr.py`, `app/logic/simple/resolve_equip.py`, `app/logic/core/view_builder.py`, `app/logic/resolvers/location/rest.py`, `app/ui/complex/coordinator.py`, `app/ui/complex/assembler.py`, `app/ui/assembler.py`, `app/ui/component_builder.py`, `app/ui/component_registry.py`, `app/ui/data_binder.py`, `app/ui/view_registry.py`, `app/ui/simple/component_builder.py`, `app/ui/simple/component_registry.py`, `app/ui/simple/data_binder.py`, `app/ui/simple/view_registry.py`, `app/ui/simple/basic/input_field.py`, `app/ui/simple/basic/dialog_box.py`, `app/ui/simple/basic/text_display.py`, `app/ui/simple/basic/action_button.py`, `app/ui/simple/basic/menu_list.py`, `app/ui/simple/panels/inventory_panel.py`, `app/ui/simple/panels/combat_panel.py`, `app/ui/simple/panels/lore_panel.py`, `app/components/game_engine/dungeon_actions.py`, `app/components/game_engine/location_actions.py`, `app/data/managers/dungeon_gen.py`.

---

### BUG-024 — Unused Local Variables `theme` / `global_theme` in `ComponentBuilder`

**Files:** `app/ui/component_builder.py`, `app/ui/simple/component_builder.py`
**Severity:** Low — dead code; variables assigned but never read

**Description:**
Both copies of `ComponentBuilder.build()` computed `theme = self._theme.get(comp_type, {})` and `global_theme = self._theme.get("global", {})` and then never used either variable. `StyleManager` handles theming globally; no per-build theme lookup is needed.

**Fix:** Removed both dead assignments from both files.
