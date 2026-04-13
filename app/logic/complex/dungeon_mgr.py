"""
DungeonMgr — middle management for dungeon traversal.

Validates dungeon state (is the player in a dungeon? is there an enemy here?).
Coordinates DungeonGen (room navigation) and ItemMgr (take item).
Returns structured results. Never raises.
"""
from typing import Dict, Optional, Tuple

from app.logic.simple.add_item    import add_item


class DungeonMgr:
    def __init__(self, dungeon_gen):
        self._gen = dungeon_gen

    def generate(self) -> Dict:
        return self._gen.generate()

    def current_room(self, dungeon: Dict) -> Optional[Dict]:
        return self._gen.current_room(dungeon)

    def take_item(self, player_state: Dict, dungeon: Dict) -> Tuple[Dict, Dict, str]:
        room = self._gen.current_room(dungeon)
        if not room or not room.get("has_item") or room.get("cleared"):
            return player_state, dungeon, "Nothing to take."
        item = room.get("item")
        if not item:
            return player_state, dungeon, "Nothing to take."
        ps = add_item(player_state, item["id"])
        d  = self._gen.mark_cleared(dungeon)
        return ps, d, f"You take: {item.get('name', item['id'])}."

    def next_room(self, dungeon: Dict) -> Tuple[Dict, bool, str]:
        d = self._gen.advance(dungeon)
        at_exit = self._gen.at_exit(d)
        msg = "You reach the dungeon exit." if at_exit else ""
        return d, at_exit, msg

    def mark_cleared(self, dungeon: Dict) -> Dict:
        return self._gen.mark_cleared(dungeon)

    def room_lore(self, room: Dict) -> str:
        return self._gen.room_lore_text(room)
