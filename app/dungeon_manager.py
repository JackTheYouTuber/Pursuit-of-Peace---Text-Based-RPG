import random


class DungeonManager:
    """
    Generates and manages a single dungeon run.

    A run is a sequence of rooms drawn from room_templates.json.
    Room count is random between min_rooms and max_rooms (dungeon/config.json).
    Each room has a depth level starting at 1; deeper rooms spawn harder enemies.
    No map is exposed — the player sees only the current room.
    Exiting returns the player to the city entrance via LocationManager.
    """

    def __init__(self, data_loader, logger=None):
        self._loader = data_loader
        self._logger = logger

    # ------------------------------------------------------------------
    # Run generation
    # ------------------------------------------------------------------

    def generate(self):
        """
        Build a new dungeon run. Returns a dungeon_state dict:
        {
            "rooms":        [room_state, ...],   # ordered list
            "total_rooms":  int,
            "current_index": 0,
            "active":       True,
        }
        Each room_state:
        {
            "depth":      int,
            "template_id": str,
            "lore_key":   str,
            "has_enemy":  bool,
            "has_item":   bool,
            "enemy":      dict | None,
            "item":       dict | None,
            "cleared":    bool,
        }
        """
        config = self._loader.get_dungeon_config()
        min_rooms = config.get("min_rooms", 5)
        max_rooms = config.get("max_rooms", 12)
        max_depth = config.get("max_depth", 5)

        total_rooms = random.randint(min_rooms, max_rooms)
        templates = self._loader.get_room_templates()

        if not templates:
            if self._logger:
                self._logger.warn(
                    "No room templates found. Generating empty dungeon.",
                    context="DungeonManager.generate",
                )
            templates = [
                {"id": "room_fallback", "has_enemy": False, "has_item": False,
                 "lore_key": "lore_room_empty_01"}
            ]

        rooms = []
        for i in range(total_rooms):
            depth = self._depth_for_room(i, total_rooms, max_depth)
            template = random.choice(templates)

            enemy = None
            item = None

            if template.get("has_enemy"):
                enemy = self._pick_enemy(depth)

            if template.get("has_item"):
                item = self._pick_item(depth)

            room_state = {
                "depth": depth,
                "template_id": template.get("id", "room_unknown"),
                "lore_key": template.get("lore_key", ""),
                "has_enemy": template.get("has_enemy", False),
                "has_item": template.get("has_item", False),
                "enemy": enemy,
                "item": item,
                "cleared": False,
            }
            rooms.append(room_state)

        dungeon_state = {
            "rooms": rooms,
            "total_rooms": total_rooms,
            "current_index": 0,
            "active": True,
        }

        if self._logger:
            self._logger.info(
                f"Dungeon generated: {total_rooms} rooms, max depth {max_depth}."
            )

        return dungeon_state

    # ------------------------------------------------------------------
    # Room traversal
    # ------------------------------------------------------------------

    def get_current_room(self, dungeon_state):
        """Return the current room_state dict, or None if run is over."""
        idx = dungeon_state.get("current_index", 0)
        rooms = dungeon_state.get("rooms", [])
        if idx >= len(rooms):
            return None
        return rooms[idx]

    def advance_room(self, dungeon_state):
        """
        Move to the next room.
        Returns (updated_dungeon_state, at_exit).
        at_exit is True when the player has cleared all rooms.
        """
        state = dict(dungeon_state)
        state["rooms"] = list(state["rooms"])

        next_index = state["current_index"] + 1

        if next_index >= state["total_rooms"]:
            state["active"] = False
            if self._logger:
                self._logger.info("Dungeon run complete — all rooms cleared.")
            return state, True

        state["current_index"] = next_index
        return state, False

    def mark_room_cleared(self, dungeon_state):
        """Mark the current room as cleared. Returns updated dungeon_state."""
        state = dict(dungeon_state)
        rooms = list(state["rooms"])
        idx = state["current_index"]
        if 0 <= idx < len(rooms):
            room = dict(rooms[idx])
            room["cleared"] = True
            rooms[idx] = room
            state["rooms"] = rooms
        return state

    def exit_dungeon(self, dungeon_state):
        """Force-end the dungeon run regardless of progress."""
        state = dict(dungeon_state)
        state["active"] = False

        if self._logger:
            self._logger.info(
                f"Player exited dungeon early at room {state.get('current_index', 0) + 1}."
            )

        return state

    # ------------------------------------------------------------------
    # Lore resolution
    # ------------------------------------------------------------------

    def get_room_lore_text(self, room_state):
        """
        Resolve the lore entry for a room from data/lore/dungeon.json.
        Returns the text string, or empty string if not found.
        """
        lore_key = room_state.get("lore_key", "")
        if not lore_key:
            return ""

        entries = self._loader.get_lore("dungeon")
        for entry in entries:
            if entry.get("id") == lore_key:
                return entry.get("text", "")

        if self._logger:
            self._logger.warn(
                f"Lore key not found: '{lore_key}'",
                context="DungeonManager.get_room_lore_text",
            )
        return ""

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _depth_for_room(self, room_index, total_rooms, max_depth):
        """
        Map a room's sequential index to a depth level 1..max_depth.
        Rooms get progressively deeper as the player advances.
        """
        if total_rooms <= 1:
            return 1
        depth = 1 + int((room_index / (total_rooms - 1)) * (max_depth - 1))
        return max(1, min(depth, max_depth))

    def _pick_enemy(self, depth):
        """
        Filter enemies by min_depth <= depth <= max_depth, pick at random.
        Returns enemy dict or None if no candidates.
        """
        candidates = [
            e for e in self._loader.get_all_enemies()
            if e.get("min_depth", 1) <= depth <= e.get("max_depth", 99)
        ]
        if not candidates:
            if self._logger:
                self._logger.warn(
                    f"No enemies found for depth {depth}.",
                    context="DungeonManager._pick_enemy",
                )
            return None
        return dict(random.choice(candidates))

    def _pick_item(self, depth):
        """
        Filter items by min_depth <= depth, pick at random.
        Excludes fishing-source items (those are river-only).
        Returns item dict or None if no candidates.
        """
        candidates = [
            item for item in self._loader.get_all_items()
            if item.get("min_depth", 0) <= depth
            and item.get("source") != "fishing"
        ]
        if not candidates:
            if self._logger:
                self._logger.warn(
                    f"No items found for depth {depth}.",
                    context="DungeonManager._pick_item",
                )
            return None
        return dict(random.choice(candidates))
