import tkinter as tk
from tkinter import ttk
from app.ui.style_manager import StyleManager
from app.ui.components.complex.player_panel import PlayerPanel


class MainWindow:
    """Manages the sidebar and content frame within an existing root."""

    BG = StyleManager.BG_DEFAULT
    SIDEBAR_BG = StyleManager.PANEL_BG

    def __init__(self, root: tk.Tk, theme: dict = None):
        self.root = root
        self.root.configure(bg=self.BG)
        if theme is None:
            from app.ui.theme import load_theme
            theme = load_theme()
        StyleManager.init_styles(root, theme)
        self._sidebar = None
        self._player_panel = None
        self._nav_buttons = {}
        self._content_frame = None
        self._build_layout()

    def _build_layout(self):
        self.root.columnconfigure(0, weight=0, minsize=200)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        self._sidebar = ttk.Frame(self.root, style="Panel.TFrame", width=200)
        self._sidebar.grid(row=0, column=0, sticky="nsew")
        self._sidebar.grid_propagate(False)

        self._player_panel = PlayerPanel(self._sidebar, data={}, logger=None)
        self._player_panel.pack(fill=tk.X, padx=4, pady=4)

        ttk.Separator(self._sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=4)

        self._content_frame = ttk.Frame(self.root, style="TFrame")
        self._content_frame.grid(row=0, column=1, sticky="nsew", padx=4, pady=4)
        self._content_frame.rowconfigure(0, weight=1)
        self._content_frame.columnconfigure(0, weight=1)

    def set_player_panel_data(self, data: dict, logger=None):
        if self._player_panel:
            self._player_panel.update_data(data)

    def add_nav_button(self, view_key: str, label: str, command):
        btn = ttk.Button(
            self._sidebar,
            text=label,
            style="TButton",
            command=command,
        )
        btn.pack(fill=tk.X, padx=4, pady=2)
        self._nav_buttons[view_key] = btn

    def highlight_nav_button(self, view_key: str, active: bool):
        if view_key in self._nav_buttons:
            style = "Active.TButton" if active else "TButton"
            self._nav_buttons[view_key].configure(style=style)

    def get_content_frame(self) -> ttk.Frame:
        return self._content_frame