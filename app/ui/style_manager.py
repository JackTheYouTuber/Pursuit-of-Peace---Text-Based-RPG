"""Central style management for ttk widgets – configured from theme dict."""
import tkinter as tk
from tkinter import ttk
from typing import Dict

class StyleManager:
    _initialized = False
    _theme: Dict = {}

    # Default color constants (can be overridden by theme)
    BG_DEFAULT = "#0f172a"
    PANEL_BG = "#1e293b"

    @classmethod
    def get_theme(cls) -> Dict:
        """Return the current theme dictionary."""
        return cls._theme

    @classmethod
    def init_styles(cls, root: tk.Widget, theme_dict: Dict):
        if cls._initialized:
            return
            
        cls._initialized = True
        cls._theme = theme_dict
        global_cfg = theme_dict.get("global", {})
        
        # Extract global values
        bg = global_cfg.get("bg", "#0f172a")
        fg = global_cfg.get("fg", "#e2e8f0")
        font_family = global_cfg.get("font_family", "Segoe UI")
        font_size = global_cfg.get("font_size", 10)
        font_body = (font_family, font_size)
        font_bold = (font_family, font_size, "bold")
        
        style = ttk.Style()
        if 'clam' in style.theme_names():
            style.theme_use('clam')
        
        # Global styles
        style.configure("TFrame", background=bg)
        style.configure("TLabel", background=bg, foreground=fg, font=font_body)
        style.configure("TLabelframe", background=bg, foreground=fg)
        style.configure("TLabelframe.Label", background=bg, foreground=fg)
        
        # Buttons – use theme colors from ActionButton section or fallback
        action_cfg = theme_dict.get("ActionButton", {})
        btn_bg = action_cfg.get("bg", "#3b82f6")
        btn_fg = action_cfg.get("fg", "#ffffff")
        style.configure("TButton",
                        background=bg,
                        foreground=fg,
                        borderwidth=1,
                        padding=(12, 6),
                        font=font_body)
        style.map("TButton",
                  background=[("active", btn_bg), ("pressed", btn_bg)],
                  foreground=[("active", btn_fg)])
        
        style.configure("Active.TButton",
                        background=btn_bg,
                        foreground=btn_fg,
                        font=font_bold,
                        padding=(12, 6))
        style.map("Active.TButton",
                  background=[("active", btn_bg)])
        
        style.configure("Action.TButton",
                        background=btn_bg,
                        foreground=btn_fg,
                        borderwidth=0,
                        padding=(16, 8),
                        font=font_bold)
        style.map("Action.TButton",
                  background=[("active", btn_bg)])
        
        # Entry
        entry_cfg = theme_dict.get("InputField", {})
        entry_bg = entry_cfg.get("bg", "#334155")
        style.configure("TEntry",
                        fieldbackground=entry_bg,
                        foreground=fg,
                        borderwidth=1,
                        relief="solid",
                        padding=6)
        style.map("TEntry",
                  fieldbackground=[("focus", entry_bg)])
        
        # Scrollbar
        style.configure("TScrollbar",
                        background=bg,
                        troughcolor=bg,
                        arrowcolor=fg,
                        borderwidth=0)
        
        # Frame variants
        style.configure("Card.TFrame", background=entry_bg, relief="groove", borderwidth=1)
        panel_bg = theme_dict.get("MenuList", {}).get("bg", "#1e293b")
        style.configure("Panel.TFrame", background=panel_bg)