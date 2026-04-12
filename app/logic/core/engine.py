"""
engine.py — the core orchestrator. Gives orders. Reads results.

v1.0.0: Integrates ActionDispatcher (AAD) as the primary dispatch layer.
All city/service/inventory/shop actions now route through the dispatcher.
Complex combat and dungeon session management remain in their managers
(CombatMgr, DungeonMgr) because they maintain multi-round state machines
that require two-phase UI coordination.
"""
from typing import Dict, Optional, Tuple

from app.logic.resolver_registry     import ResolverRegistry
from app.logic.dispatcher            import ActionDispatcher
from app.logic.core.state            import State
from app.logic.core.year_clock       import YearClock
from app.logic.core.router           import (is_nav, is_prefixed, split_prefix)
from app.logic.simple.set_location   import set_location
from app.logic.simple.expire_run_buffs import expire_run_buffs


class Engine:
    def __init__(self, data_registry, profile_name: str = None, logger=None):
        self._reg    = data_registry
        self._name   = profile_name
        self._logger = logger
        self._state  = State(data_registry.config.defaults())
        self._clock  = YearClock()

        # ── AAD core ─────────────────────────────────────────────────────
        self._resolver_registry = ResolverRegistry()
        self._dispatcher = ActionDispatcher(
            registry      = self._resolver_registry,
            data_registry = data_registry,
            logger        = logger,
        )

        # ── Managers ─────────────────────────────────────────────────────
        from app.logic.complex.entity_mgr  import EntityMgr
        from app.logic.complex.player_mgr  import PlayerMgr
        from app.logic.complex.combat_mgr  import CombatMgr
        from app.logic.complex.dungeon_mgr import DungeonMgr

        self._entity  = EntityMgr(data_registry.items)
        self._player  = PlayerMgr(data_registry.items, data_registry.lore,
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

    def get_action_progress(self) -> Tuple[int, int]:
        return self._clock.progress()

    # ── AAD dispatch helper ────────────────────────────────────────────
    def _dispatch(self, action_id: str, context_overrides: Optional[Dict] = None):
        """Route through ActionDispatcher; apply result back to State."""
        ps  = self._state.player()
        ds  = self._state.dungeon()
        loc_id = ps.get("current_location_id", "city_entrance")
        location_state = self._reg.config.services().get(loc_id, {})

        result = self._dispatcher.dispatch(
            action_id,
            player_state      = ps,
            dungeon_state     = ds,
            location_state    = location_state,
            context_overrides = context_overrides or {},
        )

        self._state.set_player(result.new_player_state)
        # Only overwrite dungeon state when the resolver actually changed it
        if result.new_dungeon_state is not None:
            self._state.set_dungeon(result.new_dungeon_state)
        elif action_id in ("flee", "flee_dungeon", "dungeon.flee"):
            self._state.clear_dungeon()

        if self._logger:
            for msg in result.messages:
                self._logger.info(msg)

        return result

    # ── Year rollover (Step 8) ─────────────────────────────────────────
    def _tick_year(self) -> Optional[str]:
        """Increment action counter; dispatch advance_year on rollover."""
        if self._clock.tick():
            result = self._dispatch("advance_year")
            msg = "\n".join(result.messages)
            if "GAME OVER" in msg or "Exiled" in msg:
                self._on_exile()
            return msg or None
        return None

    def _on_exile(self):
        if self._name and self._reg.profiles.exists(self._name):
            self._reg.profiles.delete(self._name)
            if self._logger:
                self._logger.info(f"Profile '{self._name}' deleted (exile).")
        self._name = None
        self._clock.reset()
        self._state.reset_player(self._reg.config.defaults())
        self._state.clear_dungeon()

    # ── City actions ───────────────────────────────────────────────────
    def do_city_action(self, action_id: str) -> Tuple[bool, str]:
        # Navigation — dispatcher handles set_location
        if is_nav(action_id):
            result = self._dispatch(action_id)
            return True, "\n".join(result.messages)

        # Prefixed: use_item:x  equip_item:x  unequip:x  buy_item:x  sell_item:x
        if is_prefixed(action_id):
            prefix, param = split_prefix(action_id)
            result = self._dispatch(prefix, {"reference": param})
            msg = "\n".join(result.messages)
            rollover = self._tick_year()
            if rollover:
                msg = (msg + "\n\n" + rollover).strip() if msg else rollover
            return True, msg

        # view_debt — read-only, no year tick
        if action_id == "view_debt":
            result = self._dispatch("view_debt")
            return False, "\n".join(result.messages)

        # enter_dungeon — generate via DungeonMgr, set state directly
        if action_id == "enter_dungeon":
            dungeon = self._dungeon.generate()
            self._state.set_dungeon(dungeon)
            self._state.set_player(
                set_location(self._state.player(), "dungeon_entrance"))
            return True, "You descend into the darkness."

        # All other city service actions → dispatcher
        if self._dispatcher.is_available(action_id):
            result = self._dispatch(action_id)
            msg = "\n".join(result.messages)
            rollover = self._tick_year()
            if rollover:
                msg = (msg + "\n\n" + rollover).strip() if msg else rollover
            return True, msg

        if self._logger:
            self._logger.warn(f"Unknown city action: {action_id}")
        return False, f"Action '{action_id}' not implemented."

    # ── Dungeon actions ────────────────────────────────────────────────
    def do_dungeon_action(self, action_id: str) -> Tuple[bool, str, Optional[Dict]]:
        dungeon = self._state.dungeon()
        if not dungeon:
            return False, "You are not in the dungeon.", None
        ps = self._state.player()

        if action_id in ("flee_dungeon", "dungeon_exit"):
            result = self._dispatch("flee_dungeon")
            return True, "\n".join(result.messages), None

        if action_id == "enter_combat":
            room = self._dungeon.current_room(dungeon)
            if room and room.get("enemy"):
                cs = self._combat.start(ps, room["enemy"])
                return False, "", self._view.build_combat(cs, ps)
            return False, "No enemy here.", None

        if action_id == "take_item":
            room = self._dungeon.current_room(dungeon)
            item_entry = room.get("item") if room else None
            if not item_entry:
                return False, "Nothing to pick up.", None
            item_id = item_entry.get("id") if isinstance(item_entry, dict) else item_entry
            new_ps = self._player.give_item(ps, item_id)
            new_dungeon = self._dungeon.mark_cleared(dungeon)
            self._state.set_player(new_ps)
            self._state.set_dungeon(new_dungeon)
            item = self._reg.items.get(item_id)
            name = item["name"] if item else item_id
            rollover = self._tick_year()
            msg = f"You pick up: {name}."
            if rollover:
                msg = (msg + "\n\n" + rollover).strip()
            return True, msg, None

        if action_id == "next_room":
            new_d, at_exit, msg = self._dungeon.next_room(dungeon)
            self._state.set_dungeon(new_d)
            rollover = self._tick_year()
            if rollover:
                msg = (msg + "\n\n" + rollover).strip() if rollover else msg
            if at_exit:
                cur_ps, _ = expire_run_buffs(self._state.player())
                self._state.set_player(set_location(cur_ps, "city_entrance"))
                self._state.clear_dungeon()
            return True, msg, None

        if action_id.startswith("use_item:"):
            _, item_id = split_prefix(action_id)
            result = self._dispatch("use_item", {"reference": item_id})
            return True, "\n".join(result.messages), None

        return False, f"Unknown dungeon action: {action_id}", None

    # ── Combat actions ─────────────────────────────────────────────────
    def do_combat_action(self, action_id: str) -> Tuple[bool, str, bool, bool]:
        ps = self._state.player()

        if action_id == "flee":
            self._combat.flee()
            self._combat.clear()
            result = self._dispatch("flee")
            return True, "\n".join(result.messages), True, False

        if action_id.startswith("use_item:"):
            _, item_id = split_prefix(action_id)
            result = self._dispatch("use_item", {"reference": item_id})
            new_ps = self._state.player()
            if self._combat.active():
                self._combat._cs["player"] = dict(new_ps)
            return False, "\n".join(result.messages), False, False

        # Attack — CombatMgr owns the session; yields updated player state
        new_ps, snapshot, ended, player_dead = self._combat.player_turn(ps, action_id)
        self._state.set_player(new_ps)
        msg = snapshot.get("log_text", "") if snapshot else ""

        if ended:
            if player_dead:
                self._on_player_death()
            else:
                d = self._state.dungeon()
                if d:
                    self._state.set_dungeon(self._dungeon.mark_cleared(d))
                self._combat.clear()
                self._tick_year()

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
        ps = self._state.player()
        loc_id = ps.get("current_location_id", "city_entrance")
        location_state = self._reg.config.services().get(loc_id, {})

        if view_name == "city":
            state = self._view.build_city(ps, self._reg.location, self._reg.lore)
            # Step 6: inject shop inventory when present
            shop_inv = location_state.get("shop_inventory", [])
            if shop_inv:
                shop_items = []
                for item_id in shop_inv:
                    item = self._reg.items.get(item_id)
                    if item:
                        shop_items.append({
                            "id":    item_id,
                            "label": f"{item['name']}  ({item.get('value', 0)}g)",
                        })
                state["shop"] = {"items": shop_items}
            return state
        if view_name == "dungeon":
            return self._view.build_dungeon(self._state.dungeon(), self._dungeon)
        if view_name == "inventory":
            return self._view.build_inventory(ps)
        if view_name == "lore":
            return self._view.build_lore(self._reg.lore)
        if view_name == "combat":
            cs = self._combat.snapshot()
            return self._view.build_combat(cs, ps) if cs else {}
        return {}

    def get_player_panel_data(self) -> Dict:
        return self._view.build_player_panel(self._state.player(), self._player)
