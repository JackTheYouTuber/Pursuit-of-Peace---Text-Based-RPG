# Pursuit of Peace — Text-Based RPG  `v0.9.5`

A single-player, turn-based text RPG built with Python and Tkinter. You play as a citizen of a walled city who must survive year-to-year by managing gold, exploring dungeons, equipping weapons and armour, using consumables, and paying taxes to avoid permanent exile.

---

## Requirements

- Python 3.10 or higher
- Tkinter (bundled with most Python distributions)
- No third-party packages required to play

---

## Community & Links

- **Play on Itch.io**: [jacktheyoutuber.itch.io/pursuit-of-peace](https://jacktheyoutuber.itch.io/pursuit-of-peace)
- **Discord**: [Join the community](https://discord.gg/HPVcBv5Dma)
- **Subreddit**: [r/PursuitOfPeaceGame](https://www.reddit.com/r/PursuitOfPeaceGame/)

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
2. Navigate city locations to earn gold, sell loot, rest, and prepare for the dungeon.
3. Descend into the dungeon to fight enemies, collect items, and earn gold.
4. Equip weapons and armour from your inventory to improve combat performance.
5. Use consumables (bandages, potions, antidotes) to stay alive.
6. Pay your annual taxes at City Hall before year-end or face permanent exile.

### City Locations

| Location | What you can do |
|---|---|
| City Gates | Navigate to all other areas |
| Tavern | Rest to restore full HP (costs gold); hear rumours |
| Marketplace | Sell unwanted items for gold |
| Alchemy Hall | Sell reagents and other goods |
| Blacksmiths Street | Repair damaged weapons and armour |
| City Hall | Pay annual taxes; check outstanding debt |
| Public Bathhouse | Buy the Refreshed buff (+5 max HP for one dungeon run) |
| The River | Go fishing — catch items you can sell |
| Dungeon Entrance | Enter the dungeon |

> **Note:** The Coliseum is present in the world but its events are not yet implemented.

### The Dungeon

- A randomly generated sequence of rooms (5–12 rooms per run).
- Rooms contain an enemy, an item, or are empty.
- Enemies scale in difficulty with depth. Deeper rooms spawn stronger enemies.
- **Fight** an enemy to earn gold and a chance at loot drops.
- **Flee** to exit the dungeon immediately without reward.
- Clearing all rooms exits the dungeon and returns you to the city.

### Combat

Each combat round:
- Your attack damage = base roll (4–8) + equipped weapon bonus + any active strength buffs.
- Enemy damage received = enemy roll − equipped armour defence (minimum 1 damage always lands).
- Weapon and armour **durability** decreases with each hit. Items break at 0 and must be repaired at the Blacksmith.

During combat you can also **use consumable items** directly from your inventory without ending the round.

### Equipment

- Open **Inventory** to see your currently equipped weapon and armour, with a durability bar (`[████░░░░]`).
- Click any weapon or armour in the list and press **Equip**. The previously equipped item returns to inventory.
- Use **Unequip** buttons in the equipment summary to return items to your bag.
- Repair damaged gear at the **Blacksmith**. Cost = missing durability points × repair rate.

### Buffs & Debuffs

Active effects are shown in the player sidebar under **Effects**. Examples:
- `Refreshed (until exit)` — max HP +5 for the current dungeon run (from the Public Bath).
- `Strength +3 (2 turns)` — damage bonus for the next 2 attack rounds (from Muscle Draught).

### Taxes & Exile

- One tax bill is due per in-game year (default: 100 gold).
- Pay at **City Hall** before year-end.
- If unpaid when the year rolls over, you are exiled — **game over, profile deleted**.

---

## Profile System

- On launch, a dialog lets you select an existing profile or create a new one.
- Profiles are saved as JSON files in `data/player/profiles/`.
- Use **File → Save Game** to save manually at any time.
- Use **File → Load Game** to switch profiles mid-session.
- **Death is permanent.** If you are killed in combat, your profile file is deleted.

---

## Project Layout

```
main.pyw                    Entry point — run this to play
DevTools.pyw                Developer utilities (audit, build, pycache cleaner)
app/                        Application source code
data/                       All game data (JSON — fully moddable)
docs/                       Project documentation
logs/                       Session log files (auto-created at runtime)
```

See `docs/ARCHITECTURE.md` for a full breakdown of the source tree.

---

## Modding

All game content lives in JSON files under `data/`. You can add enemies, items, lore, and locations without touching any Python code. See `docs/CONTRIBUTING.md` for step-by-step guides.
