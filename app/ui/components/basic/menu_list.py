import tkinter as tk
from .theme import PANEL_BG, TEXT_FG, ACTIVE_BG, ACTIVE_FG, HOVER_BG, FONT_BODY, PAD_SMALL

class MenuList(tk.Frame):
    def __init__(self, parent, items=None, on_select=None, columns=1, **kwargs):
        bg = kwargs.pop('bg', PANEL_BG)
        super().__init__(parent, bg=bg, **kwargs)
        self._on_select = on_select
        self._buttons = []
        self._items = []
        self._columns = columns
        if items:
            self.set_items(items)

    def set_items(self, items):
        for btn in self._buttons:
            btn.destroy()
        self._buttons.clear()
        self._items = list(items)

        cols = self._columns
        for idx, item in enumerate(self._items):
            item_id = item["id"]
            label = item["label"]
            btn = tk.Button(
                self,
                text=label,
                font=FONT_BODY,
                bg=PANEL_BG,
                fg=TEXT_FG,
                activebackground=ACTIVE_BG,
                activeforeground=ACTIVE_FG,
                relief=tk.FLAT,
                padx=PAD_SMALL,
                pady=PAD_SMALL,
                cursor="hand2",
                command=lambda i=item_id: self._handle_select(i),
            )
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=HOVER_BG))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=PANEL_BG))
            row = idx // cols
            col = idx % cols
            btn.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
            self._buttons.append(btn)

        # Configure grid weights
        for c in range(cols):
            self.columnconfigure(c, weight=1)
        rows_needed = (len(items) + cols - 1) // cols
        for r in range(rows_needed):
            self.rowconfigure(r, weight=1)

    def _handle_select(self, item_id):
        if self._on_select:
            self._on_select(item_id)

    def clear(self):
        self.set_items([])