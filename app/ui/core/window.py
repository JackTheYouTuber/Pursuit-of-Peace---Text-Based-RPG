import tkinter as tk
from tkinter import ttk
from app.ui.simple.style_manager import StyleManager
from app.ui.simple.panels.player_panel import PlayerPanel


class MainWindow:
    """Manages the sidebar and content frame within an existing root."""

    BG = StyleManager.BG_DEFAULT
    SIDEBAR_BG = StyleManager.PANEL_BG

    def __init__(self, root: tk.Tk, theme: dict = None):
        self.root = root
        self.root.configure(bg=self.BG)
        if theme is None:
            from app.ui.simple.theme import load_theme
            theme = load_theme()
        StyleManager.init_styles(root, theme)
        self._sidebar = None
        self._player_panel = None
        self._nav_buttons = {}
        self._content_frame = None
        self._msg_display = None          # inline message log (TextDisplay)
        self._confirm_bar = None          # inline Yes/No confirmation strip
        self._build_layout()

    def _build_layout(self):
        self.root.columnconfigure(0, weight=0, minsize=200)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=0)   # message strip row

        # Sidebar
        self._sidebar = ttk.Frame(self.root, style="Panel.TFrame", width=200)
        self._sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self._sidebar.grid_propagate(False)

        self._player_panel = PlayerPanel(self._sidebar, data={}, logger=None)
        self._player_panel.pack(fill=tk.X, padx=4, pady=4)

        ttk.Separator(self._sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=4)

        # Content frame
        self._content_frame = ttk.Frame(self.root, style="TFrame")
        self._content_frame.grid(row=0, column=1, sticky="nsew", padx=4, pady=(4, 0))
        self._content_frame.rowconfigure(0, weight=1)
        self._content_frame.columnconfigure(0, weight=1)

        # ── Message log strip (below content, above window bottom) ────────
        msg_strip = tk.Frame(self.root, bg="#0f172a", height=80)
        msg_strip.grid(row=1, column=1, sticky="ew", padx=4, pady=(2, 4))
        msg_strip.grid_propagate(False)

        tk.Label(msg_strip, text="Messages",
                 bg="#0f172a", fg="#475569",
                 font=("Segoe UI", 7)).pack(anchor=tk.W, padx=6, pady=(2, 0))

        try:
            from app.ui.simple.basic.text_display import TextDisplay
            self._msg_display = TextDisplay(msg_strip, content="")
            self._msg_display.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0, 4))
        except Exception:
            # Fallback: plain tk.Text
            self._msg_display = tk.Text(msg_strip, wrap=tk.WORD, height=4,
                                        bg="#1e293b", fg="#e2e8f0",
                                        state=tk.DISABLED,
                                        font=("Segoe UI", 9),
                                        relief=tk.FLAT)
            self._msg_display.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0, 4))

        # ── Inline confirmation bar (hidden initially) ────────────────────
        self._confirm_bar    = tk.Frame(self.root, bg="#3b1515")
        self._confirm_label  = tk.Label(self._confirm_bar, text="",
                                        bg="#3b1515", fg="#f87171",
                                        font=("Segoe UI", 9))
        self._confirm_label.pack(side=tk.LEFT, padx=10, pady=4)
        self._confirm_yes_btn = tk.Button(self._confirm_bar, text="Yes",
                                          bg="#7f1d1d", fg="#fff",
                                          relief=tk.FLAT, padx=12, pady=3,
                                          font=("Segoe UI", 9))
        self._confirm_yes_btn.pack(side=tk.LEFT, padx=4)
        self._confirm_no_btn = tk.Button(self._confirm_bar, text="No",
                                         bg="#334155", fg="#e2e8f0",
                                         relief=tk.FLAT, padx=10, pady=3,
                                         font=("Segoe UI", 9))
        self._confirm_no_btn.pack(side=tk.LEFT, padx=2)
        # Not gridded until show_confirm() is called

    # ── public: player panel ──────────────────────────────────────────────

    def set_player_panel_data(self, data: dict, logger=None):
        if self._player_panel:
            self._player_panel.update_data(data)

    # ── public: nav buttons ───────────────────────────────────────────────

    def add_nav_button(self, view_key: str, label: str, command):
        btn = ttk.Button(self._sidebar, text=label, style="TButton", command=command)
        btn.pack(fill=tk.X, padx=4, pady=2)
        self._nav_buttons[view_key] = btn

    def highlight_nav_button(self, view_key: str, active: bool):
        if view_key in self._nav_buttons:
            self._nav_buttons[view_key].configure(
                style="Active.TButton" if active else "TButton")

    def get_content_frame(self) -> ttk.Frame:
        return self._content_frame

    # ── public: inline message log ────────────────────────────────────────

    def post_message(self, msg: str) -> None:
        """Append a game-event message to the inline message strip."""
        if not msg or not self._msg_display:
            return
        text = msg.strip() + "\n"
        try:
            if hasattr(self._msg_display, "append"):
                self._msg_display.append(text)
            else:
                self._msg_display.configure(state=tk.NORMAL)
                self._msg_display.insert(tk.END, text)
                self._msg_display.see(tk.END)
                self._msg_display.configure(state=tk.DISABLED)
        except Exception:
            pass

    # ── public: inline confirmation bar ──────────────────────────────────

    def show_confirm(self, prompt: str, on_yes, on_no=None) -> None:
        """
        Show an inline Yes/No bar below the content area.
        *on_yes* and *on_no* are zero-argument callables.
        The bar hides itself after either button is pressed.
        """
        self._confirm_label.config(text=prompt)

        def _yes():
            self.hide_confirm()
            on_yes()

        def _no():
            self.hide_confirm()
            if on_no:
                on_no()

        self._confirm_yes_btn.config(command=_yes)
        self._confirm_no_btn.config(command=_no)
        # Place the confirm bar between content and message strip
        self._confirm_bar.grid(row=1, column=1, sticky="ew", padx=4, pady=2)
        self._confirm_bar.lift()

    def hide_confirm(self) -> None:
        self._confirm_bar.grid_forget()