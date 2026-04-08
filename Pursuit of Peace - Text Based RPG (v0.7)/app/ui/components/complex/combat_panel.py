import tkinter as tk

from app.ui.components.basic.text_display import TextDisplay
from app.ui.components.basic.menu_list import MenuList
from app.ui.components.basic.stat_bar import StatBar


class CombatPanel(tk.Frame):
    """TextDisplay (log) + MenuList (actions) + StatBars (enemy hp, player hp).

    v0.7 — Added player HP bar so the counter-attack damage is visible.
    """

    BG = "#1a0a0a"

    def __init__(self, parent, data=None, on_action=None, logger=None, **kwargs):
        """
        data      — {"log": str, "actions": [{"id": str, "label": str}],
                     "enemy_name": str, "enemy_hp": int,
                     "player_hp": int, "player_max_hp": int}
        on_action — callback(action_id: str)
        """
        bg = kwargs.pop('bg', self.BG)
        super().__init__(parent, bg=bg, **kwargs)
        self._logger = logger
        self._on_action = on_action

        data = data or {}

        tk.Label(
            self,
            text="— COMBAT —",
            font=("Courier", 10, "bold"),
            fg="#e94560",
            bg=self.BG,
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
            bg="#110808",
            fg="#e2b96f",
        )
        self._log.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)

        self._actions = MenuList(
            self,
            items=data.get("actions", []),
            on_select=self._handle_action,
        )
        self._actions.pack(fill=tk.X, padx=4, pady=(2, 6))

    def _handle_action(self, action_id):
        if self._logger:
            self._logger.data("combat_action", action_id)
        if self._on_action:
            self._on_action(action_id)

    def update_enemy_hp(self, enemy_name, hp):
        self._enemy_hp_bar.set_label(f"{enemy_name} HP:")
        self._enemy_hp_bar.set_value(hp)

    def update_player_hp(self, hp):
        self._player_hp_bar.set_value(hp)

    def set_actions(self, actions):
        self._actions.set_items(actions)

    def set_log(self, text: str):
        """Replace the entire log content."""
        self._log.set_content(text)

    def append_log(self, text: str):
        self._log.append(text)
