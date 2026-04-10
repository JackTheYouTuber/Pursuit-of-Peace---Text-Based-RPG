"""
BuffMgr — middle management for buff/debuff state.

Receives orders from Core (apply this effect, tick buffs, expire run buffs).
Coordinates Simple units (apply_buff, remove_buff, tick_buffs, expire_run_buffs).
Validates orders (can this effect be applied? does the buff already exist?).
Answers stat queries (what is the current damage bonus?).
"""
from typing import Dict, List, Tuple

from app.logic.simple.apply_buff       import apply_buff
from app.logic.simple.remove_buff      import remove_buff
from app.logic.simple.tick_buffs       import tick_buffs
from app.logic.simple.expire_run_buffs import expire_run_buffs
from app.logic.simple.parse_effect     import parse_effect


class BuffMgr:
    # -- Stat queries ---------------------------------------------------
    def damage_bonus(self, state: Dict) -> int:
        return sum(b.get("stat_mods", {}).get("damage_bonus", 0)
                   for b in state.get("buffs", []))

    def max_hp_bonus(self, state: Dict) -> int:
        return sum(b.get("stat_mods", {}).get("max_hp", 0)
                   for b in state.get("buffs", []))

    def defense_bonus(self, state: Dict) -> int:
        return sum(b.get("stat_mods", {}).get("defense_bonus", 0)
                   for b in state.get("buffs", []))

    def summary(self, state: Dict) -> str:
        buffs = state.get("buffs", [])
        if not buffs:
            return ""
        parts = []
        for b in buffs:
            label = b.get("label", b.get("id", "?"))
            dur   = b.get("duration", "")
            if dur == "turns":
                parts.append(f"{label} ({b.get('duration_remaining','?')} turns)")
            elif dur == "one_run":
                parts.append(f"{label} (until exit)")
            else:
                parts.append(label)
        return ", ".join(parts)

    # -- Apply a parsed effect to state ---------------------------------
    def apply_effect(self, state: Dict, parsed: Dict) -> Tuple[Dict, str]:
        """
        Given a parsed effect dict from parse_effect(), apply it to state.
        Returns (new_state, result_message).
        """
        kind = parsed.get("type")

        if kind == "heal":
            # Healing is handled by heal_player in combat_mgr / player_mgr;
            # we only handle buff-related effects here.
            return state, ""

        if kind == "buff_damage":
            amount = parsed.get("value", 0)
            turns  = parsed.get("turns", 3)
            buff = {
                "id": "strength_boost",
                "label": f"Strength +{amount}",
                "stat_mods": {"damage_bonus": amount},
                "duration": "turns",
                "duration_remaining": turns,
            }
            s = apply_buff(state, buff)
            return s, f"Damage +{amount} for {turns} turns."

        if kind == "remove_debuff":
            target = parsed.get("target", "")
            had = any(b.get("id") == target for b in state.get("buffs", []))
            s = remove_buff(state, target)
            return s, f"{target.capitalize()} cleansed." if had else f"You weren't {target}."

        return state, ""

    # -- Lifecycle calls ------------------------------------------------
    def tick(self, state: Dict) -> Tuple[Dict, List[str]]:
        return tick_buffs(state)

    def expire_run(self, state: Dict) -> Tuple[Dict, List[str]]:
        return expire_run_buffs(state)

    def add(self, state: Dict, buff: Dict) -> Dict:
        return apply_buff(state, buff)

    def remove(self, state: Dict, buff_id: str) -> Dict:
        return remove_buff(state, buff_id)
