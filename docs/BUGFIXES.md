# Bug Fix Log — Pursuit of Peace

All bugs identified and fixed during code audit. Listed in order of severity.

---

## Fixed Bugs

---

### BUG-001 — Double `end_combat()` Call (Critical)

**File:** `app/controllers/game_actions.py`  
**Severity:** Critical — game crash / corrupted state  

**Description:**  
`GameEngine.do_combat_action()` already calls `self.end_combat()` internally after a winning attack or a flee action. `GameActions.on_combat_action()` was calling `self._engine.end_combat(fled)` a second time after receiving the result. This caused:
- Combat state to be cleared twice.
- The dungeon state to be set to `None` a second time when fleeing, which could cause downstream `NoneType` errors.
- On a winning attack, `end_combat(False)` was called once correctly inside the engine, then called again with the variable `fled` (which could be `True` at that point depending on flow), potentially marking the player as fled when they actually won.

**Fix:**  
Removed the redundant `self._engine.end_combat(fled)` call from `on_combat_action()`. State cleanup is now handled exclusively inside `GameEngine.do_combat_action()`.

---

### BUG-002 — Call to Non-Existent Method `_build_combat_state()` (Critical)

**File:** `app/controllers/game_actions.py` (line 69, original)  
**Severity:** Critical — `AttributeError` crash on every non-ending attack  

**Description:**  
After a non-lethal attack, the code attempted to refresh the combat panel by calling:
```python
combat_state = self._engine._build_combat_state(enemy)
```
No such method exists on `GameEngine`. This would raise `AttributeError` on every attack that did not end combat, making combat non-functional.

**Fix:**  
Replaced with the correct method:
```python
combat_state = self._engine.get_view_state(self.VIEW_COMBAT)
```
This uses the engine's proper public API, which builds the combat state dict from the active `CombatSystem` instance.

---

### BUG-003 — Private Method Name Mismatch: `_refresh_current_view` (High)

**File:** `app/controllers/game_actions.py`  
**Severity:** High — `AttributeError` on any location or dungeon action that changed state  

**Description:**  
`on_location_action()` and `on_dungeon_action()` called `self._refresh_current_view()` (with a leading underscore). The only defined method is the public `refresh_current_view()` (no underscore). Python does not silently ignore this — it raises `AttributeError` at runtime whenever a location navigation or dungeon transition occurred.

**Fix:**  
All internal call sites were updated to use `self.refresh_current_view()`. A class-level alias `_refresh_current_view = refresh_current_view` was also added so any future callers using either form continue to work.

---

### BUG-004 — Orphan File `view_builder.py.py` (Medium)

**File:** `app/components/game_engine/view_builder.py.py`  
**Severity:** Medium — `SyntaxError` / `IndentationError` if Python discovers it  

**Description:**  
A stray file with the double extension `.py.py` existed in the `game_engine` component directory. Its content was a bare function definition with no class or imports — not a valid Python module. Python's import system could potentially discover this file depending on `sys.path` configuration, and attempting to compile it would raise a `SyntaxError` (the function references `Dict` without importing `typing`). Even if never imported, its presence in the package directory was misleading and a maintenance hazard.

**Fix:**  
File deleted.

---

### BUG-005 — Duplicate `append_log` Method in `CombatPanel` (Low)

**File:** `app/ui/components/complex/combat_panel.py`  
**Severity:** Low — silent dead code; the first definition was unreachable  

**Description:**  
`CombatPanel` defined `append_log` twice:
1. First definition (no type hint on `text`): `def append_log(self, text):`
2. Second definition (typed): `def append_log(self, text: str):`

In Python, the second definition silently overwrites the first. The first definition was dead code. While this caused no runtime error, it was confusing and a latent source of bugs if the two definitions had ever diverged in behaviour.

**Fix:**  
Removed the first (untyped) definition. The typed version is retained.

---

### BUG-006 — Mixed CRLF / LF Line Endings (Low)

**Files:** `app/ui_assembler.py`, `app/ui/components/complex/combat_panel.py`, `app/ui/components/complex/location_panel.py`, `app/ui/components/complex/inventory_panel.py`, `app/ui/components/complex/player_panel.py`, `app/ui/components/complex/lore_panel.py`, `app/init/ui_factory.py`, `data/ui/layouts/*.json`  
**Severity:** Low — no runtime impact on Linux/macOS; causes messy version control diffs and potential issues in some Windows tools  

**Description:**  
Several files used Windows-style CRLF (`\r\n`) line endings while the rest of the project used Unix LF (`\n`). This created inconsistent diffs in version control and could cause issues with some text processing tools.

**Fix:**  
Ran `sed -i 's/\r//'` across all `.py` files under `app/` and all `.json` files under `data/ui/`. All files now use LF uniformly.
