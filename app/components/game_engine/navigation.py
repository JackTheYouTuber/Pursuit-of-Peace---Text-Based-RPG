# app/components/game_engine/navigation.py
from typing import Dict

class Navigation:
    """Handle movement between city locations and dungeon exit."""

    def __init__(self, location_manager, logger=None):
        self._location_mgr = location_manager
        self._logger = logger

    def navigate_to(self, player_state: Dict, location_id: str) -> Dict:
        """Change current location."""
        new_state = self._location_mgr.navigate_to(player_state, location_id)
        if self._logger:
            self._logger.data("navigation", {"to": location_id})
        return new_state

    def exit_dungeon(self, player_state: Dict) -> Dict:
        """Return to city entrance."""
        return self.navigate_to(player_state, "city_entrance")