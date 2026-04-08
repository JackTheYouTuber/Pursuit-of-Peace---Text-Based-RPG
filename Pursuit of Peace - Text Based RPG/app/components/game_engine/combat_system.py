# app/components/game_engine/combat_system.py
import random
from typing import Dict, Tuple, List, Optional

class CombatSystem:
    """Handles combat logic and maintains a persistent log."""

    def __init__(self, logger=None):
        self._logger = logger
        self._log_lines: List[str] = []
        self._active_combat_state: Optional[Dict] = None

    def start_combat(self, enemy: Dict) -> Dict:
        """Initialize combat state for an enemy."""
        self._log_lines = [f"A {enemy.get('name', 'creature')} bars your path!"]
        self._active_combat_state = {
            "enemy": enemy,
            "enemy_current_hp": enemy.get("hp", 10),
            "log_text": "\n".join(self._log_lines),
        }
        if self._logger:
            self._logger.data("combat_start", enemy.get("id"))
        return self._active_combat_state

    def attack(self, player_damage: int) -> Tuple[Dict, bool, str]:
        """
        Perform an attack, update HP.
        Returns (updated_combat_state, combat_ended, message)
        """
        if not self._active_combat_state:
            raise RuntimeError("No active combat")
        enemy = self._active_combat_state["enemy"]
        new_hp = self._active_combat_state["enemy_current_hp"] - player_damage
        msg = f"You strike the {enemy['name']} for {player_damage} damage!"
        self._log_lines.append(msg)

        if new_hp <= 0:
            self._log_lines.append(f"The {enemy['name']} falls.")
            combat_ended = True
            self._active_combat_state["enemy_current_hp"] = 0
        else:
            combat_ended = False
            self._active_combat_state["enemy_current_hp"] = new_hp

        self._active_combat_state["log_text"] = "\n".join(self._log_lines)
        if self._logger:
            self._logger.data("combat_attack", {"damage": player_damage, "remaining_hp": new_hp})
        return self._active_combat_state, combat_ended, msg

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