"""
profile_actions.py — UI core controller for profile menu events.

Save, load, new game, quit. No game logic. Just file + UI coordination.
"""
import tkinter as tk
from tkinter import messagebox, simpledialog
from app.data.init.profile_selector import ProfileSelector


class ProfileActions:
    def __init__(self, root, data_registry, engine, window, coordinator, logger=None):
        self._root        = root
        self._reg         = data_registry
        self._engine      = engine
        self._window      = window
        self._coordinator = coordinator
        self._logger      = logger
        self._profile     = None

    def set_profile(self, name: str): self._profile = name

    def save(self):
        if not self._profile:
            messagebox.showerror("Error", "No active profile."); return
        ok = self._reg.profiles.save(self._profile, self._engine.player_state)
        messagebox.showinfo("Saved", f"Saved to '{self._profile}'.") if ok else \
            messagebox.showerror("Error", "Save failed.")

    def load(self):
        name, state = ProfileSelector.select_or_create(
            self._root, self._reg.profiles, self._reg.config, self._logger)
        if name and state:
            self._profile = name
            self._engine._state.set_player(state)
            self._engine._state.clear_dungeon()
            self._engine._combat.clear()
            self._engine.set_profile(name)
            self._coordinator.show_view("city")
            self._coordinator.refresh_active_view()
            self._window.set_player_panel_data(
                self._engine.get_player_panel_data(), self._logger)
            messagebox.showinfo("Loaded", f"Loaded '{name}'.")

    def new_game(self):
        name = simpledialog.askstring("New Game", "Enter profile name:", parent=self._root)
        if not name or not name.strip(): return
        name = name.strip()
        state = self._reg.profiles.create(name, self._reg.config.defaults())
        if state:
            self._profile = name
            self._engine._state.set_player(state)
            self._engine._state.clear_dungeon()
            self._engine._combat.clear()
            self._engine.set_profile(name)
            self._coordinator.show_view("city")
            self._coordinator.refresh_active_view()
            self._window.set_player_panel_data(
                self._engine.get_player_panel_data(), self._logger)
            messagebox.showinfo("New Game", f"Started as '{name}'.")
        else:
            messagebox.showerror("Error", "Could not create profile.")

    def quit(self):
        if messagebox.askokcancel("Quit", "Exit the game?"):
            if self._logger: self._logger.shutdown()
            self._root.destroy()
