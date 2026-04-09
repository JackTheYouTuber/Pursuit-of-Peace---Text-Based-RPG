import tkinter as tk
from tkinter import ttk
from app.ui.style_manager import StyleManager

class MenuList(ttk.Frame):
    def __init__(self, parent, items=None, on_select=None, columns=1, **kwargs):
        super().__init__(parent, **kwargs)
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
            btn = ttk.Button(
                self,
                text=label,
                style="TButton",
                command=lambda i=item_id: self._handle_select(i),
            )
            row = idx // cols
            col = idx % cols
            btn.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
            self._buttons.append(btn)

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