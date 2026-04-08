# app/game_engine.py
"""
Core game logic orchestrator. Delegates to modular components.
"""
import random
from typing import Dict, Any, Optional, Tuple

from app.components.game_engine.state_manager import StateManager
from app.components.game_engine.combat_system import CombatSystem
from app.components.game_engine.dungeon_actions import DungeonActions
from app.components.game_engine.location_actions import LocationActions
from app.components.game_engine.navigation import Navigation
from app.components.game_engine.view_builder import ViewBuilder

class GameEngine:
    def __init__(self, data_loader, location_manager, dungeon_manager, logger=None):
        self._loader = data_loader
        self._location_mgr = location_manager
        self._dungeon_mgr = dungeon_manager
        self._logger = logger

        # Components
        self._state_mgr = StateManager(data_loader, logger)
        self._combat_sys = CombatSystem(logger)
        self._dungeon_actions = DungeonActions(data_loader, dungeon_manager, logger)
        self._location_actions = LocationActions(data_loader, location_manager, logger)
        self._nav = Navigation(location_manager, logger)
        self._view_builder = ViewBuilder(data_loader, location_manager, dungeon_manager, logger)

        # Initialise player state
        self._state_mgr.init_player()

    # ------------------------------------------------------------------
    # Public properties for backward compatibility
    # ------------------------------------------------------------------
    @property
    def player_state(self) -> Dict:
        return self._state_mgr.get_player()

    @property
    def dungeon_state(self) -> Optional[Dict]:
        return self._state_mgr.get_dungeon()

    # ------------------------------------------------------------------
    # Action handlers
    # ------------------------------------------------------------------
    def do_location_action(self, action_id: str) -> Tuple[bool, str]:
        """Execute action in city view."""
        player = self._state_mgr.get_player()
        nav_map = {
            "go_tavern": "tavern",
            "go_marketplace": "marketplace",
            "go_alchemy_hall": "alchemy_hall",
            "go_blacksmiths_street": "blacksmiths_street",
            "go_city_hall": "city_hall",
            "go_coliseum": "coliseum",
            "go_public_bath": "public_bath",
            "go_the_river": "the_river",
            "go_dungeon": "dungeon_entrance",
            "go_city": "city_entrance",
        }
        # Navigation
        if action_id in nav_map:
            new_player = self._nav.navigate_to(player, nav_map[action_id])
            self._state_mgr.update_player(new_player)
            return True, ""

        # Service actions
        if action_id == "rest":
            new_player, msg = self._location_actions.rest(player)
            self._state_mgr.update_player(new_player)
            return True, msg
        if action_id == "hear_rumors":
            _, msg = self._location_actions.hear_rumors(player)
            return False, msg
        if action_id == "take_bath":
            new_player, msg = self._location_actions.take_bath(player)
            self._state_mgr.update_player(new_player)
            return True, msg
        if action_id == "go_fishing":
            new_player, msg = self._location_actions.go_fishing(player)
            self._state_mgr.update_player(new_player)
            return True, msg
        if action_id == "pay_taxes":
            new_player, msg = self._location_actions.pay_taxes(player)
            self._state_mgr.update_player(new_player)
            return True, msg
        if action_id == "view_debt":
            msg = self._location_actions.view_debt(player)
            return False, msg
        if action_id == "enter_dungeon":
            new_player, new_dungeon = self._location_actions.enter_dungeon(
                player, lambda: self._dungeon_mgr.generate()
            )
            self._state_mgr.update_player(new_player)
            self._state_mgr.set_dungeon(new_dungeon)
            return True, "You descend into the darkness."

        if self._logger:
            self._logger.warn(f"Unhandled location action: {action_id}")
        return False, f"Action '{action_id}' not yet implemented."

    def do_dungeon_action(self, action_id: str) -> Tuple[bool, str, Optional[Dict]]:
        """Execute action inside dungeon."""
        dungeon = self._state_mgr.get_dungeon()
        if not dungeon:
            return False, "You are not in the dungeon.", None

        player = self._state_mgr.get_player()

        if action_id in ("flee_dungeon", "dungeon_exit"):
            # Exit dungeon
            new_dungeon = self._dungeon_actions.exit_dungeon(dungeon)
            self._state_mgr.set_dungeon(new_dungeon)
            new_player = self._nav.exit_dungeon(player)
            self._state_mgr.update_player(new_player)
            self._state_mgr.set_dungeon(None)
            return True, "You flee back to the city gates.", None

        if action_id == "enter_combat":
            room = self._dungeon_mgr.get_current_room(dungeon)
            if room and room.get("enemy"):
                combat_state = self._combat_sys.start_combat(room["enemy"])
                return False, "", combat_state
            return False, "There is no enemy here.", None

        if action_id == "take_item":
            new_player, new_dungeon, msg = self._dungeon_actions.take_item(player, dungeon)
            self._state_mgr.update_player(new_player)
            self._state_mgr.set_dungeon(new_dungeon)
            return True, msg, None

        if action_id == "next_room":
            new_dungeon, at_exit, msg = self._dungeon_actions.next_room(dungeon)
            self._state_mgr.set_dungeon(new_dungeon)
            if at_exit:
                new_player = self._nav.exit_dungeon(player)
                self._state_mgr.update_player(new_player)
                self._state_mgr.set_dungeon(None)
                return True, msg, None
            return True, "", None

        return False, f"Unknown dungeon action: {action_id}", None

    def do_combat_action(self, action_id: str, enemy: Dict) -> Tuple[bool, str, bool]:
        """Execute combat action (attack or flee). Returns (ended, message, fled)."""
        if action_id == "attack":
            damage = random.randint(4, 8)
            _, ended, msg = self._combat_sys.attack(damage)
            if ended:
                self.end_combat(False)
            return ended, msg, False
        if action_id == "flee":
            ended, msg = self._combat_sys.flee()
            self.end_combat(True)
            return True, msg, True
        return False, "Invalid combat action.", False

    def end_combat(self, player_fled: bool):
        """Clean up after combat ends."""
        if player_fled:
            # Flee: exit dungeon
            player = self._state_mgr.get_player()
            new_player = self._nav.exit_dungeon(player)
            self._state_mgr.update_player(new_player)
            self._state_mgr.set_dungeon(None)
        else:
            # Enemy defeated: mark current room as cleared
            dungeon = self._state_mgr.get_dungeon()
            if dungeon:
                new_dungeon = self._dungeon_mgr.mark_room_cleared(dungeon)
                self._state_mgr.set_dungeon(new_dungeon)
        self._combat_sys.clear_combat()

    def process_year_rollover(self) -> Tuple[Optional[Dict], str]:
        player = self._state_mgr.get_player()
        new_player, msg = self._location_actions.process_year_rollover(player)
        if new_player is None:
            return None, msg
        self._state_mgr.update_player(new_player)
        return self._state_mgr.get_player(), msg

    # ------------------------------------------------------------------
    # View state builders (for UI)
    # ------------------------------------------------------------------
    def get_view_state(self, view_name: str) -> Dict:
        if view_name == "city":
            return self._view_builder.build_city_state(self._state_mgr.get_player())
        if view_name == "dungeon":
            return self._view_builder.build_dungeon_state(self._state_mgr.get_dungeon())
        if view_name == "inventory":
            return self._view_builder.build_inventory_state(self._state_mgr.get_player())
        if view_name == "lore":
            return self._view_builder.build_lore_state()
        if view_name == "combat":
            combat_state = self._combat_sys.get_combat_state()
            if combat_state:
                # Ensure log_text is up to date
                combat_state["log_text"] = self._combat_sys.get_log_text()
                return self._view_builder.build_combat_state(combat_state)
            return {}
        return {}

    def get_player_panel_data(self) -> Dict:
        return self._view_builder.build_player_panel_data(self._state_mgr.get_player())