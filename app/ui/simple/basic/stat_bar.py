import tkinter as tk
from tkinter import ttk
from app.ui.simple.style_manager import StyleManager
import app.ui.simple.constants as const

class StatBar(ttk.Frame):
    def __init__(self, parent, label="", value=0, **kwargs):
        super().__init__(parent, **kwargs)
        theme = StyleManager.get_theme()
        stat_cfg = theme.get("StatBar", {})
        label_fg = stat_cfg.get("label_fg", "#94a3b8")
        value_fg = stat_cfg.get("value_fg", "#fbbf24")
        global_cfg = theme.get("global", {})
        font_family = global_cfg.get("font_family", "Segoe UI")
        font_size = global_cfg.get("font_size", 10)

        self._label_var = tk.StringVar(value=label)
        self._value_var = tk.StringVar(value=str(value))

        # Use const.CARD_BG instead of self.cget("background")
        tk.Label(self, textvariable=self._label_var, fg=label_fg,
                 bg=const.CARD_BG, font=(font_family, font_size)).pack(side=tk.LEFT, padx=(4, 2))
        tk.Label(self, textvariable=self._value_var, fg=value_fg,
                 bg=const.CARD_BG, font=(font_family, font_size, "bold")).pack(side=tk.LEFT, padx=(0, 4))


    def set_value(self, value):
        self._value_var.set(str(value))

    def set_label(self, label):
        self._label_var.set(label)
