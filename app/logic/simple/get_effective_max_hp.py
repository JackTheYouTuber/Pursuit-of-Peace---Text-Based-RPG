"""
get_effective_max_hp — compute the true HP ceiling for any entity.

Adds active max_hp buff bonuses to the base max_hp field.
Does not know what entity this is.
"""
from typing import Dict
from app.logic.simple.get_buff_bonus import get_buff_bonus


def get_effective_max_hp(state: Dict) -> int:
    return state.get("max_hp", 20) + get_buff_bonus(state, "max_hp")
