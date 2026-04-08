# app/game_engine.py
"""
Core game logic orchestrator. Delegates to modular components.

v0.7 changes
------------
[ISSUE-001] Enemy counter-attack wired through do_combat_action / CombatSystem.
[ISSUE-002] Player death detected after each attack; triggers game-over path.
[ISSUE-008] Year rollover: each do_location_action / do_dungeon_action increments
            an action counter. When the counter reaches ACTIONS_PER_YEAR,
            process_year_rollover() is called automatically.
"""
import random
from typing import Dict, Any, Optional, Tuple

from app.components.game_engine.state_manager import StateManager
from app.components.game_engine.combat_system import CombatSystem
from app.components.game_engine.dungeon_actions import DungeonActions
from app.components.game_engine.location_actions import LocationActions
from app.components.game_engine.navigation import Navigation
from app.components.game_engine.view_builder import ViewBuilder

# How many player actions constitute one in-game year.
ACTIONS_PER_YEAR = 30


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

        # Action counter for year-rollover mechanic
        self._action_count: int = 0

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
    # Year rollover helper
    # ------------------------------------------------------------------
    def _tick_action(self) -> Optional[Tuple[Optional[Dict], str]]:
        """Increment action counter; trigger year rollover when due.

        Returns None normally, or the (new_player, msg) tuple from
        process_year_rollover if the year just rolled over.
        """
        self._action_count += 1
        if self._action_count >= ACTIONS_PER_YEAR:
            self._action_count = 0
            return self.process_year_rollover()
        return None

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
        # Navigation actions — don't count as actions for year purposes
        if action_id in nav_map:
            new_player = self._nav.navigate_to(player, nav_map[action_id])
            self._state_mgr.update_player(new_player)
            return True, ""

        # Service actions — each counts as one action tick
        result_changed = False
        msg = ""

        if action_id == "rest":
            new_player, msg = self._location_actions.rest(player)
            self._state_mgr.update_player(new_player)
            result_changed = True
        elif action_id == "hear_rumors":
            _, msg = self._location_actions.hear_rumors(player)
        elif action_id == "take_bath":
            new_player, msg = self._location_actions.take_bath(player)
            self._state_mgr.update_player(new_player)
            result_changed = True
        elif action_id == "go_fishing":
            new_player, msg = self._location_actions.go_fishing(player)
            self._state_mgr.update_player(new_player)
            result_changed = True
        elif action_id == "pay_taxes":
            new_player, msg = self._location_actions.pay_taxes(player)
            self._state_mgr.update_player(new_player)
            result_changed = True
        elif action_id == "view_debt":
            msg = self._location_actions.view_debt(player)
        elif action_id == "enter_dungeon":
            new_player, new_dungeon = self._location_actions.enter_dungeon(
                player, lambda: self._dungeon_mgr.generate()
            )
            self._state_mgr.update_player(new_player)
            self._state_mgr.set_dungeon(new_dungeon)
            return True, "You descend into the darkness."
        else:
            if self._logger:
                self._logger.warn(f"Unhandled location action: {action_id}")
            return False, f"Action '{action_id}' not yet implemented."

        # Tick action counter (year rollover check)
        rollover = self._tick_action()
        if rollover is not None:
            _new_player, rollover_msg = rollover
            # Prepend rollover message; it may announce exile
            if rollover_msg:
                msg = (msg + "\n\n" + rollover_msg).strip() if msg else rollover_msg
            result_changed = True

        return result_changed, msg

    def do_dungeon_action(self, action_id: str) -> Tuple[bool, str, Optional[Dict]]:
        """Execute action inside dungeon."""
        dungeon = self._state_mgr.get_dungeon()
        if not dungeon:
            return False, "You are not in the dungeon.", None

        player = self._state_mgr.get_player()

        if action_id in ("flee_dungeon", "dungeon_exit"):
            new_dungeon = self._dungeon_actions.exit_dungeon(dungeon)
            self._state_mgr.set_dungeon(new_dungeon)
            new_player = self._nav.exit_dungeon(player)
            self._state_mgr.update_player(new_player)
            self._state_mgr.set_dungeon(None)
            return True, "You flee back to the city gates.", None

        if action_id == "enter_combat":
            room = self._dungeon_mgr.get_current_room(dungeon)
            if room and room.get("enemy"):
                combat_state = self._combat_sys.start_combat(
                    room["enemy"],
                    player_hp=player.get("hp", 20),
                    player_max_hp=player.get("max_hp", 20),
                )
                return False, "", combat_state
            return False, "There is no enemy here.", None

        if action_id == "take_item":
            new_player, new_dungeon, msg = self._dungeon_actions.take_item(player, dungeon)
            self._state_mgr.update_player(new_player)
            self._state_mgr.set_dungeon(new_dungeon)
            rollover = self._tick_action()
            if rollover is not None:
                _p, rm = rollover
                msg = (msg + "\n\n" + rm).strip() if rm else msg
            return True, msg, None

        if action_id == "next_room":
            new_dungeon, at_exit, msg = self._dungeon_actions.next_room(dungeon)
            self._state_mgr.set_dungeon(new_dungeon)
            rollover = self._tick_action()
            if rollover is not None:
                _p, rm = rollover
                msg = (msg + "\n\n" + rm).strip() if rm else msg
            if at_exit:
                new_player = self._nav.exit_dungeon(player)
                self._state_mgr.update_player(new_player)
                self._state_mgr.set_dungeon(None)
                return True, msg, None
            return True, "", None

        return False, f"Unknown dungeon action: {action_id}", None

    def do_combat_action(self, action_id: str, enemy: Dict) -> Tuple[bool, str, bool, bool]:
        """Execute combat action.

        Returns (ended, message, fled, player_dead).
        """
        if action_id == "attack":
            player_damage = random.randint(4, 8)
            state, ended, msg, hp_lost = self._combat_sys.attack(player_damage)

            # Sync player HP from combat state back into player_state
            new_hp = state.get("player_current_hp", self._state_mgr.get_player().get("hp", 20))
            player = dict(self._state_mgr.get_player())
            player["hp"] = new_hp
            self._state_mgr.update_player(player)

            player_dead = state.get("player_dead", False)

            if ended:
                self.end_combat(False, player_dead=player_dead)
            return ended, msg, False, player_dead

        if action_id == "flee":
            ended, msg = self._combat_sys.flee()
            self.end_combat(True)
            return True, msg, True, False

        return False, "Invalid combat action.", False, False

    def end_combat(self, player_fled: bool, player_dead: bool = False):
        """Clean up after combat ends."""
        if player_fled or player_dead:
            # Flee or death: exit dungeon
            player = self._state_mgr.get_player()
            new_player = self._nav.exit_dungeon(player)
            self._state_mgr.update_player(new_player)
            self._state_mgr.set_dungeon(None)
        else:
            # Enemy defeated: mark current room as cleared, tick action counter
            dungeon = self._state_mgr.get_dungeon()
            if dungeon:
                new_dungeon = self._dungeon_mgr.mark_room_cleared(dungeon)
                self._state_mgr.set_dungeon(new_dungeon)
            self._tick_action()
        self._combat_sys.clear_combat()

    def process_year_rollover(self) -> Tuple[Optional[Dict], str]:
        player = self._state_mgr.get_player()
        new_player, msg = self._location_actions.process_year_rollover(player)
        if new_player is None:
            # Exile: player state is NOT updated so caller can detect it
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
                combat_state["log_text"] = self._combat_sys.get_log_text()
                return self._view_builder.build_combat_state(combat_state)
            return {}
        return {}

    def get_player_panel_data(self) -> Dict:
        return self._view_builder.build_player_panel_data(self._state_mgr.get_player())

    def get_action_progress(self) -> Tuple[int, int]:
        """Return (current_action_count, ACTIONS_PER_YEAR) for UI display."""
        return self._action_count, ACTIONS_PER_YEAR
