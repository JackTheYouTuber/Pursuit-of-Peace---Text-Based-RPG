from tkinter import messagebox


class GameActions:
    """Handles all game-related UI actions (city, dungeon, combat, inventory).

    v0.8 — Tier 1 fix: death now deletes profile (handled by engine).
           Tier 2: inventory_action dispatches use/equip/unequip/sell.
           Tier 3: combat UI shows equipment stats; Use-in-combat supported.
           Tier 4: buy_item / sell_item routed through location actions.
    """

    def __init__(self, engine, assembler, coordinator, loader, window, logger=None):
        self._engine = engine
        self._assembler = assembler
        self._coordinator = coordinator
        self._loader = loader
        self._window = window
        self._logger = logger

        self.VIEW_CITY      = "city"
        self.VIEW_DUNGEON   = "dungeon"
        self.VIEW_COMBAT    = "combat"
        self.VIEW_INVENTORY = "inventory"
        self.VIEW_LORE      = "lore"

    # ------------------------------------------------------------------
    # City / location
    # ------------------------------------------------------------------
    def on_location_action(self, action_id: str):
        changed, msg = self._engine.do_location_action(action_id)
        if msg:
            if "GAME OVER" in msg or "Exiled" in msg:
                self._show_game_over(msg)
                return
            self._show_message(msg)
        if changed:
            self.refresh_current_view()
        if action_id == "enter_dungeon" and self._engine.dungeon_state:
            self._show_view(self.VIEW_DUNGEON)
            self.refresh_current_view()

    # ------------------------------------------------------------------
    # Dungeon
    # ------------------------------------------------------------------
    def on_dungeon_action(self, action_id: str):
        changed, msg, combat_state = self._engine.do_dungeon_action(action_id)
        if msg:
            if "GAME OVER" in msg or "Exiled" in msg:
                self._show_game_over(msg)
                return
            self._show_message(msg)
        if action_id == "enter_combat" and combat_state:
            self._assembler.get_or_build_view(self.VIEW_COMBAT, combat_state)
            self._assembler.refresh_view(self.VIEW_COMBAT, combat_state)
            self._show_view(self.VIEW_COMBAT)
            return
        if changed:
            if self._engine.dungeon_state is None:
                self._show_view(self.VIEW_CITY)
            self.refresh_current_view()

    # ------------------------------------------------------------------
    # Combat
    # ------------------------------------------------------------------
    def on_combat_action(self, action_id: str):
        # Allow using items from combat panel without needing an enemy room check
        if action_id.startswith("use_item:"):
            ended, msg, fled, player_dead = self._engine.do_combat_action(action_id, {})
            if msg:
                self._show_message(msg)
            combat_state = self._engine.get_view_state(self.VIEW_COMBAT)
            self._assembler.refresh_view(self.VIEW_COMBAT, combat_state)
            self._update_player_panel()
            return

        if not self._engine.dungeon_state:
            self._show_view(self.VIEW_DUNGEON)
            return
        room = self._engine._dungeon_mgr.get_current_room(self._engine.dungeon_state)
        if not room or not room.get("enemy"):
            self._show_view(self.VIEW_DUNGEON)
            return
        enemy = room["enemy"]
        ended, msg, fled, player_dead = self._engine.do_combat_action(action_id, enemy)

        if player_dead:
            # Profile has already been deleted by the engine
            self._show_game_over(
                "You have been slain in combat.\n\n"
                "Your body is dragged from the dungeon.\n"
                "Your profile has been deleted.\n\n"
                "GAME OVER"
            )
            return

        if msg:
            self._show_message(msg)

        if ended:
            if self._engine.dungeon_state is None:
                self._show_view(self.VIEW_CITY)
            else:
                self._show_view(self.VIEW_DUNGEON)
            self._refresh_current_view()
        else:
            combat_state = self._engine.get_view_state(self.VIEW_COMBAT)
            self._assembler.refresh_view(self.VIEW_COMBAT, combat_state)
        self._update_player_panel()

    # ------------------------------------------------------------------
    # Inventory — select (show details + actions)
    # ------------------------------------------------------------------
    def on_inventory_select(self, item_id: str):
        try:
            item = self._loader.get_item(item_id)
            item_type = item.get("type", "misc")
            name = item.get("name", item_id)

            prices = self._loader.get_prices()
            multiplier = prices.get("sell_price_multiplier", 0.4)
            sell_price = max(1, int(item.get("value", 0) * multiplier))

            detail = (
                f"{name}\n"
                f"Type: {item_type.capitalize()}\n"
                f"Value: {item.get('value', 0)}g  (sells for {sell_price}g)"
            )
            if item.get("effect"):
                detail += f"\nEffect: {item['effect']}"
            stat_bonus = item.get("stat_bonus", {})
            if stat_bonus:
                bonus_parts = [f"+{v} {k}" for k, v in stat_bonus.items()]
                detail += f"\nStats: {', '.join(bonus_parts)}"
            if item.get("durability"):
                detail += f"\nBase durability: {item['durability']}"

            actions = []
            if item_type == "consumable":
                actions.append({"id": f"use_item:{item_id}", "label": f"Use {name}"})
            elif item_type in ("weapon", "armor"):
                actions.append({"id": f"equip_item:{item_id}", "label": f"Equip {name}"})
            actions.append({"id": f"sell_item:{item_id}", "label": f"Sell ({sell_price}g)"})

        except ValueError:
            detail = f"Unknown item: {item_id}"
            actions = []

        state = self._engine.get_view_state(self.VIEW_INVENTORY)
        state["inventory"]["detail"] = detail
        state["inventory"]["item_actions"] = actions
        self._assembler.refresh_view(self.VIEW_INVENTORY, state)

    # ------------------------------------------------------------------
    # Inventory — action (use/equip/unequip/sell)
    # ------------------------------------------------------------------
    def on_inventory_action(self, action_id: str):
        """Handle Use / Equip / Unequip / Sell buttons in inventory."""
        # Route to location action dispatcher which handles all prefixed actions
        changed, msg = self._engine.do_location_action(action_id)
        if msg:
            self._show_message(msg)
        if changed:
            # Refresh inventory view
            state = self._engine.get_view_state(self.VIEW_INVENTORY)
            self._assembler.refresh_view(self.VIEW_INVENTORY, state)
            self._update_player_panel()

    def refresh_current_view(self):
        self._coordinator.refresh_active_view()
        self._update_player_panel()

    _refresh_current_view = refresh_current_view

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _show_message(self, msg: str):
        if msg:
            messagebox.showinfo("", msg)

    def _show_game_over(self, msg: str):
        """Show a game-over dialog. Profile already deleted; reset to fresh state."""
        messagebox.showwarning("Game Over", msg)
        # Engine already wiped state in _delete_profile_on_death
        # Sync the profile_actions controller's profile name too
        self._engine._state_mgr.init_player()
        self._engine._combat_sys.clear_combat()
        self._engine._state_mgr.set_dungeon(None)
        self._engine._action_count = 0
        self._show_view(self.VIEW_CITY)
        self.refresh_current_view()

    def _show_view(self, view_name: str):
        self._coordinator.show_view(view_name)
        self._window.highlight_nav_button(view_name, True)

    def _update_player_panel(self):
        data = self._engine.get_player_panel_data()
        self._window.set_player_panel_data(data, self._logger)
