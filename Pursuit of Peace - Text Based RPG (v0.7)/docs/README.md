# Pursuit of Peace — Text-Based RPG  `v0.7`

A single-player, turn-based text RPG built with Python and Tkinter. You play as a citizen of a walled city who must survive year-to-year by managing gold, exploring dungeons, and paying taxes to avoid exile.

---

## Requirements

- Python 3.10 or higher
- Tkinter (bundled with most Python distributions)
- No third-party packages required

---

## How to Run

From the project root directory:

```
python main.pyw
```

Or double-click `main.pyw` on Windows if Python is associated with `.pyw` files. The `.pyw` extension suppresses the console window on Windows.

---

## Game Overview

### Core Loop
1. You start at the City Gates each session.
2. Navigate to city locations to earn gold, buy items, rest, and gather information.
3. Descend into the dungeon to fight enemies and collect loot.
4. Pay your annual taxes at City Hall before year-end or face permanent exile (game over).

### City Locations

| Location | Key Actions |
|---|---|
| City Gates | Navigate to all other areas |
| Tavern | Rest (restore HP, costs gold), hear rumors |
| Marketplace | Buy and sell items |
| Alchemy Hall | Buy potions, sell reagents, craft consumables |
| Blacksmiths Street | Buy weapons/armour, repair equipment |
| City Hall | Pay annual taxes, view tax debt |
| Coliseum | Arena events, wager gold |
| Public Bath | Buy a cleanliness buff |
| The River | Go fishing for items |
| Dungeon Entrance | Enter the dungeon |

### The Dungeon
- A randomly generated sequence of rooms (5–12 rooms per run).
- Rooms can contain an enemy, an item, or be empty.
- Enemies scale in difficulty with room depth.
- You can fight or flee. Fleeing exits the dungeon immediately.
- Clearing all rooms exits the dungeon and returns you to the city.

### Taxes & Exile
- Each year, a tax is due (default: 100 gold).
- Pay at City Hall before year-end.
- If unpaid at year rollover, you are exiled — **game over**.

---

## Profile System

- On launch, a dialog lets you select an existing profile or create a new one.
- Profiles are saved as JSON files in `data/player/profiles/`.
- Use **File → Save Game** to save manually at any time.
- Use **File → Load Game** to switch profiles mid-session.

---

## Project Layout

```
main.pyw                    Entry point
app/                        Application source code
data/                       All game data (JSON)
logs/                       Session log files (auto-created)
Docs/                       Project documentation
```

See `Docs/ARCHITECTURE.md` for a full breakdown of the source tree.
