import tkinter as tk
from app.ui.components.complex.player_panel import PlayerPanel


class MainWindow:
    """Manages the sidebar and content frame within an existing root."""

    BG = "#0d1b2a"
    SIDEBAR_BG = "#16213e"

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.configure(bg=self.BG)
        self._sidebar = None
        self._player_panel = None
        self._nav_buttons = {}
        self._content_frame = None
        self._build_layout()

    def _build_layout(self):
        self.root.columnconfigure(0, weight=0, minsize=200)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        self._sidebar = tk.Frame(self.root, bg=self.SIDEBAR_BG, width=200)
        self._sidebar.grid(row=0, column=0, sticky="nsew")
        self._sidebar.grid_propagate(False)

        self._player_panel = PlayerPanel(self._sidebar, data={}, logger=None)
        self._player_panel.pack(fill=tk.X)

        tk.Frame(self._sidebar, bg=self.BG, height=2).pack(fill=tk.X, pady=4)

        self._content_frame = tk.Frame(self.root, bg=self.BG)
        self._content_frame.grid(row=0, column=1, sticky="nsew", padx=4, pady=4)
        self._content_frame.rowconfigure(0, weight=1)
        self._content_frame.columnconfigure(0, weight=1)

    def set_player_panel_data(self, data: dict, logger=None):
        if self._player_panel:
            self._player_panel.update_data(data)

    def add_nav_button(self, view_key: str, label: str, command):
        btn = tk.Button(
            self._sidebar,
            text=label,
            font=("Courier", 11),
            bg=self.SIDEBAR_BG,
            fg="#d4c9a8",
            activebackground="#0f3460",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            anchor=tk.W,
            padx=12,
            pady=6,
            cursor="hand2",
            command=command,
        )
        btn.pack(fill=tk.X)
        self._nav_buttons[view_key] = btn

    def highlight_nav_button(self, view_key: str, active: bool):
        if view_key in self._nav_buttons:
            self._nav_buttons[view_key].config(
                bg="#0f3460" if active else self.SIDEBAR_BG
            )

    def get_content_frame(self) -> tk.Frame:
        return self._content_frame