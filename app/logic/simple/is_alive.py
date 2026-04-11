"""
is_alive — check whether any entity still has HP above zero.

One job. Does not know what entity this is.
"""
from typing import Dict


def is_alive(state: Dict) -> bool:
    return state.get("hp", 0) > 0
