# app/components/game_engine/state_manager.py
from typing import Dict, Any, Optional

class StateManager:
    """Manages player and dungeon state with validation."""

    def __init__(self, data_loader, logger=None):
        self._loader = data_loader
        self._logger = logger
        self._player_state: Dict[str, Any] = {}
        self._dungeon_state: Optional[Dict[str, Any]] = None

    def init_player(self) -> Dict[str, Any]:
        """Load default player state."""
        self._player_state = dict(self._loader.get_player_defaults())
        if "current_location_id" not in self._player_state:
            self._player_state["current_location_id"] = "city_entrance"
        if self._logger:
            self._logger.system("Player state initialised.")
        return self._player_state

    def get_player(self) -> Dict[str, Any]:
        return self._player_state

    def update_player(self, new_state: Dict[str, Any]) -> None:
        self._player_state = new_state

    def get_dungeon(self) -> Optional[Dict[str, Any]]:
        return self._dungeon_state

    def set_dungeon(self, dungeon_state: Optional[Dict[str, Any]]) -> None:
        self._dungeon_state = dungeon_state
        if self._logger and dungeon_state is None:
            self._logger.system("Dungeon state cleared.")

    def clear_dungeon(self) -> None:
        self._dungeon_state = None