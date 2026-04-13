# Pursuit of Peace — Text-Based RPG  `v1.0.0-stable`

A single-player, turn-based text RPG built with Python and Tkinter. You play as a citizen of a walled city who must survive year-to-year — managing gold, equipping gear, exploring dungeons, and paying taxes to avoid permanent exile.

**Death is permanent. Exile is permanent. Every run counts.**

---

## Features (v1.0.0-stable)

### Core Survival Loop
- **Year system** — every 30 actions a year passes. Pay your taxes at City Hall or face permanent exile.
- **Permanent death** — dying in the dungeon deletes your save file. No second chances.
- **Roguelike identity** — each profile is a unique run. Losing one means starting fresh.

### City & Economy (Tier 4)
- **Buy items** at the Marketplace, Alchemy Hall, and Blacksmith's Street.
- **Sell items** from your inventory for 40% of base value.
- **Repair gear** at the Blacksmith — cost scales with damage taken.
- **Pay taxes** at City Hall before year end.
- **Rest** at the Tavern to restore full HP.
- **Take a bath** at the Public Bath for a dungeon-run buff.
- **Go fishing** at the River for a chance to catch sellable fish.

### Dungeon Exploration
- Procedurally generated dungeons with variable room counts and depths.
- Enemy encounters, item pickups, and room-by-room traversal.
- Flee the dungeon at any time (one_run buffs expire on exit).

### Combat (Tier 1–3)
- Turn-based combat with enemy counter-attacks.
- Weapon bonus + buff bonus + base roll determine your attack.
- Armor absorbs incoming damage.
- Durability decay per hit; broken gear auto-unequips with a warning.
- Use consumable items mid-combat.

### Equipment & Buffs (Tier 2–3)
- Two equipment slots: weapon and armor.
- Buff durations: `turns`, `one_run`, `permanent`.
- Buff summary always visible in the player panel.

### Inline UI (v1.0.0-stable)
- Profile creation, selection, and deletion all happen inside the main window — no popup dialogs.
- Game event messages stream to an inline message strip at the bottom of the window.
- Quit confirmation uses an inline Yes/No bar, not a popup.

### Data-Driven Architecture (AAD)
- Every action is defined in a JSON file under `data/actions/` — no hardcoded if/elif chains.
- Resolvers are auto-discovered at startup. Adding a new action = two files, zero engine edits.
- Full audit trail: every dispatched action logs a `DATA` event with resolver and context.

---

## Requirements

- Python 3.10 or higher
- Tkinter (bundled with standard Python distributions)
- No third-party packages required for the game itself
- PyInstaller (optional, for building the `.exe` — install via `pip install pyinstaller`)

---

## How to Run

```
python main.pyw
```

Debug mode (verbose dispatcher output):
```
python main.pyw --debug
```

Developer tools:
```
python DevTools.pyw
```

---

## Community & Links

- **Play on Itch.io**: [jacktheyoutuber.itch.io/pursuit-of-peace](https://jacktheyoutuber.itch.io/pursuit-of-peace)
- **Discord**: [Join the community](https://discord.gg/HPVcBv5Dma)
- **Subreddit**: [r/PursuitOfPeaceGame](https://www.reddit.com/r/PursuitOfPeaceGame/)

---

## Development

See `docs/CONTRIBUTING.md` to add new actions, items, enemies, and locations — most require no Python changes.

See `docs/ARCHITECTURE.md` for the full AAD system, data-flow diagram, and file-by-file breakdown.

See `docs/DEVTOOLS_GUIDE.md` for how to use every tab in DevTools.

See `docs/BUILD_PROCESS.md` for building a standalone `.exe`.

See `docs/UI_SYSTEM.md` for the UI component system and how to add new views.
