# Contributing & Developer Guide — Pursuit of Peace

This document explains how to extend the game: adding locations, enemies, items, lore, and new action handlers.

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

3. **Add navigation** — in `app/game_engine.py`, add an entry to `nav_map` inside `do_location_action`:
   ```python
   "go_blackmarket": "blackmarket",
   ```

4. **Add the nav action label** in `app/components/game_engine/view_builder.py` inside `_action_label()`:
   ```python
   "go_blackmarket": "Go to the Black Market",
   ```

5. **Add a nav button** in `data/city/services.json` under `city_entrance.actions` (or whichever locations should link to it):
   ```json
   "actions": [..., "go_blackmarket"]
   ```

6. **Implement the action** in `app/game_engine.py` (`do_location_action`) or delegate to `LocationActions`.

7. **Add lore** — create `data/lore/blackmarket.json` with at least one `"description"` entry.

---

## Adding a New Item

Add an entry to `data/dungeon/items/items.json`:

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

The item will automatically appear in dungeon rooms at or beyond `min_depth`. No code changes required for dungeon drops.

For fishing items, set `"source": "fishing"`. These items are excluded from dungeon drops and can only be obtained at The River.

---

## Adding a New Enemy

Add an entry to `data/dungeon/enemies/enemies.json`:

```json
{
  "id":          "enemy_shadow_wolf_01",
  "name":        "Shadow Wolf",
  "min_depth":   3,
  "max_depth":   5,
  "hp":          30,
  "damage_min":  5,
  "damage_max":  10,
  "loot_table":  ["item_bone_shard_01", "item_crude_knife_01"]
}
```

The enemy will automatically be eligible to spawn in dungeon rooms at the specified depth range. No code changes required.

---

## Adding a New Action Handler

1. **Add the action ID** to the relevant location in `data/city/services.json`.

2. **Add a display label** in `app/components/game_engine/view_builder.py` → `_action_label()`.

3. **Implement the handler** in `app/game_engine.py` → `do_location_action()`:
   ```python
   if action_id == "my_new_action":
       new_player, msg = self._location_actions.my_new_action(player)
       self._state_mgr.update_player(new_player)
       return True, msg
   ```

4. **Add the method** to `app/components/game_engine/location_actions.py`:
   ```python
   def my_new_action(self, player_state: Dict) -> Tuple[Dict, str]:
       state = dict(player_state)
       # ... mutate state ...
       return state, "Action result message."
   ```

---

## Adding Lore Text

Lore files are in `data/lore/<location_id>.json`. Each file is an array of entries:

```json
[
  {
    "id":   "lore_tavern_desc_01",
    "type": "description",
    "text": "The Rusty Flagon reeks of tallow smoke and spilled mead..."
  },
  {
    "id":   "lore_tavern_rumor_01",
    "type": "rumor",
    "text": "A man in the corner whispers that the dungeon's third level is cursed ground."
  }
]
```

For dungeon room lore, add entries to `data/lore/dungeon.json` and reference the `id` as the `lore_key` in a room template.

---

## Adding a New UI View

1. **Create a layout file** at `data/ui/layouts/<view_name>.json` describing the component tree.

2. **Register any new component types** in `UIAssembler._COMPONENT_REGISTRY` if needed.

3. **Implement `get_view_state()`** in `GameEngine` to return the state dict for the new view.

4. **Add the view** to `App._show_view()` whitelist.

5. **Wire a navigation trigger** — a nav button in the sidebar or a callback in an existing controller.

---

## Code Style Guidelines

- **State immutability pattern:** Always `state = dict(player_state)` at the start of any action method. Never mutate the incoming dict directly.
- **No game logic in UI classes.** Widgets emit action IDs only. They never read engine state directly.
- **No content in Python source.** Text, prices, item stats, lore, and action lists all belong in JSON data files.
- **Logger discipline:** Use `self._logger.data(event_id, payload)` for game events, `self._logger.info(msg)` for navigation/system events, and `self._logger.warn(msg)` for recoverable problems.
- **Layer 1 widgets have zero project imports.** `basic/` components must not import from `app/`.

---

## Running the Audit Tool

`audit.pyw` is a standalone Tkinter tool for browsing session log files. Run it directly:

```
python audit.pyw
```

It does not require the rest of the app to be running.
