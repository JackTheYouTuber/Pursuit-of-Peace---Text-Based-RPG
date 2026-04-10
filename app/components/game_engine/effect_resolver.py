# app/components/game_engine/effect_resolver.py
"""
EffectResolver — applies item/buff effects to player state.

Supports:
  - heal:         restore HP (capped at max_hp)
  - damage:       deal direct damage (used by traps, etc.)
  - add_buff:     push a buff dict onto player_state["buffs"]
  - remove_buff:  remove matching buff by id
  - remove_poison: convenience alias for remove_buff "poisoned"
"""
import re
from typing import Dict, Tuple


class EffectResolver:
    def __init__(self, logger=None):
        self._logger = logger

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    def apply_item_effect(self, player_state: Dict, item: Dict) -> Tuple[Dict, str]:
        """Apply an item's effect to player_state.  Returns (new_state, msg)."""
        state = dict(player_state)
        effect_text = item.get("effect") or ""
        if not effect_text:
            return state, f"You used {item.get('name', 'item')} but nothing happened."

        msg = self._parse_and_apply(state, effect_text, item.get("name", "item"))
        if self._logger:
            self._logger.data("item_used", {"item": item.get("id"), "effect": effect_text})
        return state, msg

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _parse_and_apply(self, state: Dict, effect_text: str, item_name: str) -> str:
        text = effect_text.lower()

        # Healing: "Restores X hp" / "Restores X health"
        heal_match = re.search(r"restor(?:es?)?\s+(\d+)\s*hp", text)
        if heal_match:
            amount = int(heal_match.group(1))
            return self._apply_heal(state, amount, item_name)

        # Buff: "Increases damage by X for Y turns"
        str_match = re.search(r"increases? damage by (\d+)", text)
        if str_match:
            amount = int(str_match.group(1))
            buff = {
                "id": "strength_boost",
                "label": f"Strength +{amount}",
                "stat_mods": {"damage_bonus": amount},
                "duration": "turns",
                "duration_remaining": 3,
            }
            state.setdefault("buffs", [])
            # Remove existing strength boost (no stacking)
            state["buffs"] = [b for b in state["buffs"] if b.get("id") != "strength_boost"]
            state["buffs"].append(buff)
            return f"You used {item_name}! Damage +{amount} for 3 turns."

        # Remove poison / debuff
        if "removes" in text and "poison" in text:
            state.setdefault("buffs", [])
            before = len(state["buffs"])
            state["buffs"] = [b for b in state["buffs"] if b.get("id") != "poisoned"]
            if len(state["buffs"]) < before:
                return f"You used {item_name}. The poison is cleansed!"
            return f"You used {item_name} but you weren't poisoned."

        return f"You used {item_name}. ({effect_text})"

    @staticmethod
    def _apply_heal(state: Dict, amount: int, item_name: str) -> str:
        old_hp = state.get("hp", 0)
        max_hp = state.get("max_hp", 20)

        # Apply equipped-armor max_hp buff bonus
        bonus_max = sum(
            b.get("stat_mods", {}).get("max_hp", 0)
            for b in state.get("buffs", [])
        )
        effective_max = max_hp + bonus_max

        new_hp = min(old_hp + amount, effective_max)
        state["hp"] = new_hp
        gained = new_hp - old_hp
        return f"You used {item_name}. HP restored +{gained} (now {new_hp}/{effective_max})."
