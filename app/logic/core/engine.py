"""
engine.py — the core orchestrator. Gives orders. Reads results.

Routes action strings through the Router to the correct manager.
The player acts through PlayerMgr. Enemies act through EntityMgr.
CombatMgr coordinates both during combat.
"""
from typing import Dict, Optional, Tuple

from app.logic.core.state      import State
from app.logic.core.year_clock import YearClock
from app.logic.core.router     import (is_nav, nav_target, is_prefixed,
                                        split_prefix, is_city_action)
from app.logic.simple.set_location      import set_location
from app.logic.simple.expire_run_buffs  import expire_run_buffs


class Engine:
    def __init__(self, data_registry, profile_name: str = None, logger=None):
        self._reg    = data_registry
        self._name   = profile_name
        self._logger = logger
        self._state  = State(data_registry.config.defaults())
        self._clock  = YearClock()

        from app.logic.complex.entity_mgr  import EntityMgr
        from app.logic.complex.player_mgr  import PlayerMgr
        from app.logic.complex.combat_mgr  import CombatMgr
        from app.logic.complex.dungeon_mgr import DungeonMgr

        self._entity = EntityMgr(data_registry.items)
        self._player = PlayerMgr(data_registry.items, data_registry.lore,
                                 data_registry.config)
        self._combat  = CombatMgr(self._player, self._entity)
        self._dungeon = DungeonMgr(data_registry.dungeon)

        from app.logic.core.view_builder import ViewBuilder
        self._view = ViewBuilder(data_registry, self._player)

    # ── Public surface ─────────────────────────────────────────────────
    @property
    def player_state(self) -> Dict:            return self._state.player()
    @property
    def dungeon_state(self) -> Optional[Dict]: return self._state.dungeon()

    def set_profile(self, name: str): self._name = name

    # ── City actions ───────────────────────────────────────────────────
    def do_city_action(self, action_id: str) -> Tuple[bool, str]:
        ps = self._state.player()

        if is_nav(action_id):
            self._state.set_player(set_location(ps, nav_target(action_id)))
            return True, ""

        if is_prefixed(action_id):
            prefix, param = split_prefix(action_id)
            return self._dispatch_prefixed(prefix, param, ps)

        if not is_city_action(action_id):
            if self._logger: self._logger.warn(f"Unknown action: {action_id}")
            return False, f"Action '{action_id}' not implemented."

        changed, msg = self._dispatch_city(action_id, ps)

        if changed and self._clock.tick():
            new_ps, rm = self._player.year_rollover(self._state.player())
            if new_ps is None:
                return True, rm  # exile
            self._state.set_player(new_ps)
            msg = (msg + "\n\n" + rm).strip() if msg else rm

        return changed, msg

    def _dispatch_city(self, action_id: str, ps: Dict) -> Tuple[bool, str]:
        table = {
            "rest":          lambda: self._player.rest(ps),
            "hear_rumors":   lambda: self._player.hear_rumors(ps),
            "take_bath":     lambda: self._player.take_bath(ps),
            "go_fishing":    lambda: self._player.fish(ps),
            "pay_taxes":     lambda: self._player.pay_taxes(ps),
            "repair_weapon": lambda: self._player.repair(ps, "equipped_weapon"),
            "repair_armor":  lambda: self._player.repair(ps, "equipped_armor"),
        }
        if action_id == "view_debt":
            return False, self._player.view_debt(ps)
        if action_id == "enter_dungeon":
            self._state.set_dungeon(self._dungeon.generate())
            self._state.set_player(set_location(ps, "dungeon_entrance"))
            return True, "You descend into the darkness."
        fn = table.get(action_id)
        if fn:
            new_ps, msg = fn()
            self._state.set_player(new_ps)
            return True, msg
        return False, f"Action '{action_id}' not handled."

    def _dispatch_prefixed(self, prefix: str, param: str, ps: Dict) -> Tuple[bool, str]:
        table = {
            "use_item":   lambda: self._player.use_item(ps, param),
            "equip_item": lambda: self._player.equip(ps, param),
            "unequip":    lambda: self._player.unequip(ps, param),
            "sell_item":  lambda: self._player.sell_item(ps, param),
            "buy_item":   lambda: self._player.buy_item(ps, param),
        }
        fn = table.get(prefix)
        if fn is None:
            return False, f"Unknown action: {prefix}:{param}"
        new_ps, msg = fn()
        self._state.set_player(new_ps)
        return True, msg

    # ── Dungeon actions ────────────────────────────────────────────────
    def do_dungeon_action(self, action_id: str) -> Tuple[bool, str, Optional[Dict]]:
        dungeon = self._state.dungeon()
        if not dungeon:
            return False, "You are not in the dungeon.", None
        ps = self._state.player()

        if action_id in ("flee_dungeon", "dungeon_exit"):
            ps, _ = self._player.expire_run_buffs(ps)
            self._state.set_player(set_location(ps, "city_entrance"))
            self._state.clear_dungeon()
            return True, "You return to the city.", None

        if action_id == "enter_combat":
            room = self._dungeon.current_room(dungeon)
            if room and room.get("enemy"):
                cs = self._combat.start(ps, room["enemy"])
                return False, "", self._view.build_combat(cs, ps)
            return False, "No enemy here.", None

        if action_id == "take_item":
            new_ps, new_d, msg = self._dungeon.take_item(ps, dungeon)
            self._state.set_player(new_ps)
            self._state.set_dungeon(new_d)
            if self._clock.tick():
                new_ps2, rm = self._player.year_rollover(self._state.player())
                self._state.set_player(new_ps2 or self._state.player())
                msg = (msg + "\n\n" + rm).strip()
            return True, msg, None

        if action_id == "next_room":
            new_d, at_exit, msg = self._dungeon.next_room(dungeon)
            self._state.set_dungeon(new_d)
            if self._clock.tick():
                new_ps, rm = self._player.year_rollover(self._state.player())
                self._state.set_player(new_ps or self._state.player())
                msg = (msg + "\n\n" + rm).strip() if rm else msg
            if at_exit:
                ps, _ = self._player.expire_run_buffs(self._state.player())
                self._state.set_player(set_location(ps, "city_entrance"))
                self._state.clear_dungeon()
            return True, msg, None

        if action_id.startswith("use_item:"):
            _, item_id = split_prefix(action_id)
            new_ps, msg = self._player.use_item(ps, item_id)
            self._state.set_player(new_ps)
            return True, msg, None

        return False, f"Unknown dungeon action: {action_id}", None

    # ── Combat actions ─────────────────────────────────────────────────
    def do_combat_action(self, action_id: str) -> Tuple[bool, str, bool, bool]:
        ps = self._state.player()

        if action_id == "flee":
            msg = self._combat.flee()
            self._combat.clear()
            ps, _ = self._player.expire_run_buffs(ps)
            self._state.set_player(set_location(ps, "city_entrance"))
            self._state.clear_dungeon()
            return True, msg, True, False

        new_ps, snapshot, ended, player_dead = self._combat.player_turn(ps, action_id)
        self._state.set_player(new_ps)
        msg = snapshot.get("log_text", "")

        if ended:
            if player_dead:
                self._on_player_death()
            else:
                d = self._state.dungeon()
                if d:
                    self._state.set_dungeon(self._dungeon.mark_cleared(d))
                self._combat.clear()
                self._clock.tick()

        return ended, msg, False, player_dead

    def _on_player_death(self):
        self._combat.clear()
        self._state.clear_dungeon()
        if self._name and self._reg.profiles.exists(self._name):
            self._reg.profiles.delete(self._name)
            if self._logger:
                self._logger.info(f"Profile '{self._name}' deleted (death).")
        self._name = None
        self._clock.reset()
        self._state.reset_player(self._reg.config.defaults())

    # ── View state ─────────────────────────────────────────────────────
    def get_view_state(self, view_name: str) -> Dict:
        if view_name == "city":
            return self._view.build_city(
                self._state.player(), self._reg.location, self._reg.lore)
        if view_name == "dungeon":
            return self._view.build_dungeon(self._state.dungeon(), self._dungeon)
        if view_name == "inventory":
            return self._view.build_inventory(self._state.player())
        if view_name == "lore":
            return self._view.build_lore(self._reg.lore)
        if view_name == "combat":
            cs = self._combat.snapshot()
            return self._view.build_combat(cs, self._state.player()) if cs else {}
        return {}

    def get_player_panel_data(self) -> Dict:
        return self._view.build_player_panel(self._state.player(), self._player)
