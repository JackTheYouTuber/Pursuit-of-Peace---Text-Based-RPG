# app/components/game_engine/combat_system.py
"""
CombatSystem — full combat logic.

Tier 1 (v0.7) — enemy counter-attack, player death detection.
Tier 3 (v0.9) — weapon damage scaling, armor damage reduction,
                 weapon/armor durability decay.

Death handling: player_dead=True is set in combat state;
callers are responsible for calling end_combat(player_dead=True)
which will trigger profile deletion via the engine.
"""
import random
from typing import Dict, Tuple, List, Optional


class CombatSystem:
    def __init__(self, logger=None):
        self._logger = logger
        self._log_lines: List[str] = []
        self._active_combat_state: Optional[Dict] = None

    # ------------------------------------------------------------------
    # Start / clear
    # ------------------------------------------------------------------
    def start_combat(self, enemy: Dict, player_hp: int, player_max_hp: int,
                     equipped_weapon: Optional[Dict] = None,
                     equipped_armor: Optional[Dict] = None) -> Dict:
        self._log_lines = [f"A {enemy.get('name', 'creature')} bars your path!"]
        self._active_combat_state = {
            "enemy": enemy,
            "enemy_current_hp": enemy.get("hp", 10),
            "player_current_hp": player_hp,
            "player_max_hp": player_max_hp,
            "player_dead": False,
            "log_text": "\n".join(self._log_lines),
            # equipment refs (mutable dicts, modified in-place for durability)
            "equipped_weapon": equipped_weapon,
            "equipped_armor": equipped_armor,
        }
        if self._logger:
            self._logger.data("combat_start", enemy.get("id"))
        return self._active_combat_state

    def clear_combat(self):
        self._active_combat_state = None
        self._log_lines = []

    # ------------------------------------------------------------------
    # Core attack
    # ------------------------------------------------------------------
    def attack(self, base_player_damage: int) -> Tuple[Dict, bool, str, int]:
        """
        Execute one combat round (player attacks, enemy retaliates).
        Returns (updated_combat_state, combat_ended, message, hp_lost_to_enemy).
        combat_ended=True if enemy dies OR player dies.
        Check state['player_dead'] to distinguish.
        """
        if not self._active_combat_state:
            raise RuntimeError("No active combat")

        state = self._active_combat_state
        enemy = state["enemy"]

        # ── Player attacks ──────────────────────────────────────────────
        weapon_bonus = 0
        weapon_label = "bare hands"
        ew = state.get("equipped_weapon")
        if ew and ew.get("current_durability", 0) > 0:
            weapon_bonus = ew.get("item", {}).get("stat_bonus", {}).get("damage", 0)
            weapon_label = ew.get("item", {}).get("name", "weapon")

        total_player_damage = base_player_damage + weapon_bonus
        new_enemy_hp = state["enemy_current_hp"] - total_player_damage

        if weapon_bonus > 0:
            self._log_lines.append(
                f"You strike the {enemy['name']} for {total_player_damage} damage! "
                f"({base_player_damage} + {weapon_bonus} from {weapon_label})"
            )
        else:
            self._log_lines.append(
                f"You strike the {enemy['name']} for {total_player_damage} damage!"
            )

        # Degrade weapon durability
        if ew and ew.get("current_durability", 0) > 0:
            ew["current_durability"] -= 1
            if ew["current_durability"] <= 0:
                self._log_lines.append(
                    f"⚠ Your {ew.get('item', {}).get('name', 'weapon')} has broken!"
                )
                state["equipped_weapon"] = None

        if new_enemy_hp <= 0:
            state["enemy_current_hp"] = 0
            self._log_lines.append(f"The {enemy['name']} falls.")
            state["log_text"] = "\n".join(self._log_lines)
            if self._logger:
                self._logger.data("combat_victory", {"enemy": enemy.get("id")})
            return state, True, "\n".join(self._log_lines[-3:]), 0

        state["enemy_current_hp"] = new_enemy_hp

        # ── Enemy counter-attacks ───────────────────────────────────────
        dmg_min = enemy.get("damage_min", 1)
        dmg_max = enemy.get("damage_max", 3)
        raw_enemy_damage = random.randint(dmg_min, dmg_max)

        armor_defense = 0
        armor_label = ""
        ea = state.get("equipped_armor")
        if ea and ea.get("current_durability", 0) > 0:
            armor_defense = ea.get("item", {}).get("stat_bonus", {}).get("defense", 0)
            armor_label = ea.get("item", {}).get("name", "armor")

        damage_received = max(1, raw_enemy_damage - armor_defense)
        hp_lost = damage_received

        if armor_defense > 0:
            self._log_lines.append(
                f"The {enemy['name']} strikes for {raw_enemy_damage}! "
                f"Your {armor_label} absorbs {armor_defense}. You take {damage_received} HP."
            )
            # Degrade armor durability
            ea["current_durability"] -= 1
            if ea["current_durability"] <= 0:
                self._log_lines.append(
                    f"⚠ Your {ea.get('item', {}).get('name', 'armor')} has broken!"
                )
                state["equipped_armor"] = None
        else:
            self._log_lines.append(
                f"The {enemy['name']} strikes back for {damage_received} damage!"
            )

        new_player_hp = state["player_current_hp"] - damage_received

        if new_player_hp <= 0:
            new_player_hp = 0
            state["player_dead"] = True
            self._log_lines.append("You collapse. Everything goes dark.")
            if self._logger:
                self._logger.data("player_death", {"enemy": enemy.get("id")})

        state["player_current_hp"] = new_player_hp
        state["log_text"] = "\n".join(self._log_lines)

        combat_ended = state["player_dead"]

        if self._logger:
            self._logger.data("combat_attack", {
                "player_damage": total_player_damage,
                "enemy_hp_remaining": new_enemy_hp,
                "enemy_damage": damage_received,
                "player_hp_remaining": new_player_hp,
            })

        return state, combat_ended, "\n".join(self._log_lines[-3:]), hp_lost

    # ------------------------------------------------------------------
    # Flee
    # ------------------------------------------------------------------
    def flee(self) -> Tuple[bool, str]:
        self._log_lines.append("You run away!")
        if self._active_combat_state:
            self._active_combat_state["log_text"] = "\n".join(self._log_lines)
        if self._logger:
            self._logger.data("combat_flee")
        return True, "You flee from combat."

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------
    def get_log_text(self) -> str:
        return "\n".join(self._log_lines) if self._log_lines else ""

    def get_combat_state(self) -> Optional[Dict]:
        return self._active_combat_state
