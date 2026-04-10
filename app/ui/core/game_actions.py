"""
game_actions.py — UI core controller for game events.

Receives raw action strings from widgets. Tells Engine what happened.
Reads result. Tells Coordinator and Window to update.
No game logic. No validation. Just routing.
"""
from tkinter import messagebox


class GameActions:
    VIEWS = ("city", "dungeon", "combat", "inventory", "lore")

    def __init__(self, engine, assembler, coordinator, data_registry, window, logger=None):
        self._engine      = engine
        self._assembler   = assembler
        self._coordinator = coordinator
        self._reg         = data_registry
        self._window      = window
        self._logger      = logger

    def on_city_action(self, action_id: str):
        changed, msg = self._engine.do_city_action(action_id)
        if msg and ("GAME OVER" in msg or "Exiled" in msg):
            self._handle_game_over(msg); return
        if msg: messagebox.showinfo("", msg)
        if changed: self.refresh()
        if action_id == "enter_dungeon" and self._engine.dungeon_state:
            self._show("dungeon"); self.refresh()

    def on_dungeon_action(self, action_id: str):
        changed, msg, combat = self._engine.do_dungeon_action(action_id)
        if msg and ("GAME OVER" in msg or "Exiled" in msg):
            self._handle_game_over(msg); return
        if msg: messagebox.showinfo("", msg)
        if action_id == "enter_combat" and combat:
            self._assembler.get_or_build_view("combat", combat)
            self._assembler.refresh_view("combat", combat)
            self._show("combat"); return
        if changed:
            self._show("city" if not self._engine.dungeon_state else "dungeon")
            self.refresh()

    def on_combat_action(self, action_id: str):
        if action_id.startswith("use_item:"):
            ended, msg, fled, dead = self._engine.do_combat_action(action_id)
            if msg: messagebox.showinfo("", msg)
            self._assembler.refresh_view("combat", self._engine.get_view_state("combat"))
            self._update_panel(); return

        ended, msg, fled, dead = self._engine.do_combat_action(action_id)
        if dead:
            self._handle_game_over(
                "You have been slain.\n\nYour profile has been deleted.\n\nGAME OVER"); return
        if msg: messagebox.showinfo("", msg)
        if ended:
            self._show("city" if not self._engine.dungeon_state else "dungeon")
            self.refresh()
        else:
            self._assembler.refresh_view("combat", self._engine.get_view_state("combat"))
        self._update_panel()

    def on_inventory_select(self, item_id: str):
        item = self._reg.items.get(item_id)
        if not item:
            detail, actions = f"Unknown: {item_id}", []
        else:
            prices = self._reg.config.prices()
            mult   = prices.get("sell_price_multiplier", 0.4)
            sell   = max(1, int(item.get("value", 0) * mult))
            itype  = item.get("type", "misc")
            detail = (f"{item['name']}\nType: {itype.capitalize()}\n"
                      f"Value: {item.get('value',0)}g  (sells for {sell}g)")
            if item.get("effect"):
                detail += f"\nEffect: {item['effect']}"
            sb = item.get("stat_bonus", {})
            if sb: detail += "\nStats: " + ", ".join(f"+{v} {k}" for k, v in sb.items())
            if item.get("durability"):
                detail += f"\nBase durability: {item['durability']}"
            actions = []
            if itype == "consumable":
                actions.append({"id": f"use_item:{item_id}", "label": f"Use {item['name']}"})
            elif itype in ("weapon", "armor"):
                actions.append({"id": f"equip_item:{item_id}", "label": f"Equip {item['name']}"})
            actions.append({"id": f"sell_item:{item_id}", "label": f"Sell ({sell}g)"})

        state = self._engine.get_view_state("inventory")
        state["inventory"]["detail"] = detail
        state["inventory"]["item_actions"] = actions
        self._assembler.refresh_view("inventory", state)

    def on_inventory_action(self, action_id: str):
        changed, msg = self._engine.do_city_action(action_id)
        if msg: messagebox.showinfo("", msg)
        if changed:
            self._assembler.refresh_view("inventory", self._engine.get_view_state("inventory"))
            self._update_panel()

    def refresh(self):
        self._coordinator.refresh_active_view()
        self._update_panel()

    def _show(self, view: str):
        self._coordinator.show_view(view)
        self._window.highlight_nav_button(view, True)

    def _update_panel(self):
        self._window.set_player_panel_data(self._engine.get_player_panel_data(), self._logger)

    def _handle_game_over(self, msg: str):
        messagebox.showwarning("Game Over", msg)
        self._engine._state.reset_player(self._engine._reg.config.defaults())
        self._engine._combat.clear()
        self._engine._state.clear_dungeon()
        self._engine._clock.reset()
        self._show("city"); self.refresh()
