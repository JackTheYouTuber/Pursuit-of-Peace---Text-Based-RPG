# app/game_engine.py
"""
Core game logic orchestrator.

Tier 1: enemy counter-attack, player death (profile deletion), year rollover.
Tier 2: consumable use in and out of combat, buff tick.
Tier 3: equipment slots wired into combat, durability, repair.
Tier 4: buy/sell items.
"""
import random
from typing import Dict, Any, Optional, Tuple

from app.components.game_engine.state_manager import StateManager
from app.components.game_engine.combat_system import CombatSystem
from app.components.game_engine.dungeon_actions import DungeonActions
from app.components.game_engine.location_actions import LocationActions
from app.components.game_engine.navigation import Navigation
from app.components.game_engine.view_builder import ViewBuilder
from app.components.game_engine.buff_system import BuffSystem

ACTIONS_PER_YEAR = 30


class GameEngine:
    def __init__(self, data_loader, location_manager, dungeon_manager,
                 profile_manager=None, current_profile_name=None, logger=None):
        self._loader = data_loader
        self._location_mgr = location_manager
        self._dungeon_mgr = dungeon_manager
        self._profile_mgr = profile_manager
        self._current_profile = current_profile_name
        self._logger = logger

        self._state_mgr = StateManager(data_loader, logger)
        self._combat_sys = CombatSystem(logger)
        self._dungeon_actions = DungeonActions(data_loader, dungeon_manager, logger)
        self._location_actions = LocationActions(data_loader, location_manager, logger)
        self._nav = Navigation(location_manager, logger)
        self._view_builder = ViewBuilder(data_loader, location_manager, dungeon_manager, logger)
        self._buff_sys = BuffSystem(logger)

        self._action_count: int = 0
        self._state_mgr.init_player()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def player_state(self) -> Dict:
        return self._state_mgr.get_player()

    @property
    def dungeon_state(self) -> Optional[Dict]:
        return self._state_mgr.get_dungeon()

    def set_current_profile(self, name: str):
        self._current_profile = name

    # ------------------------------------------------------------------
    # Year rollover
    # ------------------------------------------------------------------
    def _tick_action(self) -> Optional[Tuple[Optional[Dict], str]]:
        self._action_count += 1
        if self._action_count >= ACTIONS_PER_YEAR:
            self._action_count = 0
            return self.process_year_rollover()
        return None

    # ------------------------------------------------------------------
    # Location actions (city view)
    # ------------------------------------------------------------------
    def do_location_action(self, action_id: str) -> Tuple[bool, str]:
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
        if action_id in nav_map:
            new_player = self._nav.navigate_to(player, nav_map[action_id])
            self._state_mgr.update_player(new_player)
            return True, ""

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

        # ── Tier 2: use consumable ───────────────────────────────────
        elif action_id.startswith("use_item:"):
            item_id = action_id.split(":", 1)[1]
            new_player, msg = self._location_actions.use_item(player, item_id)
            self._state_mgr.update_player(new_player)
            result_changed = True

        # ── Tier 3: equip / unequip / repair ────────────────────────
        elif action_id.startswith("equip_item:"):
            item_id = action_id.split(":", 1)[1]
            new_player, msg = self._location_actions.equip_item(player, item_id)
            self._state_mgr.update_player(new_player)
            result_changed = True

        elif action_id.startswith("unequip:"):
            slot = action_id.split(":", 1)[1]
            new_player, msg = self._location_actions.unequip_item(player, slot)
            self._state_mgr.update_player(new_player)
            result_changed = True

        elif action_id == "repair_weapon":
            new_player, msg = self._location_actions.repair_equipment(
                player, "equipped_weapon"
            )
            self._state_mgr.update_player(new_player)
            result_changed = True

        elif action_id == "repair_armor":
            new_player, msg = self._location_actions.repair_equipment(
                player, "equipped_armor"
            )
            self._state_mgr.update_player(new_player)
            result_changed = True

        # ── Tier 4: buy / sell ───────────────────────────────────────
        elif action_id.startswith("buy_item:"):
            item_id = action_id.split(":", 1)[1]
            new_player, msg = self._location_actions.buy_item(player, item_id)
            self._state_mgr.update_player(new_player)
            result_changed = True

        elif action_id.startswith("sell_item:"):
            item_id = action_id.split(":", 1)[1]
            new_player, msg = self._location_actions.sell_item(player, item_id)
            self._state_mgr.update_player(new_player)
            result_changed = True

        else:
            if self._logger:
                self._logger.warn(f"Unhandled location action: {action_id}")
            return False, f"Action '{action_id}' not yet implemented."

        rollover = self._tick_action()
        if rollover is not None:
            _new_player, rollover_msg = rollover
            if rollover_msg:
                msg = (msg + "\n\n" + rollover_msg).strip() if msg else rollover_msg
            result_changed = True

        return result_changed, msg

    # ------------------------------------------------------------------
    # Dungeon actions
    # ------------------------------------------------------------------
    def do_dungeon_action(self, action_id: str) -> Tuple[bool, str, Optional[Dict]]:
        dungeon = self._state_mgr.get_dungeon()
        if not dungeon:
            return False, "You are not in the dungeon.", None
        player = self._state_mgr.get_player()

        if action_id in ("flee_dungeon", "dungeon_exit"):
            # Expire one_run buffs when leaving dungeon
            new_player, expired = self._buff_sys.expire_run_buffs(player)
            if expired:
                pass  # Could notify but keep it quiet
            self._state_mgr.update_player(new_player)

            new_dungeon = self._dungeon_actions.exit_dungeon(dungeon)
            self._state_mgr.set_dungeon(new_dungeon)
            new_player2 = self._nav.exit_dungeon(self._state_mgr.get_player())
            self._state_mgr.update_player(new_player2)
            self._state_mgr.set_dungeon(None)
            return True, "You flee back to the city gates.", None

        if action_id == "enter_combat":
            room = self._dungeon_mgr.get_current_room(dungeon)
            if room and room.get("enemy"):
                combat_state = self._combat_sys.start_combat(
                    room["enemy"],
                    player_hp=player.get("hp", 20),
                    player_max_hp=player.get("max_hp", 20),
                    equipped_weapon=player.get("equipped_weapon"),
                    equipped_armor=player.get("equipped_armor"),
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
                # Expire one_run buffs on dungeon exit
                new_player, _ = self._buff_sys.expire_run_buffs(player)
                self._state_mgr.update_player(new_player)
                new_player2 = self._nav.exit_dungeon(self._state_mgr.get_player())
                self._state_mgr.update_player(new_player2)
                self._state_mgr.set_dungeon(None)
                return True, msg, None
            return True, "", None

        # Use item mid-dungeon (from inventory)
        if action_id.startswith("use_item:"):
            item_id = action_id.split(":", 1)[1]
            new_player, msg = self._location_actions.use_item(player, item_id)
            self._state_mgr.update_player(new_player)
            return True, msg, None

        return False, f"Unknown dungeon action: {action_id}", None

    # ------------------------------------------------------------------
    # Combat actions
    # ------------------------------------------------------------------
    def do_combat_action(self, action_id: str, enemy: Dict) -> Tuple[bool, str, bool, bool]:
        """Returns (ended, message, fled, player_dead)."""
        player = self._state_mgr.get_player()

        if action_id == "attack":
            base_damage = random.randint(4, 8)
            # Apply damage buff bonus
            buff_bonus = self._buff_sys.get_damage_bonus(player)
            base_damage += buff_bonus

            state, ended, msg, hp_lost = self._combat_sys.attack(base_damage)

            # Sync player HP
            new_hp = state.get("player_current_hp", player.get("hp", 20))
            player_copy = dict(player)
            player_copy["hp"] = new_hp

            # Sync equipment durability changes back to player state
            # (combat_state holds mutable dicts shared with player state already,
            #  but we need to persist equipment state properly)
            if state.get("equipped_weapon") is not None:
                player_copy["equipped_weapon"] = state["equipped_weapon"]
            else:
                player_copy["equipped_weapon"] = None  # broken

            if state.get("equipped_armor") is not None:
                player_copy["equipped_armor"] = state["equipped_armor"]
            else:
                player_copy["equipped_armor"] = None  # broken

            # Tick turn-based buffs after attack
            player_copy, expired = self._buff_sys.tick_turn_buffs(player_copy)
            self._state_mgr.update_player(player_copy)

            player_dead = state.get("player_dead", False)

            if expired:
                expired_msg = "Buff expired: " + ", ".join(expired)
                msg = msg + "\n" + expired_msg if msg else expired_msg

            if ended:
                if not player_dead:
                    # Victory: award gold + loot
                    gold_msg, loot_msg = self._award_combat_rewards(enemy)
                    if gold_msg:
                        msg = msg + "\n" + gold_msg
                    if loot_msg:
                        msg = msg + "\n" + loot_msg
                self.end_combat(False, player_dead=player_dead)
            return ended, msg, False, player_dead

        if action_id == "flee":
            ended, msg = self._combat_sys.flee()
            self.end_combat(True)
            return True, msg, True, False

        # Use item in combat
        if action_id.startswith("use_item:"):
            item_id = action_id.split(":", 1)[1]
            new_player, msg = self._location_actions.use_item(player, item_id)
            self._state_mgr.update_player(new_player)
            # Update combat state HP so bar shows new HP
            combat_st = self._combat_sys.get_combat_state()
            if combat_st:
                combat_st["player_current_hp"] = new_player.get("hp", 20)
                combat_st["player_max_hp"] = new_player.get("max_hp", 20)
            return False, msg, False, False

        return False, "Invalid combat action.", False, False

    def _award_combat_rewards(self, enemy: Dict) -> Tuple[str, str]:
        """Award gold and loot after defeating an enemy. Returns (gold_msg, loot_msg)."""
        player = self._state_mgr.get_player()
        player_copy = dict(player)

        # Increment kill counter
        player_copy["kills"] = player_copy.get("kills", 0) + 1

        # Gold reward (based on enemy max HP as a proxy for power)
        enemy_max_hp = enemy.get("hp", 10)
        gold_earned = random.randint(
            max(1, enemy_max_hp // 4),
            max(2, enemy_max_hp // 2)
        )
        player_copy["gold"] = player_copy.get("gold", 0) + gold_earned
        gold_msg = f"You loot {gold_earned}g from the body."

        # Loot drop
        loot_table = enemy.get("loot_table", [])
        loot_msg = ""
        if loot_table and random.random() < 0.6:
            item_id = random.choice(loot_table)
            try:
                item = self._loader.get_item(item_id)
                inventory = list(player_copy.get("inventory", []))
                inventory.append(item_id)
                player_copy["inventory"] = inventory
                loot_msg = f"Dropped: {item.get('name', item_id)}."
            except ValueError:
                pass

        self._state_mgr.update_player(player_copy)
        return gold_msg, loot_msg

    def end_combat(self, player_fled: bool, player_dead: bool = False):
        """Clean up after combat. If player_dead, delete their profile."""
        if player_fled or player_dead:
            player = self._state_mgr.get_player()
            new_player = self._nav.exit_dungeon(player)
            self._state_mgr.update_player(new_player)
            self._state_mgr.set_dungeon(None)

            if player_dead:
                # ── Tier 1 fix: delete the profile on death ─────────
                self._delete_profile_on_death()
        else:
            dungeon = self._state_mgr.get_dungeon()
            if dungeon:
                new_dungeon = self._dungeon_mgr.mark_room_cleared(dungeon)
                self._state_mgr.set_dungeon(new_dungeon)
            self._tick_action()
        self._combat_sys.clear_combat()

    def _delete_profile_on_death(self):
        """Delete the current profile file — death is permanent."""
        if self._profile_mgr and self._current_profile:
            self._profile_mgr.delete_profile(self._current_profile)
            if self._logger:
                self._logger.info(
                    f"Profile '{self._current_profile}' deleted (player death)."
                )
        # Reset in-memory state to defaults
        self._state_mgr.init_player()
        self._action_count = 0
        self._current_profile = None

    def process_year_rollover(self) -> Tuple[Optional[Dict], str]:
        player = self._state_mgr.get_player()
        new_player, msg = self._location_actions.process_year_rollover(player)
        if new_player is None:
            return None, msg
        self._state_mgr.update_player(new_player)
        return self._state_mgr.get_player(), msg

    # ------------------------------------------------------------------
    # View state builders
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
                return self._view_builder.build_combat_state(
                    combat_state, self._state_mgr.get_player()
                )
            return {}
        return {}

    def get_player_panel_data(self) -> Dict:
        return self._view_builder.build_player_panel_data(self._state_mgr.get_player())

    def get_action_progress(self) -> Tuple[int, int]:
        return self._action_count, ACTIONS_PER_YEAR
