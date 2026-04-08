import tkinter as tk


class ActionButton(tk.Frame):
    """Button with label and callback. No logic inside. Layer 1."""

    BG = "#0f3460"
    FG = "#d4c9a8"
    ACTIVE_BG = "#e94560"
    ACTIVE_FG = "#ffffff"
    FONT = ("Courier", 11, "bold")

    def __init__(self, parent, label="", on_click=None, **kwargs):
        bg = kwargs.pop('bg', self.BG)
        super().__init__(parent, bg=bg, **kwargs)
        self._on_click = on_click

        self._btn = tk.Button(
            self,
            text=label,
            font=self.FONT,
            bg=self.BG,
            fg=self.FG,
            activebackground=self.ACTIVE_BG,
            activeforeground=self.ACTIVE_FG,
            relief=tk.FLAT,
            padx=12,
            pady=6,
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
