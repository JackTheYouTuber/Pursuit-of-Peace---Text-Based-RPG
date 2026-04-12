"""set_location — update the player's current_location_id."""
from typing import Dict

def set_location(state: Dict, location_id: str) -> Dict:
    s = dict(state)
    s["current_location_id"] = location_id
    return s
