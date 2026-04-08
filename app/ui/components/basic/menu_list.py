import tkinter as tk


class MenuList(tk.Frame):
    """List of labeled options rendered as clickable rows. Layer 1 — no project imports."""

    BG = "#16213e"
    FG = "#d4c9a8"
    HOVER_BG = "#0f3460"
    ACTIVE_BG = "#e94560"
    ACTIVE_FG = "#ffffff"
    FONT = ("Courier", 11)

    def __init__(self, parent, items=None, on_select=None, **kwargs):
        """
        items     — list of {"id": str, "label": str}
        on_select — callback(item_id: str)
        """
        bg = kwargs.pop('bg', self.BG)
        super().__init__(parent, bg=bg, **kwargs)
        self._on_select = on_select
        self._buttons = []
        self._items = []

        if items:
            self.set_items(items)

    def set_items(self, items):
        """Replace the current list of options."""
        for btn in self._buttons:
            btn.destroy()
        self._buttons.clear()
        self._items = list(items)

        for item in self._items:
            item_id = item["id"]
            label = item["label"]
            btn = tk.Button(
                self,
                text=label,
                anchor=tk.W,
                font=self.FONT,
                bg=self.BG,
                fg=self.FG,
                activebackground=self.ACTIVE_BG,
                activeforeground=self.ACTIVE_FG,
                relief=tk.FLAT,
                padx=8,
                pady=4,
                cursor="hand2",
                command=lambda i=item_id: self._handle_select(i),
            )
            btn.pack(fill=tk.X, pady=1)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.HOVER_BG))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.BG))
            self._buttons.append(btn)

    def _handle_select(self, item_id):
        if self._on_select:
            self._on_select(item_id)

    def clear(self):
        self.set_items([])
