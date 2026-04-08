from tkinter import messagebox


class GameActions:
    """Handles all game-related UI actions (city, dungeon, combat, inventory)."""

    def __init__(self, engine, assembler, coordinator, loader, window, logger=None):
        self._engine = engine
        self._assembler = assembler
        self._coordinator = coordinator
        self._loader = loader
        self._window = window
        self._logger = logger

        # View constants (should match App's)
        self.VIEW_CITY = "city"
        self.VIEW_DUNGEON = "dungeon"
        self.VIEW_COMBAT = "combat"
        self.VIEW_INVENTORY = "inventory"
        self.VIEW_LORE = "lore"

    # ------------------------------------------------------------------
    # Public callbacks for UI
    # ------------------------------------------------------------------
    def on_location_action(self, action_id: str):
        changed, msg = self._engine.do_location_action(action_id)
        if msg:
            self._show_message(msg)
        if changed:
            self.refresh_current_view()
        if action_id == "enter_dungeon" and self._engine.dungeon_state:
            self._show_view(self.VIEW_DUNGEON)
            self.refresh_current_view()

    def on_dungeon_action(self, action_id: str):
        changed, msg, combat_state = self._engine.do_dungeon_action(action_id)
        if msg:
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

    def on_combat_action(self, action_id: str):
        if not self._engine.dungeon_state:
            self._show_view(self.VIEW_DUNGEON)
            return
        room = self._engine._dungeon_mgr.get_current_room(self._engine.dungeon_state)
        if not room or not room.get("enemy"):
            self._show_view(self.VIEW_DUNGEON)
            return
        enemy = room["enemy"]
        ended, msg, fled = self._engine.do_combat_action(action_id, enemy)
        if msg:
            self._show_message(msg)
        if ended:
            # NOTE: end_combat is already called inside do_combat_action; do NOT call it again.
            if self._engine.dungeon_state is None:
                self._show_view(self.VIEW_CITY)
            else:
                self._show_view(self.VIEW_DUNGEON)
            self._refresh_current_view()
        else:
            # Refresh the combat panel with the latest state from the engine.
            combat_state = self._engine.get_view_state(self.VIEW_COMBAT)
            self._assembler.refresh_view(self.VIEW_COMBAT, combat_state)

    def on_inventory_select(self, item_id: str):
        try:
            item = self._loader.get_item(item_id)
            detail = (
                f"{item.get('name', item_id)}\n"
                f"Type: {item.get('type', 'unknown')}\n"
                f"Value: {item.get('value', 0)}"
            )
            if item.get("effect"):
                detail += f"\nEffect: {item['effect']}"
        except ValueError:
            detail = f"Unknown item: {item_id}"
        state = self._engine.get_view_state(self.VIEW_INVENTORY)
        state["inventory"]["detail"] = detail
        self._assembler.refresh_view(self.VIEW_INVENTORY, state)

    def refresh_current_view(self):
        self._coordinator.refresh_active_view()
        self._update_player_panel()

    # Alias so internal callers using the private form still work
    _refresh_current_view = refresh_current_view

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _show_message(self, msg: str):
        if msg:
            messagebox.showinfo("", msg)

    def _show_view(self, view_name: str):
        self._coordinator.show_view(view_name)
        # Also update nav button highlight via window method
        self._window.highlight_nav_button(view_name, True)

    def _update_player_panel(self):
        data = self._engine.get_player_panel_data()
        self._window.set_player_panel_data(data, self._logger)