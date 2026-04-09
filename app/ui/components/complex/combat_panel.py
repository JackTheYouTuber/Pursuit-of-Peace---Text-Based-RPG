import tkinter as tk
from tkinter import ttk
from app.ui.style_manager import StyleManager
import app.ui.constants as const
from ..basic.text_display import TextDisplay
from ..basic.menu_list import MenuList
from ..basic.stat_bar import StatBar

class CombatPanel(ttk.Frame):
    def __init__(self, parent, data=None, on_action=None, logger=None, **kwargs):
        super().__init__(parent, **kwargs)
        self._logger = logger
        self._on_action = on_action

        data = data or {}

        tk.Label(
            self,
            text="— COMBAT —",
            font=("Segoe UI", 10, "bold"),
            bg=const.CARD_BG,
        ).pack(pady=(6, 2))

        enemy_label = data.get("enemy_name", "Enemy")
        self._enemy_hp_bar = StatBar(
            self,
            label=f"{enemy_label} HP:",
            value=data.get("enemy_hp", 0),
        )
        self._enemy_hp_bar.pack(fill=tk.X, padx=4, pady=(0, 2))

        self._player_hp_bar = StatBar(
            self,
            label="Your HP:",
            value=data.get("player_hp", 0),
        )
        self._player_hp_bar.pack(fill=tk.X, padx=4, pady=(0, 4))

        self._log = TextDisplay(
            self,
            content=data.get("log", ""),
        )
        self._log.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)

        self._actions = MenuList(
            self,
            items=data.get("actions", []),
            on_select=self._handle_action,
        )
        self._actions.pack(fill=tk.X, padx=4, pady=(2, 6))

    def _handle_action(self, action_id: str) -> None:
        if self._logger:
            self._logger.data("combat_action", action_id)
        if self._on_action:
            self._on_action(action_id)

    def update_enemy_hp(self, enemy_name: str, hp: int) -> None:
        self._enemy_hp_bar.set_label(f"{enemy_name} HP:")
        self._enemy_hp_bar.set_value(hp)

    def update_player_hp(self, hp: int) -> None:
        self._player_hp_bar.set_value(hp)

    def set_actions(self, actions: list) -> None:
        self._actions.set_items(actions)

    def set_log(self, text: str) -> None:
        self._log.set_content(text)

    def append_log(self, text: str) -> None:
        self._log.append(text)