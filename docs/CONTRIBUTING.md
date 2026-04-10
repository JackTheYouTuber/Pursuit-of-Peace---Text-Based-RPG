# Contributing & Developer Guide — Pursuit of Peace

This document covers how to extend the game (adding content) and how to use the developer tools. All game content lives in JSON — most additions require no Python changes at all.

---

## Developer Tools — DevTools.pyw

`DevTools.pyw` is the single consolidated developer utility. It replaces the three separate tools that existed in earlier versions (`audit.pyw`, `build_tool.pyw`, `delete_pycache.pyw`). Run it from the project root:

```
python DevTools.pyw
```

It opens a tabbed window with three tools:

### Tab 1 — Pycache Cleaner

Recursively deletes all `__pycache__` folders inside a directory you choose. Use this before packaging, committing, or to resolve import confusion after a refactor. Browse to the project root, click **Start Deletion**, and confirm.

### Tab 2 — Audit Tool

Runs the game engine in headless mode with random actions for a configurable number of steps, then reports any crashes with a full traceback and the last 20 actions taken. Use this after any engine change to catch regressions quickly.

- **Steps** — how many random actions to simulate (default 1000; use 5000+ for a thorough soak test).
- **Seed** — optional integer for a reproducible run. Leave blank for a random seed.
- **Export Log** — saves the full log to a `.txt` file for sharing or archiving.

The tool imports the game engine directly, so it must be run from the project root where `app/` is importable.

### Tab 3 — Build Tool

Packages the game into a standalone executable using PyInstaller. If PyInstaller is not installed, the tool offers to install it for you via pip.

Options:
- **Main script** — path to `main.pyw` (auto-detected if in the project root).
- **Executable name** — output name (e.g. `PursuitOfPeace`).
- **Icon file** — optional `.ico` file for the executable.
- **Windowed mode** — hides the console window (recommended for release builds).
- **Copy `data/` folder** — automatically copies the data directory next to the built executable so it runs correctly.
- **Clean before build** — removes old `build/` and `dist/` folders first.

Output lands in `dist/`. The `data/` folder must be distributed alongside the executable.

---

## Adding a New City Location

1. **Register the location** in `data/city/locations.json`:
   ```json
   { "id": "blackmarket", "name": "Black Market", "access": "always", "condition_ref": null }
   ```

2. **Define its actions** in `data/city/services.json`:
   ```json
   "blackmarket": {
     "actions": ["buy_stolen_goods", "sell_stolen_goods", "go_city"]
   }
   ```

3. **Add a navigation entry** in `app/game_engine.py` inside `do_location_action()`:
   ```python
   "go_blackmarket": "blackmarket",
   ```

4. **Add a display label** in `app/components/game_engine/view_builder.py` inside `_action_label()`:
   ```python
   "go_blackmarket": "Black Market",
   ```

5. **Add the nav action** to `city_entrance.actions` in `data/city/services.json` so players can reach it.

6. **Implement the action handler** in `app/components/game_engine/location_actions.py` and wire it in `app/game_engine.py` → `do_location_action()`.

7. **Add lore** — create `data/lore/blackmarket.json` with at least one `"description"` entry.

---

## Adding a New Item

Add an entry to `data/dungeon/items/items.json`. All fields are required:

```json
{
  "id":        "item_iron_key_01",
  "name":      "Iron Key",
  "type":      "misc",
  "min_depth": 2,
  "value":     15,
  "effect":    null,
  "source":    null
}
```

**For weapons and armour**, also include `stat_bonus` and `durability`:

```json
{
  "id":         "item_steel_sword_01",
  "name":       "Steel Sword",
  "type":       "weapon",
  "min_depth":  4,
  "value":      80,
  "effect":     null,
  "source":     null,
  "stat_bonus": {"damage": 8},
  "durability": 60
}
```

- `stat_bonus.damage` — added to every player attack in combat.
- `stat_bonus.defense` — subtracted from every incoming hit (minimum 1 damage always lands).
- `durability` — starting and maximum durability value. Degrades by 1 per hit; repaired at the Blacksmith.

**For consumables**, set `effect` to a plain English string the `EffectResolver` will parse:

```json
{
  "id":     "item_elixir_01",
  "name":   "Healing Elixir",
  "type":   "consumable",
  "value":  40,
  "effect": "Restores 25 hp"
}
```

Recognised effect patterns:
- `"Restores X hp"` — heals X HP, capped at max HP.
- `"Increases damage by X for Y turns"` — applies a `strength_boost` buff for Y turns.
- `"Removes the poisoned debuff"` — clears the poisoned status.

**For fishing items**, set `"source": "fishing"`. These never appear in dungeon rooms; they are only obtainable at The River.

No code changes are needed for any item type — the engine reads them automatically.

---

## Adding a New Enemy

Add an entry to `data/dungeon/enemies/enemies.json`. All fields are required:

```json
{
  "id":          "enemy_shadow_wolf_01",
  "name":        "Shadow Wolf",
  "min_depth":   3,
  "max_depth":   5,
  "hp":          30,
  "damage_min":  5,
  "damage_max":  10,
  "gold_min":    10,
  "gold_max":    18,
  "loot_chance": 0.65,
  "loot_count":  1,
  "loot_table":  ["item_bone_shard_01", "item_crude_knife_01"]
}
```

| Field | Description |
|---|---|
| `min_depth` / `max_depth` | Depth range this enemy can spawn in |
| `damage_min` / `damage_max` | Enemy attack range per round |
| `gold_min` / `gold_max` | Gold dropped on defeat |
| `loot_chance` | Probability (0.0–1.0) of a loot drop on defeat |
| `loot_count` | Number of items drawn from `loot_table` when loot drops |
| `loot_table` | Item IDs to draw from; one is chosen randomly per drop |

No code changes are needed. The enemy will automatically appear in dungeon rooms within its depth range.

---

## Adding a New Action Handler

1. **Add the action ID** to the relevant location in `data/city/services.json`.

2. **Add a display label** in `app/components/game_engine/view_builder.py` → `_action_label()`.

3. **Implement the method** in `app/components/game_engine/location_actions.py`:
   ```python
   def my_new_action(self, player_state: Dict) -> Tuple[Dict, str]:
       state = dict(player_state)   # always copy — never mutate the input
       # ... mutate state ...
       return state, "Action result message shown to player."
   ```

4. **Wire it** in `app/game_engine.py` → `do_location_action()`:
   ```python
   elif action_id == "my_new_action":
       new_player, msg = self._location_actions.my_new_action(player)
       self._state_mgr.update_player(new_player)
       result_changed = True
   ```

---

## Adding a New Consumable Effect

`EffectResolver` (`app/components/game_engine/effect_resolver.py`) parses item `effect` strings using regex patterns. To support a new effect type, add a matching branch to `_parse_and_apply()`:

```python
# Example: "Grants 10 max HP permanently"
max_hp_match = re.search(r"grants (\d+) max hp", text)
if max_hp_match:
    amount = int(max_hp_match.group(1))
    state["max_hp"] = state.get("max_hp", 20) + amount
    return f"You used {item_name}! Max HP permanently increased by {amount}."
```

Then add a consumable item whose `effect` text matches your new pattern. No further wiring is needed.

---

## Adding a New Buff

Buffs are plain dicts stored in `player_state["buffs"]`. The `BuffSystem` (`app/components/game_engine/buff_system.py`) reads `stat_mods` from each active buff when computing derived stats. To introduce a new stat modifier:

1. Add a new key to a buff's `stat_mods` dict (e.g. `"gold_bonus": 0.2`).
2. Add a corresponding `get_<stat>_bonus(player_state)` method to `BuffSystem`.
3. Apply it wherever the stat is used (e.g. in `game_engine._award_combat_rewards()` for a gold multiplier).

Buff duration types:
- `"turns"` — decremented after each attack round; requires a `duration_remaining` integer.
- `"one_run"` — automatically removed when the player exits the dungeon.
- `"permanent"` — never removed.

---

## Adding Lore Text

Lore files live in `data/lore/<location_id>.json`. Each file is an array:

```json
[
  {
    "id":   "lore_tavern_desc_01",
    "type": "description",
    "text": "The Rusty Flagon reeks of tallow smoke and spilled mead."
  },
  {
    "id":   "lore_tavern_rumor_01",
    "type": "rumor",
    "text": "A man in the corner whispers that the dungeon's third level is cursed ground."
  }
]
```

- `"description"` entries are shown when the player arrives at a location.
- `"rumor"` entries are shown when the player uses the **Rumors** action in the Tavern.
- `"ambient"` entries are used as a fallback description if no `"description"` entry exists.

For dungeon room lore, add entries to `data/lore/dungeon.json` and reference the `id` as the `lore_key` in a room template in `data/dungeon/rooms/room_templates.json`.

---

## Adding a New UI View

1. **Create a layout file** at `data/ui/layouts/<view_name>.json` describing the component tree (see existing layouts for examples).

2. **Register any new component types** in `app/ui/component_registry.py` if you created a new widget class.

3. **Implement `get_view_state(view_name)`** in `GameEngine` to return the state dict the view needs.

4. **Add the view name** to the whitelist in `App._show_view()`.

5. **Wire a navigation trigger** — a nav button in the sidebar or a callback in an existing controller.

---

## Code Style Guidelines

- **State immutability.** Always `state = dict(player_state)` at the top of any action method. Never mutate the input dict directly. This makes state transitions easy to trace and test.
- **No game logic in UI classes.** Widgets emit action ID strings only. They never read engine state directly.
- **No content in Python source.** Text, prices, item stats, enemy stats, buff definitions, lore, and action lists all belong in JSON.
- **Logger discipline.** Use `self._logger.data(event_id, payload)` for trackable game events, `self._logger.info(msg)` for navigation and system events, and `self._logger.warn(msg)` for recoverable problems. Never use `print()`.
- **Layer 1 widget rule.** Files in `app/ui/components/basic/` must have zero imports from `app/`. They are standalone Tkinter widgets.
- **Action ID naming.** Parameterised actions use a colon separator: `use_item:item_id`, `equip_item:item_id`, `sell_item:item_id`. The engine splits on `:` to extract the parameter.

---

## Running the Audit Tool

Use the **Audit Tool** tab in `DevTools.pyw`. It imports the game engine directly, so run it from the project root. For a thorough soak test before a release, use at least 5000 steps with a fixed seed so any failure is reproducible.

---

## Community & Support

- **Subreddit**: [r/PursuitOfPeaceGame](https://www.reddit.com/r/PursuitOfPeaceGame/) — share mods, ask questions, post suggestions
- **Discord**: [Join the server](https://discord.gg/HPVcBv5Dma) — real-time chat with developers and modders
- **Itch.io**: [Game page](https://jacktheyoutuber.itch.io/pursuit-of-peace) — download latest builds, leave reviews
