import tkinter as tk
from tkinter import ttk
from app.ui.style_manager import StyleManager
import app.ui.constants as const   # <-- ADD THIS
from ..basic.stat_bar import StatBar

class PlayerPanel(ttk.Frame):
    def __init__(self, parent, data=None, logger=None, **kwargs):
        super().__init__(parent, **kwargs)
        self._logger = logger

        data = data or {}

        tk.Label(
            self,
            text="— PLAYER —",
            font=("Segoe UI", 10, "bold"),
            bg=const.CARD_BG,
        ).pack(pady=(6, 2))

        hp_val = f"{data.get('hp', 0)} / {data.get('max_hp', 0)}"
        self._hp_bar = StatBar(self, label="HP:", value=hp_val)
        self._hp_bar.pack(fill=tk.X, padx=4, pady=1)

        self._gold_bar = StatBar(self, label="Gold:", value=data.get("gold", 0))
        self._gold_bar.pack(fill=tk.X, padx=4, pady=1)

        self._level_bar = StatBar(self, label="Level:", value=data.get("level", 1))
        self._level_bar.pack(fill=tk.X, padx=4, pady=(1, 6))

    def update_data(self, data: dict) -> None:
        hp_val = f"{data.get('hp', 0)} / {data.get('max_hp', 0)}"
        self._hp_bar.set_value(hp_val)
        self._gold_bar.set_value(data.get("gold", 0))
        self._level_bar.set_value(data.get("level", 1))