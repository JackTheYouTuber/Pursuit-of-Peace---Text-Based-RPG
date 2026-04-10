"""
CombatMgr — middle management for combat state.

Holds the active combat session. Coordinates Simples (damage_player,
heal_player, decay_durability, increment_kills, add_gold, add_item).
Coordinates BuffMgr (tick, damage bonus, defense bonus).
Returns structured results — never raises.
"""
import random
from typing import Dict, List, Optional, Tuple

from app.logic.simple.damage_player    import damage_player
from app.logic.simple.decay_durability import decay_durability
from app.logic.simple.increment_kills  import increment_kills
from app.logic.simple.add_gold         import add_gold
from app.logic.simple.add_item         import add_item


class CombatMgr:
    def __init__(self, item_loader, buff_mgr):
        self._items   = item_loader
        self._buffs   = buff_mgr
        self._state:  Optional[Dict] = None
        self._log:    List[str] = []

    # -- Session --------------------------------------------------------
    def start(self, enemy: Dict, player_hp: int, player_max_hp: int,
              equipped_weapon: Optional[Dict], equipped_armor: Optional[Dict]) -> Dict:
        self._log = [f"A {enemy.get('name','?')} bars your path!"]
        self._state = {
            "enemy": enemy,
            "enemy_current_hp": enemy.get("hp", 10),
            "player_current_hp": player_hp,
            "player_max_hp": player_max_hp,
            "player_dead": False,
            "equipped_weapon": equipped_weapon,
            "equipped_armor":  equipped_armor,
        }
        return self._snapshot()

    def clear(self):
        self._state = None
        self._log   = []

    def active(self) -> bool:
        return self._state is not None

    def snapshot(self) -> Optional[Dict]:
        return self._snapshot() if self._state else None

    def log_text(self) -> str:
        return "\n".join(self._log)

    # -- Attack round ---------------------------------------------------
    def attack(self, player_state: Dict) -> Tuple[Dict, Dict, bool, bool]:
        """
        Execute one round: player attacks, enemy retaliates.
        Returns (updated_player_state, combat_snapshot, combat_ended, player_dead).
        """
        assert self._state, "No active combat"
        cs     = self._state
        enemy  = cs["enemy"]
        ps     = dict(player_state)

        # --- Player hits enemy ---
        base   = random.randint(4, 8)
        bonus  = self._buffs.damage_bonus(ps)
        weapon_bonus = 0
        weapon_name  = "bare hands"
        ew = cs.get("equipped_weapon")
        if ew and ew.get("current_durability", 0) > 0:
            weapon_bonus = ew.get("item", {}).get("stat_bonus", {}).get("damage", 0)
            weapon_name  = ew.get("item", {}).get("name", "weapon")

        total_dmg = base + bonus + weapon_bonus
        cs["enemy_current_hp"] -= total_dmg

        detail = f"({base}+{bonus} buff+{weapon_bonus} {weapon_name})" if (bonus or weapon_bonus) else ""
        self._log.append(f"You strike {enemy['name']} for {total_dmg}. {detail}".rstrip())

        # Decay weapon
        if ew and ew.get("current_durability", 0) > 0:
            ps, broke = decay_durability(ps, "equipped_weapon")
            cs["equipped_weapon"] = ps.get("equipped_weapon")
            if broke:
                cs["equipped_weapon"] = None
                self._log.append(f"⚠ Your {weapon_name} breaks!")

        # --- Enemy dies ---
        if cs["enemy_current_hp"] <= 0:
            cs["enemy_current_hp"] = 0
            self._log.append(f"The {enemy['name']} falls.")
            ps = self._award(ps, enemy)
            ps, expired = self._buffs.tick(ps)
            if expired:
                self._log.append("Buff expired: " + ", ".join(expired))
            return ps, self._snapshot(), True, False

        # --- Enemy counter-attacks ---
        raw = random.randint(enemy.get("damage_min", 1), enemy.get("damage_max", 3))
        defense = self._buffs.defense_bonus(ps)
        armor_val = 0
        armor_name = ""
        ea = cs.get("equipped_armor")
        if ea and ea.get("current_durability", 0) > 0:
            armor_val  = ea.get("item", {}).get("stat_bonus", {}).get("defense", 0)
            armor_name = ea.get("item", {}).get("name", "armor")

        absorbed = min(raw - 1, defense + armor_val)  # minimum 1 always lands
        received = raw - absorbed
        cs["player_current_hp"] -= received

        if absorbed > 0:
            self._log.append(f"{enemy['name']} strikes {raw}. "
                             f"{armor_name} absorbs {absorbed}. You take {received}.")
            ps, broke = decay_durability(ps, "equipped_armor")
            cs["equipped_armor"] = ps.get("equipped_armor")
            if broke:
                cs["equipped_armor"] = None
                self._log.append(f"⚠ Your {armor_name} breaks!")
        else:
            self._log.append(f"{enemy['name']} strikes you for {received}.")

        ps, dead = damage_player(ps, received)
        cs["player_current_hp"] = ps.get("hp", 0)

        if dead:
            cs["player_dead"] = True
            self._log.append("You collapse. Everything goes dark.")

        ps, expired = self._buffs.tick(ps)
        if expired:
            self._log.append("Buff expired: " + ", ".join(expired))

        return ps, self._snapshot(), dead, dead

    # -- Flee -----------------------------------------------------------
    def flee(self) -> str:
        self._log.append("You flee!")
        return "You flee from combat."

    # -- Internals ------------------------------------------------------
    def _snapshot(self) -> Dict:
        cs = self._state
        return {
            "enemy": cs["enemy"],
            "enemy_current_hp": cs["enemy_current_hp"],
            "player_current_hp": cs["player_current_hp"],
            "player_max_hp": cs["player_max_hp"],
            "player_dead": cs["player_dead"],
            "log_text": "\n".join(self._log),
            "equipped_weapon": cs.get("equipped_weapon"),
            "equipped_armor":  cs.get("equipped_armor"),
        }

    def _award(self, player_state: Dict, enemy: Dict) -> Dict:
        ps = increment_kills(player_state)
        gmin = enemy.get("gold_min", max(1, enemy.get("hp", 10) // 4))
        gmax = enemy.get("gold_max", max(2, enemy.get("hp", 10) // 2))
        gold = random.randint(int(gmin), int(gmax))
        ps, _ = add_gold(ps, gold)
        self._log.append(f"You loot {gold}g.")

        loot_table = enemy.get("loot_table", [])
        chance     = enemy.get("loot_chance", 0.6)
        count      = enemy.get("loot_count", 1)
        if loot_table and random.random() < chance:
            for _ in range(int(count)):
                item_id = random.choice(loot_table)
                item    = self._items.get(item_id)
                if item:
                    ps = add_item(ps, item_id)
                    self._log.append(f"Dropped: {item['name']}.")
        return ps
