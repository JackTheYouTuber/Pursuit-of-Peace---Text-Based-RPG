# app/components/game_engine/combat_system.py
import random
from typing import Dict, Tuple, List, Optional

class CombatSystem:
    """Handles combat logic and maintains a persistent log.

    v0.7 — [ISSUE-001] Enemy counter-attack: after the player attacks,
           the enemy retaliates using its damage_min/damage_max range.
           [ISSUE-002] Player death: the combat state now tracks
           player_current_hp; if it reaches 0 the round ends with
           player_dead=True so callers can show the game-over screen.
    """

    def __init__(self, logger=None):
        self._logger = logger
        self._log_lines: List[str] = []
        self._active_combat_state: Optional[Dict] = None

    def start_combat(self, enemy: Dict, player_hp: int, player_max_hp: int) -> Dict:
        """Initialize combat state for an enemy."""
        self._log_lines = [f"A {enemy.get('name', 'creature')} bars your path!"]
        self._active_combat_state = {
            "enemy": enemy,
            "enemy_current_hp": enemy.get("hp", 10),
            "player_current_hp": player_hp,
            "player_max_hp": player_max_hp,
            "player_dead": False,
            "log_text": "\n".join(self._log_lines),
        }
        if self._logger:
            self._logger.data("combat_start", enemy.get("id"))
        return self._active_combat_state

    def attack(self, player_damage: int) -> Tuple[Dict, bool, str, int]:
        """
        Perform an attack, then enemy retaliates.
        Returns (updated_combat_state, combat_ended, message, hp_lost_to_enemy)

        combat_ended is True when the enemy dies OR the player dies.
        Check state['player_dead'] to distinguish the two outcomes.
        """
        if not self._active_combat_state:
            raise RuntimeError("No active combat")

        enemy = self._active_combat_state["enemy"]
        hp_lost = 0

        # --- Player attacks enemy ---
        new_enemy_hp = self._active_combat_state["enemy_current_hp"] - player_damage
        self._log_lines.append(
            f"You strike the {enemy['name']} for {player_damage} damage!"
        )

        if new_enemy_hp <= 0:
            self._log_lines.append(f"The {enemy['name']} falls.")
            self._active_combat_state["enemy_current_hp"] = 0
            self._active_combat_state["log_text"] = "\n".join(self._log_lines)
            if self._logger:
                self._logger.data("combat_victory", {"enemy": enemy.get("id")})
            return self._active_combat_state, True, "\n".join(self._log_lines[-2:]), 0

        self._active_combat_state["enemy_current_hp"] = new_enemy_hp

        # --- Enemy counter-attacks player ---
        dmg_min = enemy.get("damage_min", 1)
        dmg_max = enemy.get("damage_max", 3)
        enemy_damage = random.randint(dmg_min, dmg_max)
        hp_lost = enemy_damage

        new_player_hp = self._active_combat_state["player_current_hp"] - enemy_damage
        self._log_lines.append(
            f"The {enemy['name']} strikes back for {enemy_damage} damage!"
        )

        if new_player_hp <= 0:
            new_player_hp = 0
            self._active_combat_state["player_dead"] = True
            self._log_lines.append("You collapse. Everything goes dark.")
            if self._logger:
                self._logger.data("player_death", {"enemy": enemy.get("id")})

        self._active_combat_state["player_current_hp"] = new_player_hp
        self._active_combat_state["log_text"] = "\n".join(self._log_lines)

        combat_ended = self._active_combat_state["player_dead"]
        msg = "\n".join(self._log_lines[-2:])

        if self._logger:
            self._logger.data("combat_attack", {
                "player_damage": player_damage,
                "enemy_hp_remaining": new_enemy_hp,
                "enemy_damage": enemy_damage,
                "player_hp_remaining": new_player_hp,
            })

        return self._active_combat_state, combat_ended, msg, hp_lost

    def flee(self) -> Tuple[bool, str]:
        """Attempt to flee combat."""
        self._log_lines.append("You run away!")
        self._active_combat_state["log_text"] = "\n".join(self._log_lines)
        if self._logger:
            self._logger.data("combat_flee")
        return True, "You flee from combat."

    def get_log_text(self) -> str:
        return "\n".join(self._log_lines) if self._log_lines else ""

    def get_combat_state(self) -> Optional[Dict]:
        return self._active_combat_state

    def clear_combat(self):
        self._active_combat_state = None
        self._log_lines = []
