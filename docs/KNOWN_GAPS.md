# Known Gaps — Pursuit of Peace

Features that the architecture anticipates or partially scaffolds, but which are not yet implemented. Unlike Known Issues (which are bugs in existing systems), these are missing systems entirely.

---

## Game Systems

---

### GAP-001 — Economy / Shop System

**Anticipated by:** `data/economy/`, `data/city/services.json` (marketplace, alchemy hall, blacksmiths actions), `data/dungeon/items/items.json` (item `value` fields)

**Description:**  
Items have `value` fields. Services define `buy_item`, `sell_item`, `buy_weapon`, `buy_armor`, `buy_potion`, `sell_reagent`, `repair_equipment` actions. No shop, pricing, or transaction logic exists. The `inventory_templates.json` stub suggests shop stock was planned.

**What is needed:**  
- A shop state (per-location stock list).
- Buy/sell UI flow (show available items, confirm purchase).
- Sell logic to remove items from inventory and add gold.
- Shop refresh between runs or per-year.

---

### GAP-002 — Equipment System (Weapons / Armour)

**Anticipated by:** Item types `"weapon"` and `"armor"` in `items.json`, `repair_equipment` action in `services.json`

**Description:**  
The player can collect weapons and armour from the dungeon, but has no concept of equipped items. No stats (attack, defence) exist on the player. Nothing reads equipped weapons to modify combat damage, and nothing reads armour to reduce incoming damage.

**What is needed:**  
- Player state fields: `equipped_weapon`, `equipped_armor`.
- Equip/unequip action in the Inventory view.
- `CombatSystem.attack()` should read the equipped weapon's damage bonus.
- Enemy damage should be reduced by equipped armour's defence value.
- `repair_equipment` action in the blacksmith needs to reference equipment durability.

---

### GAP-003 — Consumable Use in Combat and City

**Anticipated by:** Item type `"consumable"` and `effect` strings in `items.json`

**Description:**  
Items like `item_bandage_01` ("Restores 5 hp"), `item_potion_health_01` ("Restores 10 hp"), `item_antidote_01` ("Removes the poisoned debuff"), `item_potion_strength_01` ("Increases damage by 3 for 3 turns") are collectable but unusable. There is no "Use Item" action in any view.

**What is needed:**  
- A "Use" button in the Inventory view and/or a "Use item" action in Combat.
- An item effect resolver that parses `effect` strings or uses a structured effect schema.
- Buff/debuff application to player state.

---

### GAP-004 — Debuff / Status Effect System

**Anticipated by:** `player_state["buffs"]` field, bath buff (`stat: "max_hp", amount: 5`), antidote item effect ("Removes the poisoned debuff")

**Description:**  
The buff list exists in player state and is written to by the bath action, but nothing reads it. The antidote references a "poisoned" debuff that cannot currently be inflicted. A full status system (poison, strength boost, refresh, etc.) was clearly planned but not built.

**What is needed:**  
- A buff/debuff resolver run each combat turn and at rest.
- Duration tracking (`one_run`, `N turns`, `permanent`).
- Stat modifiers applied from active buffs.
- Enemies with poison attacks that apply the `poisoned` debuff.

---

### GAP-005 — World Events System

**Anticipated by:** `data/events/events.json` (currently empty), `DataLoader.get_events_for_location()`, `DataLoader.get_event()`

**Description:**  
The data loader has full event-loading infrastructure including per-location event queries. No events are defined and no code triggers them. Events could include random city events (tax collector, visiting merchant, brawl) or dungeon modifiers (cursed level, treasure bonus room).

**What is needed:**  
- Populated `events.json` with event definitions.
- An event scheduler that triggers events at location entry or turn boundaries.
- Event handlers wired into `LocationActions` or `GameEngine`.

---

### GAP-006 — Year Rollover Trigger Mechanism

**Anticipated by:** `GameEngine.process_year_rollover()`, `player_state["year"]`, `player_state["tax_paid"]`, exile/game-over logic

**Description:**  
Year rollover is fully implemented in the engine but never triggered. There is no in-game mechanism (timer, turn counter, calendar) that advances time. The tax and exile system is therefore inert.

**What is needed:**  
- A time/turn counter (e.g. days per year, or action count per year).
- A year-end event that calls `GameEngine.process_year_rollover()`.
- A game-over screen or dialog for the exile case (`process_year_rollover` returning `None`).

---

### GAP-007 — Coliseum / Arena System

**Anticipated by:** `services.json` (actions: `enter_combat_event`, `watch_combat_event`, `place_wager`)

**Description:**  
Three Coliseum actions are surfaced in the UI but not implemented. The arena is a natural gold sink and could provide a structured alternative to dungeon combat.

**What is needed:**  
- Arena opponent definitions (pre-defined fighters, not dungeon enemies).
- Wager system (bet gold before a fight, win/lose accordingly).
- `watch_combat_event` — passive gold-cost activity that grants lore or rumors.

---

### GAP-008 — Crafting System (Alchemy Hall)

**Anticipated by:** `services.json` (actions: `craft_consumable`, `sell_reagent`)

**Description:**  
Reagent items (`item_reagent_sulfur_01`, `item_reagent_root_01`) exist in the dungeon loot table but serve no purpose. The Alchemy Hall has a `craft_consumable` action that is unimplemented.

**What is needed:**  
- A recipe table (ingredient → output item).
- Crafting UI showing available recipes given current inventory.
- Sell-reagent flow (sell reagents for gold).

---

## Technical / Infrastructure

---

### GAP-009 — Save-on-Exit

**Anticipated by:** `ProfileActions.quit_app()` — it currently only destroys the window

**Description:**  
Quitting the game does not auto-save. A player who forgets to use File → Save Game will lose all progress. Auto-save on quit (with an "unsaved changes" prompt) should be considered.

---

### GAP-010 — `UIFactory` Completion

**Anticipated by:** `app/init/ui_factory.py` (currently a stub `pass`)

**Description:**  
`UIFactory` was likely intended to centralise all UI construction logic that is currently inline in `App.__init__()`. Completing it would improve testability and reduce coupling in `App`.

---

### GAP-011 — Dungeon Lore Population

**Anticipated by:** `DungeonManager.get_room_lore_text()`, `lore_key` field in room templates, `data/lore/dungeon.json` (currently `[]`)

**Description:**  
Room templates reference `lore_key` values (e.g. `"lore_room_empty_01"`, `"lore_room_enemy_01"`) that are supposed to resolve to descriptive text from `data/lore/dungeon.json`. The lore file is empty, so all dungeon rooms display no atmospheric text.
