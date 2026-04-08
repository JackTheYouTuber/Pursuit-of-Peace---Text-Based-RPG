import tkinter as tk
from .theme import BG_DEFAULT, TEXT_FG, ACTIVE_BG, ACTIVE_FG, FONT_BOLD, BUTTON_PADX, BUTTON_PADY

class ActionButton(tk.Frame):
    def __init__(self, parent, label="", on_click=None, **kwargs):
        bg = kwargs.pop('bg', BG_DEFAULT)
        super().__init__(parent, bg=bg, **kwargs)
        self._on_click = on_click
        self._btn = tk.Button(
            self,
            text=label,
            font=FONT_BOLD,
            bg=BG_DEFAULT,
            fg=TEXT_FG,
            activebackground=ACTIVE_BG,
            activeforeground=ACTIVE_FG,
            relief=tk.FLAT,
            padx=BUTTON_PADX,
            pady=BUTTON_PADY,
            cursor="hand2",
            command=self._handle_click,
        )
        self._btn.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

    def _handle_click(self):
        if self._on_click:
            self._on_click()

    def set_label(self, label):
        self._btn.config(text=label)

    def set_enabled(self, enabled):
        self._btn.config(state=tk.NORMAL if enabled else tk.DISABLED)