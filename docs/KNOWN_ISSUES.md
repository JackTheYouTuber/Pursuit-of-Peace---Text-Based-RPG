# Known Issues — Pursuit of Peace  v1.0.0-stable

Active bugs and limitations in the current release. See BUGFIXES.md for resolved issues.

---

### ISSUE-001 — Coliseum Has No Content

**Location:** `data/city/services.json` → `coliseum`
**Priority:** Low

The Coliseum is accessible from the city entrance but contains only a `go_city` navigation button. No combat, leaderboard, or event logic exists.

**Workaround:** None. The location is visually inert.
**Planned:** v1.1.0 (GAP-104).

---

### ISSUE-002 — Fishing Is Instant (Mini-Loop Not Active)

**Location:** `app/logic/resolvers/location/fish.py`
**Priority:** Low

`go_fishing` dispatches through the AAD resolver `location.fish`, which immediately picks a random fish. The full fishing mini-loop (`cast_line` + real-time `fishing_tick`) is scaffolded but not yet active.

**Workaround:** Current instant-catch behaviour is functional; items are awarded correctly.
**Planned:** v1.1.0 (GAP-101).

---

### ISSUE-003 — No Startup `current_location_id` Validation

**Location:** `app/logic/core/state.py`, `data/player/defaults.json`
**Priority:** Low

If a saved profile's `current_location_id` references a location not in `services.json` (e.g. after a modded data update), the engine silently returns an empty action list. The player sees a blank city panel.

**Workaround:** Manually edit the profile JSON to set `"current_location_id": "city_entrance"`.

---

### ISSUE-004 — Misc Items With `value: 0` Show Sell Button

**Location:** `app/ui/core/game_actions.py` → `on_inventory_select`
**Priority:** Low

Misc items with `value: 0` (junk drops) display a Sell button and sell for the 1g floor price. This may confuse players who expect junk to be unsellable.

**Workaround:** None visible. Items correctly sell for 1g.

---

### ISSUE-005 — Audit Tool Does Not Simulate Combat

**Location:** `DevTools.pyw` → Audit Tool tab
**Priority:** Low

The headless audit loop generates random city and dungeon actions but does not enter the combat state machine. Combat-specific bugs (player death, loot, durability decay) cannot be caught by the audit tool.

**Workaround:** Test combat paths manually or by reading the combat resolver code.
