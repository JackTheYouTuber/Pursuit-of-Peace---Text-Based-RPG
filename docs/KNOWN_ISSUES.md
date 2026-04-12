# Known Issues — Pursuit of Peace  v1.0.0

Active bugs and limitations in the current release. Issues resolved in v1.0.0 have been removed; see BUGFIXES.md for the full history.

---

## Active Issues

---

### ISSUE-001 — Coliseum Has No Content

**Location:** `data/city/services.json` → `coliseum`
**Priority:** Low

**Description:**
The Coliseum location is accessible from the city entrance but contains only a `go_city` navigation button. No combat, leaderboard, or event logic exists.

**Expected Behaviour:**
Arena fights, a wave-survival mode, or at minimum a placeholder description explaining it is under construction.

**Workaround:** None. The location is visually inert.

---

### ISSUE-002 — Fishing Action Uses go_fishing (Non-AAD Path)

**Location:** `app/logic/core/engine.py`, `data/city/services.json`
**Priority:** Low

**Description:**
`go_fishing` is dispatched through the AAD resolver `location.fish`, which immediately picks a random fish. The full fishing mini-loop (`cast_line` + real-time `fishing_tick`) is scaffolded but not yet active. The current behaviour is instant — no wait, no feedback.

**Expected Behaviour (v1.1.0):**
Player casts line, waits ~10 seconds, result announced.

**Workaround:** Current instant-catch behaviour is functional; items are awarded correctly.

---

### ISSUE-003 — No Startup `current_location_id` Validation

**Location:** `app/logic/core/state.py`, `data/player/defaults.json`
**Priority:** Low

**Description:**
If a saved profile's `current_location_id` references a location not present in `services.json` (e.g. after a services.json update), the engine silently falls back to an empty action list. The player sees a blank city panel with no buttons.

**Expected Behaviour:**
Profiles with unknown location IDs should be reset to `city_entrance` on load with a logged warning.

**Workaround:** Manually edit the profile JSON to set `"current_location_id": "city_entrance"`.

---

### ISSUE-004 — Sell Button Available on Misc Items With No Sale Value

**Location:** `app/ui/core/game_actions.py` → `on_inventory_select`
**Priority:** Low

**Description:**
Misc items (bone shards, reagents, fish) show a Sell button in the inventory panel. Selling works correctly (awards 40% of `value`), but items with `value: 0` sell for 1g (the `max(1, ...)` floor). This may confuse players who expect junk items to be worthless.

**Expected Behaviour:**
Items with `value: 0` should not show a Sell button, or the sell price display should clearly show `"Junk — 1g"`.

**Workaround:** None visible; items sell for 1g floor correctly.

---

### ISSUE-005 — DevTools Audit Does Not Simulate Combat

**Location:** `DevTools.pyw` → Audit tab
**Priority:** Low

**Description:**
The headless audit loop generates random city and dungeon actions but does not enter the combat state machine. Combat bugs (player death path, loot drop, durability decay) cannot be caught by the audit tool in its current form.

**Expected Behaviour:**
Audit should include a combat simulation path that enters, resolves, and exits combat in headless mode.
