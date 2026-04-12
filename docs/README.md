# Pursuit of Peace — Text-Based RPG  `v1.0.0`

A single-player, turn-based text RPG built with Python and Tkinter. You play as a citizen of a walled city who must survive year-to-year — managing gold, equipping gear, exploring dungeons, and paying taxes to avoid permanent exile.

Death is permanent. Exile is permanent. Every run counts.

---

## Features (v1.0.0)

### Core Survival Loop
- **Year system** — every 30 actions a year passes. Pay your taxes at City Hall or face permanent exile.
- **Permanent death** — dying in the dungeon deletes your save file. No second chances.
- **Roguelike identity** — each profile is a unique run. Losing a profile means starting fresh.

### City & Economy (Tier 4)
- **Buy items** at the Marketplace, Alchemy Hall, and Blacksmith's Street. Each location stocks different goods.
- **Sell items** from your inventory for 40% of base value.
- **Repair gear** at the Blacksmith — cost scales with damage taken.
- **Pay taxes** at City Hall before year end.
- **Rest** at the Tavern to restore full HP.
- **Take a bath** at the Public Bath for a dungeon-run buff (+5 max HP).
- **Go fishing** at the River for a chance to catch sellable fish.

### Dungeon Exploration
- Procedurally generated dungeons with variable room counts and depths.
- Enemy encounters, item pickups, and room-by-room traversal.
- Flee the dungeon at any time (one_run buffs expire on exit).

### Combat (Tier 1–3)
- Turn-based combat with enemy counter-attacks.
- Weapon damage bonus + buff bonus + base roll determine your attack.
- Armor absorbs incoming damage (minimum 1 always lands).
- Durability decay: weapons and armor degrade per hit. Broken gear auto-unequips with a warning.
- Use consumable items mid-combat without ending your turn.

### Equipment System (Tier 3)
- Two equipment slots: weapon and armor.
- Equip from inventory; old item is returned to inventory automatically.
- Stats shown in player panel and inventory with durability bars.

### Consumables & Buffs (Tier 2)
- Healing tonics, bandages, rations, strength draughts, antidotes.
- Buff durations: `turns` (decrements per attack), `one_run` (expires on dungeon exit), `permanent`.
- Buff summary visible in player panel at all times.

### Data-Driven Architecture (Tier 4 — AAD)
- Every action is defined in a JSON file under `data/actions/` — no hardcoded if/elif chains.
- Resolvers auto-discovered at startup. Adding a new action = two files, zero engine edits.
- Full audit trail: every dispatched action logs a `DATA` event with resolver and context.

---

## Requirements

- Python 3.10 or higher
- Tkinter (bundled with standard Python distributions)
- No third-party packages required

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

## For Developers & Modders

See `docs/CONTRIBUTING.md` for how to add new actions, shops, enemies, and items — most require no Python changes.

See `docs/ARCHITECTURE.md` for a full description of the AAD system and data flow.
