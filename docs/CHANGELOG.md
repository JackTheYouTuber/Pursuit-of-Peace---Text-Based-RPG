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
