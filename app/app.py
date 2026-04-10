"""
Pursuit of Peace - Main Application Entry Point

Initializes the Tkinter root window, loads player profile,
sets up the game engine, UI assembler, and action controllers.
"""

import tkinter as tk
from app.version import VERSION_LABEL
from app.data_loader import DataLoader
from app.profile_manager import ProfileManager
from app.init.profile_selector import ProfileSelector
from app.init.engine_factory import EngineFactory
from app.ui.main_window import MainWindow
from app.ui.menu import GameMenu
from app.ui_assembler import UIAssembler
from app.view_coordinator import ViewCoordinator
from app.controllers.game_actions import GameActions
from app.controllers.profile_actions import ProfileActions


class App:
    """Main application class that orchestrates the game lifecycle."""

    WINDOW_TITLE = f"Pursuit of Peace  {VERSION_LABEL}"
    WINDOW_W = 1024
    WINDOW_H = 720
    MIN_W = 800
    MIN_H = 560

    def __init__(self, logger=None):
        self._logger = logger

        # ----- Root window -----
        self._root = tk.Tk()
        self._root.title(self.WINDOW_TITLE)
        self._root.geometry(f"{self.WINDOW_W}x{self.WINDOW_H}")
        self._root.minsize(self.MIN_W, self.MIN_H)

        # ----- Core data -----
        self._loader = DataLoader(logger=self._logger)
        self._profile_mgr = ProfileManager(logger=self._logger)

        # ----- Profile selection (blocks until chosen) -----
        profile_name, profile_state = ProfileSelector.select_or_create(
            self._root, self._profile_mgr, self._loader, self._logger
        )
        if not profile_name:
            self._root.destroy()
            return
        self._profile_name = profile_name

        # ----- UI layout (sidebar + content) -----
        self._window = MainWindow(self._root)

        # ----- Game engine with loaded profile + profile manager for death deletion -----
        self._engine = EngineFactory.create(
            profile_state, self._loader,
            profile_manager=self._profile_mgr,
            profile_name=self._profile_name,
            logger=self._logger,
        )

        # ----- UI Assembler & Coordinator -----
        self._assembler = UIAssembler(
            root=self._window.get_content_frame(),
            callbacks={},
            logger=self._logger,
        )
        self._coordinator = ViewCoordinator(
            content_frame=self._window.get_content_frame(),
            assembler=self._assembler,
            game_engine=self._engine,
            logger=self._logger,
        )

        # ----- Controllers -----
        self._game_actions = GameActions(
            engine=self._engine,
            assembler=self._assembler,
            coordinator=self._coordinator,
            loader=self._loader,
            window=self._window,
            logger=self._logger,
        )
        self._profile_actions = ProfileActions(
            root=self._root,
            profile_mgr=self._profile_mgr,
            loader=self._loader,
            engine=self._engine,
            window=self._window,
            coordinator=self._coordinator,
            logger=self._logger,
        )
        self._profile_actions.set_current_profile(self._profile_name)

        # ----- Connect callbacks to assembler -----
        self._assembler._callbacks.update({
            "location_action": self._game_actions.on_location_action,
            "dungeon_action":  self._game_actions.on_dungeon_action,
            "combat_action":   self._game_actions.on_combat_action,
            "inventory_select": self._game_actions.on_inventory_select,
            "inventory_action": self._game_actions.on_inventory_action,
        })

        # ----- Navigation buttons -----
        nav_buttons = [
            ("city",      "  Explore"),
            ("inventory", "  Inventory"),
            ("lore",      "  Lore"),
        ]
        for view_key, label in nav_buttons:
            self._window.add_nav_button(
                view_key, label,
                lambda k=view_key: self._show_view(k)
            )

        # ----- Menu -----
        self._menu = GameMenu(
            self._root,
            callbacks={
                "new_game":  self._profile_actions.new_game,
                "save_game": self._profile_actions.save_game,
                "load_game": self._profile_actions.load_game,
                "quit":      self._profile_actions.quit_app,
            }
        )

        # ----- Initial view -----
        self._coordinator.show_view("city")
        self._game_actions.refresh_current_view()

        if self._logger:
            self._logger.system("App initialised.")

    def _show_view(self, view_name: str):
        if view_name not in ("city", "dungeon", "combat", "inventory", "lore"):
            return
        self._coordinator.show_view(view_name)
        for key in ("city", "inventory", "lore"):
            self._window.highlight_nav_button(key, key == view_name)

    def run(self):
        self._root.mainloop()
