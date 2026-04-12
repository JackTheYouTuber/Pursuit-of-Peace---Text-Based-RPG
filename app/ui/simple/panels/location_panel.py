import tkinter as tk
from tkinter import ttk
from app.ui.simple.basic.text_display import TextDisplay
from app.ui.simple.basic.menu_list import MenuList


class LocationPanel(ttk.Frame):
    """
    Displays location description, action buttons, and — when the current
    location has a shop — a list of purchasable items.

    Shop item selection dispatches  buy_item:<item_id>  via on_action.
    """

    def __init__(self, parent, data=None, on_action=None, logger=None, columns=5, **kwargs):
        super().__init__(parent, **kwargs)
        self._logger    = logger
        self._on_action = on_action
        self._columns   = columns

        data = data or {}

        # ── Location description ───────────────────────────────────────
        self._description = TextDisplay(self, content=data.get("description", ""))
        self._description.pack(fill=tk.BOTH, expand=True, padx=4, pady=(4, 2))

        # ── Action buttons (navigation / services) ────────────────────
        self._actions = MenuList(
            self,
            items=data.get("actions", []),
            on_select=self._handle_action,
            columns=self._columns,
        )
        self._actions.pack(fill=tk.BOTH, padx=4, pady=(2, 4))

        # ── Shop section (hidden until shop items arrive) ─────────────
        self._shop_frame = ttk.LabelFrame(self, text="  Shop — click an item to buy  ")
        self._shop_list  = MenuList(
            self._shop_frame,
            items=[],
            on_select=self._handle_buy,
            columns=3,
        )
        self._shop_list.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        # Do not pack self._shop_frame yet — only shown when shop has items

    # ── Callbacks ──────────────────────────────────────────────────────

    def _handle_action(self, action_id: str) -> None:
        if self._logger:
            self._logger.data("location_action", action_id)
        if self._on_action:
            self._on_action(action_id)

    def _handle_buy(self, item_id: str) -> None:
        """Wrap item click as a buy_item prefixed action."""
        buy_action = f"buy_item:{item_id}"
        if self._logger:
            self._logger.data("shop_buy", item_id)
        if self._on_action:
            self._on_action(buy_action)

    # ── Data update ────────────────────────────────────────────────────

    def update_data(self, data: dict) -> None:
        self._description.set_content(data.get("description", ""))
        self._actions.set_items(data.get("actions", []))
        self._update_shop(data.get("shop", []))

    def _update_shop(self, shop_items: list) -> None:
        """Show or hide the shop section based on whether items are available."""
        if shop_items:
            self._shop_list.set_items(shop_items)
            if not self._shop_frame.winfo_ismapped():
                self._shop_frame.pack(fill=tk.BOTH, padx=4, pady=(0, 6))
        else:
            self._shop_list.clear()
            if self._shop_frame.winfo_ismapped():
                self._shop_frame.pack_forget()
