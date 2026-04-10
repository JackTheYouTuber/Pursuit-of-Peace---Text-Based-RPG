# app/components/game_engine/buff_system.py
"""
BuffSystem — manages active buffs and debuffs on the player.

Buff object schema (stored in player_state["buffs"]):
{
  "id":                 str,          # unique buff type id
  "label":              str,          # display name
  "stat_mods":          {str: int},   # e.g. {"damage_bonus": 3, "max_hp": 5}
  "duration":           str,          # "turns" | "one_run" | "permanent"
  "duration_remaining": int | None,   # only used when duration == "turns"
}
"""
from typing import Dict, List, Tuple


class BuffSystem:
    def __init__(self, logger=None):
        self._logger = logger

    # ------------------------------------------------------------------
    # Derived stat helpers
    # ------------------------------------------------------------------
    def get_damage_bonus(self, player_state: Dict) -> int:
        """Sum all damage_bonus mods from active buffs."""
        return sum(b.get("stat_mods", {}).get("damage_bonus", 0)
                   for b in player_state.get("buffs", []))

    def get_max_hp_bonus(self, player_state: Dict) -> int:
        """Sum all max_hp mods from active buffs."""
        return sum(b.get("stat_mods", {}).get("max_hp", 0)
                   for b in player_state.get("buffs", []))

    def get_defense_bonus(self, player_state: Dict) -> int:
        """Sum all defense mods from active buffs."""
        return sum(b.get("stat_mods", {}).get("defense_bonus", 0)
                   for b in player_state.get("buffs", []))

    # ------------------------------------------------------------------
    # Buff management
    # ------------------------------------------------------------------
    def add_buff(self, player_state: Dict, buff: Dict) -> Dict:
        state = dict(player_state)
        buffs = list(state.get("buffs", []))
        # Remove existing buff with same id unless it stacks
        buffs = [b for b in buffs if b.get("id") != buff.get("id")]
        buffs.append(dict(buff))
        state["buffs"] = buffs
        return state

    def remove_buff(self, player_state: Dict, buff_id: str) -> Dict:
        state = dict(player_state)
        state["buffs"] = [b for b in state.get("buffs", []) if b.get("id") != buff_id]
        return state

    def tick_turn_buffs(self, player_state: Dict) -> Tuple[Dict, List[str]]:
        """Decrement duration-based buffs by 1 turn. Returns (new_state, expired_names)."""
        state = dict(player_state)
        buffs = []
        expired = []
        for buff in state.get("buffs", []):
            b = dict(buff)
            if b.get("duration") == "turns":
                rem = b.get("duration_remaining", 1) - 1
                if rem <= 0:
                    expired.append(b.get("label", b.get("id")))
                    continue
                b["duration_remaining"] = rem
            buffs.append(b)
        state["buffs"] = buffs
        return state, expired

    def expire_run_buffs(self, player_state: Dict) -> Tuple[Dict, List[str]]:
        """Remove all one_run buffs (called when leaving dungeon)."""
        state = dict(player_state)
        buffs = []
        expired = []
        for buff in state.get("buffs", []):
            if buff.get("duration") == "one_run":
                expired.append(buff.get("label", buff.get("id")))
            else:
                buffs.append(buff)
        state["buffs"] = buffs
        return state, expired

    def get_buff_summary(self, player_state: Dict) -> str:
        """Return a short human-readable list of active buffs."""
        buffs = player_state.get("buffs", [])
        if not buffs:
            return "No active effects."
        parts = []
        for b in buffs:
            label = b.get("label", b.get("id", "?"))
            dur = b.get("duration", "")
            if dur == "turns":
                rem = b.get("duration_remaining", "?")
                parts.append(f"{label} ({rem} turns)")
            elif dur == "one_run":
                parts.append(f"{label} (until exit)")
            else:
                parts.append(label)
        return ", ".join(parts)
