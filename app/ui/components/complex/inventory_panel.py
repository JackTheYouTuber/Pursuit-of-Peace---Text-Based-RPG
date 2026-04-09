import tkinter as tk
from tkinter import ttk
from app.ui.style_manager import StyleManager
import app.ui.constants as const
from ..basic.menu_list import MenuList
from ..basic.text_display import TextDisplay


class InventoryPanel(ttk.Frame):
    def __init__(self, parent, data=None, on_select=None, logger=None, **kwargs):
        super().__init__(parent, **kwargs)
        self._logger = logger
        self._on_select = on_select

        data = data or {}

        tk.Label(
            self,
            text="— INVENTORY —",
            font=("Segoe UI", 10, "bold"),
            bg=const.CARD_BG,
        ).pack(pady=(6, 2))

        self._items = MenuList(
            self,
            items=data.get("items", []),
            on_select=self._handle_select,
        )
        self._items.pack(fill=tk.BOTH, expand=True, padx=4, pady=(2, 2))

        self._detail = TextDisplay(self, content=data.get("detail", ""))
        self._detail.pack(fill=tk.X, padx=4, pady=(2, 4))

    def _handle_select(self, item_id: str) -> None:
        if self._logger:
            self._logger.data("inventory_select", item_id)
        if self._on_select:
            self._on_select(item_id)

    def update_items(self, items: list) -> None:
        self._items.set_items(items)

    def update_detail(self, text: str) -> None:
        self._detail.set_content(text)