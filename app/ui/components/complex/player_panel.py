import tkinter as tk
from tkinter import ttk
import app.ui.constants as const
from ..basic.stat_bar import StatBar


class PlayerPanel(ttk.Frame):
    """Sidebar player status: HP, gold, level, equipment, buffs, kills."""

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
        self._level_bar.pack(fill=tk.X, padx=4, pady=1)

        self._equip_bar = StatBar(self, label="Gear:", value=data.get("equipment", "—"))
        self._equip_bar.pack(fill=tk.X, padx=4, pady=1)

        self._kills_bar = StatBar(self, label="Kills:", value=data.get("kills", 0))
        self._kills_bar.pack(fill=tk.X, padx=4, pady=1)

        # Buff/debuff display — only shown when active
        self._buff_frame = tk.Frame(self, bg=const.CARD_BG)
        self._buff_frame.pack(fill=tk.X, padx=4, pady=(2, 6))
        self._buff_label_title = tk.Label(
            self._buff_frame,
            text="Effects:",
            font=("Segoe UI", 9),
            fg="#94a3b8",
            bg=const.CARD_BG,
            anchor="w",
        )
        self._buff_text = tk.Label(
            self._buff_frame,
            text=data.get("buffs", ""),
            font=("Segoe UI", 9, "italic"),
            fg="#a3e635",
            bg=const.CARD_BG,
            anchor="w",
            wraplength=160,
            justify=tk.LEFT,
        )
        self._refresh_buff_display(data.get("buffs", ""))

    def _refresh_buff_display(self, buff_text: str) -> None:
        if buff_text:
            self._buff_label_title.pack(side=tk.TOP, fill=tk.X)
            self._buff_text.config(text=buff_text)
            self._buff_text.pack(side=tk.TOP, fill=tk.X)
        else:
            self._buff_label_title.pack_forget()
            self._buff_text.pack_forget()

    def update_data(self, data: dict) -> None:
        hp_val = f"{data.get('hp', 0)} / {data.get('max_hp', 0)}"
        self._hp_bar.set_value(hp_val)
        self._gold_bar.set_value(data.get("gold", 0))
        self._level_bar.set_value(data.get("level", 1))
        self._equip_bar.set_value(data.get("equipment", "—"))
        self._kills_bar.set_value(data.get("kills", 0))
        self._refresh_buff_display(data.get("buffs", ""))
