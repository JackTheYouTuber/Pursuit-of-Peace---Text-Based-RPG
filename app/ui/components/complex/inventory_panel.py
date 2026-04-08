import tkinter as tk

from ..basic.menu_list import MenuList
from ..basic.text_display import TextDisplay

class InventoryPanel(tk.Frame):
    """MenuList (items) + TextDisplay (detail). Layer 2."""

    BG = "#16213e"

    def __init__(self, parent, data=None, on_select=None, logger=None, **kwargs):
        """
        data      — {"items": [{"id": str, "label": str}], "detail": str}
        on_select — callback(item_id: str)
        """
        bg = kwargs.pop('bg', self.BG)
        super().__init__(parent, bg=bg, **kwargs)
        self._logger = logger
        self._on_select = on_select

        data = data or {}

        tk.Label(
            self,
            text="— INVENTORY —",
            font=("Courier", 10, "bold"),
            fg="#7a8fa6",
            bg=self.BG,
        ).pack(pady=(6, 2))

        self._items = MenuList(
            self,
            items=data.get("items", []),
            on_select=self._handle_select,
        )
        self._items.pack(fill=tk.BOTH, expand=True, padx=4, pady=(2, 2))

        self._detail = TextDisplay(self, content=data.get("detail", ""))
        self._detail.pack(fill=tk.X, padx=4, pady=(2, 4))

    def _handle_select(self, item_id):
        if self._logger:
            self._logger.data("inventory_select", item_id)
        if self._on_select:
            self._on_select(item_id)

    def update_items(self, items):
        self._items.set_items(items)

    def update_detail(self, text):
        self._detail.set_content(text)
