import tkinter as tk
from .theme import PANEL_BG, MUTED_FG, ACCENT_FG, FONT_SMALL, FONT_BOLD, PAD_SMALL

class StatBar(tk.Frame):
    def __init__(self, parent, label="", value=0, **kwargs):
        bg = kwargs.pop('bg', PANEL_BG)
        super().__init__(parent, bg=bg, **kwargs)
        self._label_var = tk.StringVar(value=label)
        self._value_var = tk.StringVar(value=str(value))

        tk.Label(
            self,
            textvariable=self._label_var,
            font=FONT_SMALL,
            fg=MUTED_FG,
            bg=PANEL_BG,
            anchor=tk.W,
        ).pack(side=tk.LEFT, padx=(PAD_SMALL, 2))

        tk.Label(
            self,
            textvariable=self._value_var,
            font=FONT_BOLD,
            fg=ACCENT_FG,
            bg=PANEL_BG,
            anchor=tk.W,
        ).pack(side=tk.LEFT, padx=(0, PAD_SMALL))

    def set_value(self, value):
        self._value_var.set(str(value))

    def set_label(self, label):
        self._label_var.set(label)