# Pursuit of Peace — Changelog

## v0.9.0 — Tier 2 & Tier 3 Complete

### Tier 1 Fixes (retroactive)
- **Profile deletion on death** — player death now permanently deletes the save file via `ProfileManager.delete_profile()`. The old code only called `init_player()` leaving the file intact.
- **Combat gold rewards** — defeating an enemy now awards scaled gold (`hp/4` to `hp/2` range, randomised) and increments the kill counter.
- **Loot drops** — enemies have a 60% chance to drop one item from their `loot_table` on defeat. Item is added to inventory automatically with a log message.
- **Kill counter** — `player_state["kills"]` is now tracked and displayed in the player panel.

### Tier 2 — Consumable & Effect System
- **EffectResolver** (`app/components/game_engine/effect_resolver.py`) — new module that parses item `effect` text strings and applies heal, damage-buff, and debuff-removal effects to player state.
- **BuffSystem** (`app/components/game_engine/buff_system.py`) — new module managing active buffs. Supports three duration types:
  - `turns` — decremented after each attack round, expires when 0.
  - `one_run` — expires when the player exits the dungeon.
  - `permanent` — never expires.
- **Use button in inventory** — consumable items now show a **Use** button in the inventory panel. Item is consumed on use; effect is applied immediately.
- **Use item mid-combat** — consumable items from inventory appear as action buttons in the combat panel. Using a potion in combat updates HP bars instantly without ending the combat round.
- **Bath buff** — taking a bath at the Public Bath now grants the `Refreshed` buff: +5 max HP for the current dungeon run.
- **Strength potion** — Muscle Draught grants `strength_boost` buff: +3 damage for 3 attack turns.

### Tier 3 — Equipment & Combat Progression
- **Equipment slots** — `equipped_weapon` and `equipped_armor` added to `player_state` and `data/player/defaults.json`. Slots persist in profile saves.
- **Equip / Unequip** — inventory panel shows **Equip** button for weapons and armor. Equipping moves item from inventory to slot; old item is returned to inventory. Unequip buttons shown for currently equipped items.
- **`stat_bonus` and `durability` fields** added to all weapons and armors in `data/dungeon/items/items.json`.
- **Combat damage scaling** — player attack damage = base roll (4–8) + weapon `damage` bonus + buff bonus. Enemy damage received = raw roll − armor `defense` bonus (minimum 1). Both shown clearly in the combat log.
- **Durability decay** — weapon loses 1 durability per attack; armor loses 1 per hit received. At 0 the item breaks, is auto-unequipped, and a warning is shown.
- **Blacksmith repair** — `repair_weapon` and `repair_armor` location actions added. Cost = `(max_durability − current_durability) × prices["repair_per_point"]`.
- **Inventory panel redesign** — now shows:
  - Equipment summary at top (current weapon/armor with durability and stat bonuses).
  - Item list in the middle.
  - Contextual action buttons (Use / Equip / Sell) beneath the list.
- **Player panel** — now displays gear bonus summary (e.g. `+5⚔ +3🛡`) and total kill count.

### Tier 4 (Groundwork)
- `buy_item` and `sell_item` engine actions are fully wired (40% sell price). UI shop browsing (item lists per location) is the remaining step for full Tier 4 completion.

### Data Changes
- `data/player/defaults.json` — added `equipped_weapon`, `equipped_armor`, `kills`, `times_died`.
- `data/dungeon/items/items.json` — all weapons and armors now include `stat_bonus` and `durability`.
- `data/ui/layouts/inventory.json` — added `on_action: "inventory_action"` binding.

---

## v0.7.3
- Year rollover trigger (ISSUE-008 / GAP-006).
- Dungeon lore text populated (ISSUE-009 / GAP-011).

## v0.7.0
- Enemy counter-attack (ISSUE-001).
- Player death detection (ISSUE-002).

---

## v0.9.4 — Tier 1, 2 & 3 Gap Closure

### Tier 1 — Data-Driven Loot & Gold
- **`enemies.json`** — all 12 enemies now have `gold_min`, `gold_max`, `loot_chance`, and `loot_count` fields. The engine reads these directly; hardcoded fallback values are gone.
- Gold rewards are now properly scaled per enemy tier (e.g. Bloated Rat drops 2–5g; Deep-Born Thing drops 28–50g).
- Loot drop probability ranges from 50–75% by enemy, with `loot_count: 2` for stronger enemies.

### Tier 2 — Buff Visibility & Data-Driven Sell Price
- **Active buffs now shown in the player panel sidebar.** The "Effects:" row appears only when a buff is active, listing each effect and its remaining duration (e.g. `Strength +3 (2 turns), Refreshed (until exit)`). The row hides when no effects are active.
- **`sell_price_multiplier`** moved from hardcoded `0.4` in Python to `data/economy/prices.json`. Inventory "Sell" button and sell confirmation both read the live value.

### Tier 3 — Repair Mismatch & Durability Bar
- **`repair_equipment` name mismatch fixed.** `services.json` blacksmith now lists `repair_weapon` and `repair_armor` — the same names the engine handles. The old broken `repair_equipment`, `buy_weapon`, `buy_armor` stubs removed.
- **Durability bar** — inventory equipment summary now shows a `[████░░░░░░]` text bar. Bar character changes from `█` (healthy) → `▓` (worn) → `▒` (critical) based on percentage remaining.
- **Player panel durability** — gear summary in sidebar now shows `+5⚔ [48/50]` so durability is visible without opening inventory.
- **Dead stub actions removed** from marketplace, alchemy hall, and coliseum. Players no longer see buttons that crash. These locations will get real actions in Tier 4.

---

## v0.9.5 — Trinity Architecture Restructure

### Philosophy

The entire codebase has been reorganised around two principles: **Trinity** (UI / Logic / Data) and **Bureaucracy** (Core gives orders, Complex manages, Simple executes). Every file has one job. Cores do not validate. Managers do not render. Simples do not know context.

### New directory structure

```
app/
├── app.py                     The core of cores — wires the three pillars, nothing else
├── data/
│   ├── loaders/               One file per data type. Load and serve. Never decide.
│   │   ├── item_loader.py     items.json — get by id, all, by source, by type
│   │   ├── enemy_loader.py    enemies.json — get by id, all, at depth
│   │   ├── lore_loader.py     lore/*.json — on-demand, cached per location
│   │   └── config_loader.py   prices, services, locations, dungeon config, defaults
│   ├── managers/              Coordinate loaders. Make I/O decisions.
│   │   ├── profile_mgr.py     list, load, save, delete, create profiles
│   │   ├── dungeon_gen.py     generate runs, navigate rooms, pick enemies/items
│   │   └── location_mgr.py    answer "what actions does this location have?"
│   └── init/
│       ├── registry.py        DataRegistry — build once, pass everywhere
│       ├── engine_factory.py  Wire DataRegistry → Engine
│       └── profile_selector.py  Startup dialog
├── logic/
│   ├── simple/                Atomic. One job. Pure state-in, state-out. No messages.
│   │   ├── heal_player.py     Add HP, cap at effective max
│   │   ├── damage_player.py   Subtract HP, return dead flag
│   │   ├── add_gold.py        Add gold
│   │   ├── remove_gold.py     Subtract gold
│   │   ├── add_item.py        Append item_id to inventory
│   │   ├── remove_item.py     Remove first occurrence of item_id
│   │   ├── equip_item.py      Move item from inventory to slot
│   │   ├── unequip_item.py    Move item from slot to inventory
│   │   ├── apply_buff.py      Push buff, replace same-id (no stacking by default)
│   │   ├── remove_buff.py     Filter buff by id
│   │   ├── tick_buffs.py      Decrement turn buffs, return expired labels
│   │   ├── expire_run_buffs.py Remove all one_run buffs
│   │   ├── decay_durability.py Subtract 1 durability from a slot, return broke flag
│   │   ├── parse_effect.py    Turn "Restores 10 hp" into {"type":"heal","value":10}
│   │   ├── set_location.py    Set current_location_id
│   │   ├── increment_kills.py kills += 1
│   │   └── set_year.py        Advance year, reset tax_paid
│   ├── complex/               Managers. Validate orders. Coordinate simples.
│   │   ├── buff_mgr.py        Stat queries + apply/tick/expire buff lifecycle
│   │   ├── item_mgr.py        use, equip, unequip, repair, buy, sell
│   │   ├── player_mgr.py      rest, bath, fish, pay_taxes, hear_rumors, year_rollover
│   │   ├── combat_mgr.py      combat session, attack rounds, flee, loot awards
│   │   └── dungeon_mgr.py     take_item, next_room, mark_cleared, room lore
│   └── core/                  Orchestrators. Give orders. Report results. No rules.
│       ├── engine.py          Routes action_id → manager → state update
│       ├── state.py           Single source of truth (player + dungeon state)
│       ├── year_clock.py      Action counter, fires rollover signal
│       ├── router.py          Maps action_id strings to intent (no if/elif in engine)
│       └── view_builder.py    Transforms game state → UI state dicts
└── ui/
    ├── core/
    │   ├── app.py             (moved — now at app/app.py)
    │   ├── window.py          Sidebar + content frame layout
    │   ├── game_actions.py    Routes UI events → engine → coordinator
    │   └── profile_actions.py Save/load/new/quit
    ├── complex/
    │   ├── assembler.py       Data-driven view builder (reads layout JSON)
    │   └── coordinator.py     Switches and refreshes active views
    └── simple/
        ├── component_builder.py  Instantiates widget trees
        ├── component_registry.py Maps type strings → widget classes
        ├── data_binder.py        Binds state paths to widget update methods
        ├── layout_loader.py      Reads layout JSON files
        ├── view_registry.py      Caches built view widgets
        ├── style_manager.py      ttk style application
        ├── constants.py          Dynamic theme constants
        ├── theme.py              Loads themes.json
        ├── menu.py               Tkinter menubar
        ├── profile_dialogs.py    Profile selection dialog
        ├── basic/                Layer 1 widgets — zero project imports
        └── panels/               Layer 2 panel widgets
