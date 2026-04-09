import tkinter as tk
from tkinter import ttk
from app.ui.style_manager import StyleManager

class ActionButton(ttk.Frame):
    def __init__(self, parent, label="", on_click=None, **kwargs):
        super().__init__(parent, **kwargs)
        self._on_click = on_click
        self._btn = ttk.Button(
            self,
            text=label,
            style="Action.TButton",
            command=self._handle_click,
        )
        self._btn.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

    def _handle_click(self):
        if self._on_click:
            self._on_click()

    def set_label(self, label):
        self._btn.config(text=label)

    def set_enabled(self, enabled):
        self._btn.state(["!disabled" if enabled else "disabled"])