"""
app.py — the core of cores.

Wires the three pillars together: Data, Logic, UI.
Has no game logic. Has no rendering. Just assembly.
"""
import tkinter as tk
from app.version import VERSION_LABEL
from app.data.init.registry         import DataRegistry
from app.data.init.engine_factory   import EngineFactory
from app.data.init.profile_selector import ProfileSelector
from app.ui.core.window             import MainWindow
from app.ui.core.game_actions       import GameActions
from app.ui.core.profile_actions    import ProfileActions
from app.ui.complex.assembler       import UIAssembler
from app.ui.complex.coordinator     import ViewCoordinator
from app.ui.simple.menu             import GameMenu


class App:
    W, H = 1024, 720
    MIN_W, MIN_H = 800, 560

    def __init__(self, logger=None):
        self._logger = logger
        self._root = tk.Tk()
        self._root.title(f"Pursuit of Peace  {VERSION_LABEL}")
        self._root.geometry(f"{self.W}x{self.H}")
        self._root.minsize(self.MIN_W, self.MIN_H)

        # ── Data ────────────────────────────────────────────────────────
        self._reg = DataRegistry()

        # ── Profile selection (blocks until chosen) ─────────────────────
        name, state = ProfileSelector.select_or_create(
            self._root, self._reg.profiles, self._reg.config, logger)
        if not name:
            self._root.destroy()
            return

        # ── Logic ───────────────────────────────────────────────────────
        self._engine = EngineFactory.create(state, profile_name=name, logger=logger)

        # ── UI skeleton ─────────────────────────────────────────────────
        self._window = MainWindow(self._root)

        self._assembler = UIAssembler(
            root=self._window.get_content_frame(),
            callbacks={},
            logger=logger,
        )
        self._coordinator = ViewCoordinator(
            content_frame=self._window.get_content_frame(),
            assembler=self._assembler,
            game_engine=self._engine,
            logger=logger,
        )

        # ── Controllers ─────────────────────────────────────────────────
        self._game = GameActions(
            engine=self._engine,
            assembler=self._assembler,
            coordinator=self._coordinator,
            data_registry=self._reg,
            window=self._window,
            logger=logger,
        )
        self._profile = ProfileActions(
            root=self._root,
            data_registry=self._reg,
            engine=self._engine,
            window=self._window,
            coordinator=self._coordinator,
            logger=logger,
        )
        self._profile.set_profile(name)

        # ── Callbacks ───────────────────────────────────────────────────
        self._assembler._callbacks.update({
            "location_action":  self._game.on_city_action,
            "dungeon_action":   self._game.on_dungeon_action,
            "combat_action":    self._game.on_combat_action,
            "inventory_select": self._game.on_inventory_select,
            "inventory_action": self._game.on_inventory_action,
        })

        # ── Navigation sidebar ──────────────────────────────────────────
        for key, label in (("city","  Explore"), ("inventory","  Inventory"), ("lore","  Lore")):
            self._window.add_nav_button(key, label, lambda k=key: self._show(k))

        # ── Menu bar ────────────────────────────────────────────────────
        GameMenu(self._root, callbacks={
            "new_game":  self._profile.new_game,
            "save_game": self._profile.save,
            "load_game": self._profile.load,
            "quit":      self._profile.quit,
        })

        # ── First view ──────────────────────────────────────────────────
        self._coordinator.show_view("city")
        self._game.refresh()

        if logger: logger.system("App initialised.")

    def _show(self, view: str):
        self._coordinator.show_view(view)
        for k in ("city", "inventory", "lore"):
            self._window.highlight_nav_button(k, k == view)

    def run(self):
        self._root.mainloop()
