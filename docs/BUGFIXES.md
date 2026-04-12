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
