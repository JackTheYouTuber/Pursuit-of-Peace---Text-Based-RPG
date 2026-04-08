# Pursuit of Peace — Changelog

## v0.7 (2026-04-08)

### New Features

**[ISSUE-001] Enemy Counter-Attack**
- Enemies now retaliate each combat round using their `damage_min`/`damage_max`
  values from `enemies.json`.
- The combat log shows both the player's attack and the enemy's counter-attack
  each round.

**[ISSUE-002] Player Death Handling**
- When player HP reaches 0, combat ends immediately with a "Game Over" dialog.
- The death message names the enemy responsible.
- After dismissing the dialog, the player state is reset and the game returns
  to the city view so a new run can begin without restarting the application.

**[ISSUE-008 / GAP-006] Year Rollover Trigger**
- Each service action (rest, fish, bath, take item, defeat enemy, etc.) now
  increments an internal action counter.
- When the counter reaches `ACTIONS_PER_YEAR` (30), `process_year_rollover()`
  fires automatically.
- If taxes are unpaid at rollover, the exile game-over screen is shown.
- Navigation actions (moving between locations) do not consume action ticks.

**[ISSUE-009 / GAP-011] Lore Text — All Locations**
- All previously empty lore JSON files have been populated:
  - `city_entrance.json` — description + ambient
  - `city_hall.json` — description + ambient
  - `tavern.json` — description + ambient + 4 rumor entries
  - `global.json` — world description + 2 history entries
  - `dungeon.json` — description + ambient
  - `dungeon_entrance.json` — description + ambient
  - `alchemy_hall.json` — description + ambient
  - `blacksmiths_street.json` — description + ambient
  - `marketplace.json` — description + ambient
  - `coliseum.json` — description + ambient
  - `public_bath.json` — description + ambient
  - `the_river.json` — description + ambient

### UI Changes
- Combat panel now shows a **player HP bar** alongside the enemy HP bar,
  making the counter-attack damage visible each round.
- Window title now includes the version label: `Pursuit of Peace  v0.7`.

### Internal / Code
- Added `app/version.py` — single source of truth for the version string.
- `CombatSystem.start_combat()` now accepts `player_hp` and `player_max_hp`
  and tracks `player_current_hp` / `player_dead` in the combat state dict.
- `CombatSystem.attack()` returns a 4-tuple `(state, ended, msg, hp_lost)`.
- `GameEngine.do_combat_action()` returns a 4-tuple `(ended, msg, fled, player_dead)`.
- `GameEngine.end_combat()` accepts a `player_dead` kwarg.
- `GameEngine.get_action_progress()` exposes `(count, ACTIONS_PER_YEAR)` for
  potential future UI display.

---

## Pre-v0.7 (development baseline)

Initial codebase — UI shell, dungeon generation, navigation, city services, save/load
profiles, logger. No combat risk, no lore text, no year rollover.
