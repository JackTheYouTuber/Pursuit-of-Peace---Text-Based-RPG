import tkinter as tk
from tkinter import messagebox, simpledialog
from app.init.profile_selector import ProfileSelector


class ProfileActions:
    """Handles profile management (new, save, load, quit)."""

    def __init__(self, root, profile_mgr, loader, engine, window, coordinator, logger=None):
        self._root = root
        self._profile_mgr = profile_mgr
        self._loader = loader
        self._engine = engine
        self._window = window
        self._coordinator = coordinator
        self._logger = logger
        self._current_profile = None  # set by App after selection

    def set_current_profile(self, name: str):
        self._current_profile = name

    def save_game(self):
        if not self._current_profile:
            messagebox.showerror("Error", "No active profile to save.")
            return
        if self._profile_mgr.save_profile(self._current_profile, self._engine.player_state):
            messagebox.showinfo("Saved", f"Saved to '{self._current_profile}'.")
            if self._logger:
                self._logger.info(f"Manual save: {self._current_profile}")
        else:
            messagebox.showerror("Error", "Failed to save game.")

    def load_game(self):
        name, state = ProfileSelector.select_or_create(
            self._root, self._profile_mgr, self._loader, self._logger
        )
        if name and state:
            self._current_profile = name
            self._engine._state_mgr.update_player(state)
            self._engine._state_mgr.clear_dungeon()
            self._engine._combat_sys.clear_combat()
            self._engine.set_current_profile(name)
            # Refresh UI
            self._coordinator.refresh_active_view()
            self._coordinator.show_view("city")
            # Update player panel
            data = self._engine.get_player_panel_data()
            self._window.set_player_panel_data(data, self._logger)
            messagebox.showinfo("Loaded", f"Loaded profile '{name}'.")

    def new_game(self):
        name = simpledialog.askstring("New Game", "Enter profile name:",
                                      parent=self._root)
        if not name or not name.strip():
            return
        name = name.strip()
        if self._profile_mgr.profile_exists(name):
            if not messagebox.askyesno("Overwrite", f"Profile '{name}' exists. Overwrite?"):
                return
        defaults = self._loader.get_player_defaults()
        state = self._profile_mgr.create_new_profile(name, defaults)
        if not state and self._profile_mgr.profile_exists(name):
            state = defaults
            if not self._profile_mgr.save_profile(name, state):
                messagebox.showerror("Error", "Failed to overwrite profile.")
                return
        if state:
            self._current_profile = name
            self._engine._state_mgr.update_player(state)
            self._engine._state_mgr.clear_dungeon()
            self._engine._combat_sys.clear_combat()
            self._engine.set_current_profile(name)
            self._coordinator.refresh_active_view()
            self._coordinator.show_view("city")
            data = self._engine.get_player_panel_data()
            self._window.set_player_panel_data(data, self._logger)
            messagebox.showinfo("New Game", f"Started new game as '{name}'.")
        else:
            messagebox.showerror("Error", "Could not create new profile.")

    def quit_app(self):
        if messagebox.askokcancel("Quit", "Exit the game?"):
            if self._logger:
                self._logger.shutdown()
            self._root.destroy()