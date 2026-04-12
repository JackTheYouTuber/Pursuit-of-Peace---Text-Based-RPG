# Known Gaps — Pursuit of Peace  v1.0.0

Features that are planned or structurally anticipated but not yet fully implemented.

---

## ✓ Complete in v1.0.0

| Gap | Status |
|-----|--------|
| Economy / Shop System (Tier 4) | ✓ Complete — buy/sell at marketplace, alchemy hall, blacksmith |
| Equipment System (Tier 3) | ✓ Complete — equip/unequip, durability, repair |
| Consumable Use System (Tier 2) | ✓ Complete — use in city and mid-combat |
| Buff System (Tier 2/3) | ✓ Complete — turns, one_run, permanent; tick after each attack |
| Data-Driven Loot Drops (Tier 4) | ✓ Complete — loot_table, loot_chance, loot_count per enemy |
| Year Rollover via Dispatcher | ✓ Complete — advance_year action, exile on unpaid taxes |
| Active Action Dispatch (AAD) | ✓ Complete — all actions JSON-defined, auto-discovered resolvers |

---

## Planned — v1.1.0

### GAP-101 — Fishing Mini-Loop

**Structure present:** `fishing.cast_line` and `fishing.fishing_tick` resolvers exist as stubs. `data/fish_pool.json` created with weighted catch pool.

**What is needed:**
- Scheduler thread that fires `fishing_tick` after a real-time delay (10 seconds).
- Weighted random selection from `fish_pool.json`.
- UI feedback during the wait (animated indicator or countdown).

---

### GAP-102 — Dynamic Shop Restocking

**Current behaviour:** Shop inventory is static — the same list every visit.

**What is needed:**
- A per-year or per-visit restock system. Could draw from `economy/inventory_templates.json`.
- Optional: shops sell out of items after purchases; restock on year rollover.

---

### GAP-103 — NPC Merchants

**Anticipated by:** Entity ID scheme supports `n_<name_hash>` for named NPCs.

**What is needed:**
- NPC definitions in data (name, dialogue, shop inventory, faction).
- Encounter system to place NPCs in dungeon rooms or city locations.
- Dialogue tree data format.

---

### GAP-104 — Coliseum Combat

**Current behaviour:** Coliseum location exists but has only a `go_city` action.

**What is needed:**
- Arena combat mode (no dungeon — fight waves for gold and glory).
- Leaderboard or personal best tracking.

---

## Planned — v1.2.0

### GAP-201 — Crafting System

**Anticipated by:** Reagent items exist (`item_reagent_sulfur_01`, `item_reagent_root_01`) but have no recipes.

**What is needed:**
- `data/recipes.json` schema.
- `craft_item` action and `crafting.craft` resolver.
- Alchemy Hall UI extension for recipe browsing.

### GAP-202 — Player Levelling

**Current behaviour:** `player_state["level"]` is tracked but has no mechanical effect.

**What is needed:**
- XP gain from kills.
- Level-up thresholds in config.
- Stat increases or unlock gates per level.

### GAP-203 — Events System

**Anticipated by:** `data/events/events.json` stub exists.

**What is needed:**
- Random event triggers (on location entry, on year rollover).
- Event resolver that reads from `events.json` and applies outcomes.
