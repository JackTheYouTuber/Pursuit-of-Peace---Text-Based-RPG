# Known Issues — Pursuit of Peace

Issues that exist in the current codebase but have not yet been fixed. Entries include the affected file, a description, and reproduction steps where applicable.

---

## Active Issues

---

### ISSUE-001 — No Enemy Counter-Attack in Combat

**File:** `app/components/game_engine/combat_system.py`  
**Priority:** High  

**Description:**  
Enemies have `damage_min` and `damage_max` fields defined in `enemies.json`, but the combat system never applies enemy damage to the player. Every attack round deals player damage to the enemy with no reciprocal damage. Combat is unwinnable by the enemy and presents no HP risk to the player.

**Expected Behaviour:**  
Each round after the player attacks, the enemy should deal random damage (between its `damage_min` and `damage_max`) to the player's HP.

**Reproduction:**  
Enter any dungeon room with an enemy. Attack repeatedly — player HP never decreases.

---

### ISSUE-002 — Player Death Is Not Handled

**File:** `app/game_engine.py`, `app/components/game_engine/combat_system.py`  
**Priority:** High (depends on ISSUE-001 being fixed first)  

**Description:**  
There is no game logic to handle player HP reaching zero. If enemy counter-attacks are ever implemented, a player reduced to 0 HP would continue to exist in a broken state — the UI would still show the city or dungeon, and no game-over condition would trigger.

**Expected Behaviour:**  
When player HP ≤ 0, combat should end, the player should be returned to a death/game-over screen, and the profile should be marked appropriately.

---

### ISSUE-003 — Many Location Actions Are Stubs (Unimplemented)

**File:** `app/game_engine.py`, `app/components/game_engine/location_actions.py`  
**Priority:** Medium  

**Description:**  
The following action IDs appear in `services.json` and are shown to the player as clickable buttons, but trigger the fallback `"Action not yet implemented"` message when clicked:

- `buy_item`, `sell_item` (Marketplace)
- `buy_potion`, `sell_reagent`, `craft_consumable` (Alchemy Hall)
- `buy_weapon`, `buy_armor`, `repair_equipment` (Blacksmiths Street)
- `enter_combat_event`, `watch_combat_event`, `place_wager` (Coliseum)

Players can click these buttons and receive an unhelpful error message, which is confusing. These should either be implemented or hidden/greyed out until implemented.

---

### ISSUE-004 — Item Use Has No Effect

**File:** `app/controllers/game_actions.py`, `app/components/game_engine/`  
**Priority:** Medium  

**Description:**  
Selecting an item in the Inventory view shows its description (name, type, value, effect text), but there is no "Use" or "Equip" action. Consumables like `item_bandage_01` (Restores 5 HP) and `item_potion_health_01` (Restores 10 HP) can be collected but never consumed. Weapons and armour can be collected but never equipped, so they have no effect on combat.

---

### ISSUE-005 — Buff System Has No Effect

**File:** `app/components/game_engine/location_actions.py`  
**Priority:** Medium  

**Description:**  
The Public Bath grants a buff (`{"stat": "max_hp", "amount": 5, "duration": "one_run", "label": "Refreshed"}`) that is stored in `player_state["buffs"]`. However, no part of the game reads or applies `player_state["buffs"]`. The buff is cosmetic only and has no mechanical effect.

---

### ISSUE-006 — `UIFactory` Is a Stub

**File:** `app/init/ui_factory.py`  
**Priority:** Low  

**Description:**  
`UIFactory.create()` contains only a `pass` statement and returns `None`. It is not called anywhere in the current codebase — `App.__init__()` constructs the UI components inline. The file is dead code and creates a false impression of a factory pattern being in use.

---

### ISSUE-007 — `ProfileDialogs` Is a Duplicate of `ProfileSelector`

**File:** `app/ui/profile_dialogs.py`  
**Priority:** Low  

**Description:**  
`ProfileDialogs.select_or_create()` is nearly identical to `ProfileSelector.select_or_create()` in `app/init/profile_selector.py`. The `App` class uses `ProfileSelector`; `ProfileDialogs` is never imported or called. This dead class adds maintenance burden — any change to the profile dialog must be made in two places if both are ever used.

---

### ISSUE-008 — Year Rollover Has No Trigger

**File:** `app/game_engine.py`, `app/app.py`  
**Priority:** Medium  

**Description:**  
`GameEngine.process_year_rollover()` exists and is implemented correctly, but nothing in `App` or the controllers ever calls it. There is no in-game timer, event, or player action that advances the year. The tax system is therefore inert — a player can never be exiled because the year never rolls over.

**Expected Behaviour:**  
A mechanic (e.g. a "Rest until morning" counter, a turn counter, or a year-end event trigger) should call `process_year_rollover()` and handle the exile case by ending the game.

---

### ISSUE-009 — Lore Files Are All Empty

**File:** `data/lore/*.json`  
**Priority:** Low  

**Description:**  
All lore JSON files (`alchemy_hall.json`, `blacksmiths_street.json`, `coliseum.json`, `dungeon.json`, `dungeon_entrance.json`, `marketplace.json`, `public_bath.json`, `the_river.json`, `tavern.json`) contain only `[]`. The only populated lore files are `city_entrance.json` and `global.json`. Most city locations therefore display no description text, and dungeon rooms have no lore text.

---

### ISSUE-010 — `data/economy/inventory_templates.json` and `data/events/events.json` Are Stubs

**File:** `data/economy/inventory_templates.json`, `data/events/events.json`  
**Priority:** Low  

**Description:**  
Both files contain only `[]`. The `DataLoader` loads them and exposes them via getters, but no game system currently reads inventory templates or world events.
