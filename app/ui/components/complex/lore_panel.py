import tkinter as tk

from app.ui.components.basic.text_display import TextDisplay


class LorePanel(tk.Frame):
    """TextDisplay for ambient/lore text. Layer 2."""

    BG = "#16213e"

    def __init__(self, parent, data=None, logger=None, **kwargs):
        """
        data — {"entries": [{"text": str, "type": str}]}
        """
        bg = kwargs.pop('bg', self.BG)
        super().__init__(parent, bg=bg, **kwargs)
        self._logger = logger

        data = data or {}

        tk.Label(
            self,
            text="— LORE —",
            font=("Courier", 10, "bold"),
            fg="#7a8fa6",
            bg=self.BG,
        ).pack(pady=(6, 2))

        content = self._format_entries(data.get("entries", []))
        self._display = TextDisplay(self, content=content, fg="#a89060")
        self._display.pack(fill=tk.BOTH, expand=True, padx=4, pady=(2, 6))

    def _format_entries(self, entries):
        lines = []
        for entry in entries:
            type_tag = entry.get("type", "").upper()
            text = entry.get("text", "")
            lines.append(f"[{type_tag}] {text}")
        return "\n\n".join(lines)

    def update_entries(self, entries):
        content = self._format_entries(entries)
        self._display.set_content(content)
