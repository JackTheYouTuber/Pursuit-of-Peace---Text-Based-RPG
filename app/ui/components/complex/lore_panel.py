import tkinter as tk
from tkinter import ttk
from app.ui.style_manager import StyleManager
import app.ui.constants as const
from ..basic.text_display import TextDisplay


class LorePanel(ttk.Frame):
    def __init__(self, parent, data=None, logger=None, **kwargs):
        super().__init__(parent, **kwargs)
        self._logger = logger

        data = data or {}

        tk.Label(
            self,
            text="— LORE —",
            font=("Segoe UI", 10, "bold"),
            bg=const.CARD_BG,
        ).pack(pady=(6, 2))

        content = self._format_entries(data.get("entries", []))
        self._display = TextDisplay(self, content=content)
        self._display.pack(fill=tk.BOTH, expand=True, padx=4, pady=(2, 6))

    @staticmethod
    def _format_entries(entries: list) -> str:
        lines = []
        for entry in entries:
            type_tag = entry.get("type", "").upper()
            text = entry.get("text", "")
            lines.append(f"[{type_tag}] {text}")
        return "\n\n".join(lines)

    def update_entries(self, entries: list) -> None:
        content = self._format_entries(entries)
        self._display.set_content(content)