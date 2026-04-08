import tkinter as tk

from ..basic.stat_bar import StatBar


class PlayerPanel(tk.Frame):
    """Multiple StatBar instances showing player stats. Layer 2."""

    BG = "#16213e"
    DIVIDER = "#0d1b2a"

    def __init__(self, parent, data=None, logger=None, **kwargs):
        """
        data — {"hp": int, "max_hp": int, "gold": int, "level": int}
        """
        bg = kwargs.pop('bg', self.BG)
        super().__init__(parent, bg=bg, **kwargs)
        self._logger = logger

        data = data or {}

        header = tk.Label(
            self,
            text="— PLAYER —",
            font=("Courier", 10, "bold"),
            fg="#7a8fa6",
            bg=self.BG,
        )
        header.pack(pady=(6, 2))

        hp_val = f"{data.get('hp', 0)} / {data.get('max_hp', 0)}"
        self._hp_bar = StatBar(self, label="HP:", value=hp_val)
        self._hp_bar.pack(fill=tk.X, padx=4, pady=1)

        self._gold_bar = StatBar(self, label="Gold:", value=data.get("gold", 0))
        self._gold_bar.pack(fill=tk.X, padx=4, pady=1)

        self._level_bar = StatBar(self, label="Level:", value=data.get("level", 1))
        self._level_bar.pack(fill=tk.X, padx=4, pady=(1, 6))

    def update_data(self, data):
        hp_val = f"{data.get('hp', 0)} / {data.get('max_hp', 0)}"
        self._hp_bar.set_value(hp_val)
        self._gold_bar.set_value(data.get("gold", 0))
        self._level_bar.set_value(data.get("level", 1))
