# app/components/game_engine/dungeon_actions.py
from typing import Dict, Tuple, Optional, Any

class DungeonActions:
    """Handle dungeon exploration actions: take item, next room, exit."""

    def __init__(self, data_loader, dungeon_manager, logger=None):
        self._loader = data_loader
        self._dungeon_mgr = dungeon_manager
        self._logger = logger

    def take_item(self, player_state: Dict, dungeon_state: Dict) -> Tuple[Dict, Dict, str]:
        """Take item from current room. Returns (new_player_state, new_dungeon_state, message)."""
        room = self._dungeon_mgr.get_current_room(dungeon_state)
        if not room or not room.get("item"):
            return player_state, dungeon_state, "Nothing to take here."

        item = room["item"]
        inventory = list(player_state.get("inventory", []))
        inventory.append(item["id"])
        new_player = dict(player_state)
        new_player["inventory"] = inventory

        new_dungeon = self._dungeon_mgr.mark_room_cleared(dungeon_state)

        if self._logger:
            self._logger.data("dungeon_take_item", item["id"])
        return new_player, new_dungeon, f"You picked up: {item.get('name', 'Item')}."

    def next_room(self, dungeon_state: Dict) -> Tuple[Dict, bool, str]:
        """Advance to next room. Returns (new_dungeon_state, at_exit, message)."""
        new_dungeon, at_exit = self._dungeon_mgr.advance_room(dungeon_state)
        if at_exit:
            return new_dungeon, True, "You emerge from the depths into daylight."
        return new_dungeon, False, ""

    def exit_dungeon(self, dungeon_state: Dict) -> Dict:
        """Force exit the dungeon."""
        new_dungeon = self._dungeon_mgr.exit_dungeon(dungeon_state)
        if self._logger:
            self._logger.info("Player exited dungeon early.")
        return new_dungeon