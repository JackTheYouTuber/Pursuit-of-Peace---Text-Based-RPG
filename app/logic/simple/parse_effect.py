"""
Parse an item effect string into a structured dict.
One job: turn "Restores 10 hp" into {"type":"heal","value":10}.
Does not apply anything. Does not touch state.
"""
import re
from typing import Dict, Optional


def parse_effect(effect_text: str) -> Optional[Dict]:
    """
    Convert a plain-English effect string into a structured dict.

    Recognised patterns:
      "Restores X hp"            -> {"type": "heal",         "value": X}
      "Increases damage by X ..."-> {"type": "buff_damage",  "value": X, "turns": 3}
      "Removes the poisoned ..." -> {"type": "remove_debuff","target": "poisoned"}

    Returns None if the string matches no known pattern.
    """
    if not effect_text:
        return None
    text = effect_text.lower()

    m = re.search(r"restor(?:es?)?\s+(\d+)\s*hp", text)
    if m:
        return {"type": "heal", "value": int(m.group(1))}

    m = re.search(r"increases?\s+damage\s+by\s+(\d+)", text)
    if m:
        return {"type": "buff_damage", "value": int(m.group(1)), "turns": 3}

    if "removes" in text and "poison" in text:
        return {"type": "remove_debuff", "target": "poisoned"}

    return None
