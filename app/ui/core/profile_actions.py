"""
profile_actions.py — UI core controller for profile menu events.

Save, load, new game, quit. No game logic. Just file + UI coordination.

Message policy (Step 5.2):
  • Success messages  → window.post_message()        (inline, no popup)
  • Error messages    → messagebox.showerror         (kept as modal popup)
  • Confirmations     → window.show_confirm()        (inline Yes/No bar)
  • New-profile name  → window.show_profile_name_entry()  (inline frame)
"""
import tkinter as tk
from tkinter import messagebox
from app.data.init.profile_selector import ProfileSelectorFrame


class ProfileActions:
    def __init__(self, root, data_registry, engine, window, coordinator, logger=None):
        self._root        = root
        self._reg         = data_registry
        self._engine      = engine
        self._window      = window
        self._coordinator = coordinator
        self._logger      = logger
        self._profile     = None
        # Inline profile-selector overlay (reused for load/new-game)
        self._selector_frame = None

    def set_profile(self, name: str):
        self._profile = name

    # ── save ──────────────────────────────────────────────────────────────

    def save(self):
        if not self._profile:
            messagebox.showerror("Error", "No active profile."); return
        ok = self._reg.profiles.save(self._profile, self._engine.player_state)
        if ok:
            self._window.post_message(f"✓ Game saved to '{self._profile}'.")
        else:
            messagebox.showerror("Error", "Save failed.")

    # ── load ──────────────────────────────────────────────────────────────

    def load(self):
        """Show an in-window profile selector to pick a profile to load."""
        self._show_selector(callback=self._on_load_selected)

    def _on_load_selected(self, name: str, state: dict):
        self._profile = name
        self._engine._state.set_player(state)
        self._engine._state.clear_dungeon()
        self._engine._combat.clear()
        self._engine.set_profile(name)
        self._coordinator.show_view("city")
        self._coordinator.refresh_active_view()
        self._window.set_player_panel_data(
            self._engine.get_player_panel_data(), self._logger)
        self._window.post_message(f"✓ Loaded profile '{name}'.")

    # ── new game ──────────────────────────────────────────────────────────

    def new_game(self):
        """Show an in-window profile selector to create a new profile."""
        self._show_selector(callback=self._on_new_selected)

    def _on_new_selected(self, name: str, state: dict):
        self._profile = name
        self._engine._state.set_player(state)
        self._engine._state.clear_dungeon()
        self._engine._combat.clear()
        self._engine.set_profile(name)
        self._coordinator.show_view("city")
        self._coordinator.refresh_active_view()
        self._window.set_player_panel_data(
            self._engine.get_player_panel_data(), self._logger)
        self._window.post_message(f"✓ New game started as '{name}'.")

    # ── inline profile selector overlay ──────────────────────────────────

    def _show_selector(self, callback):
        """
        Show the ProfileSelectorFrame overlaid on the main window.
        When the user picks a profile, call callback(name, state) and hide the overlay.
        """
        if self._selector_frame:
            self._selector_frame.destroy()

        result: dict = {}
        done = tk.BooleanVar(value=False)

        def _on_done(*_):
            name  = result.get("name")
            state = result.get("state")
            if self._selector_frame:
                self._selector_frame.destroy()
                self._selector_frame = None
            if name and state:
                callback(name, state)

        done.trace_add("write", _on_done)

        self._selector_frame = ProfileSelectorFrame(
            self._root,
            self._reg.profiles,
            self._reg.config,
            result=result,
            done=done,
            logger=self._logger,
        )
        self._selector_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._selector_frame.lift()

    # ── quit ──────────────────────────────────────────────────────────────

    def quit(self):
        """Show an inline confirmation bar; only destroy on Yes."""
        self._window.show_confirm(
            prompt="Exit the game?  (unsaved progress will be lost)",
            on_yes=self._do_quit,
        )

    def _do_quit(self):
        if self._logger:
            self._logger.shutdown()
        self._root.destroy()
