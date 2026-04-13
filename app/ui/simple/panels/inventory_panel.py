import tkinter as tk
from tkinter import ttk
import app.ui.simple.constants as const
from app.ui.simple.basic.menu_list import MenuList
from app.ui.simple.basic.text_display import TextDisplay


class InventoryPanel(ttk.Frame):
    """Inventory view: equipment summary, item list, item detail + action buttons.

    Tier 2: Use button for consumables.
    Tier 3: Equip/Unequip buttons for weapons and armor.
    Tier 4: Sell button for all items.
    """

    def __init__(self, parent, data=None, on_select=None, on_action=None,
                 logger=None, **kwargs):
        super().__init__(parent, **kwargs)
        self._logger = logger
        self._on_select = on_select
        self._on_action = on_action

        data = data or {}
        inv_data = data.get("inventory", data)

        tk.Label(
            self,
            text="— INVENTORY —",
            font=("Segoe UI", 10, "bold"),
            bg=const.CARD_BG,
        ).pack(pady=(6, 2))

        # Detail pane (equipment summary + selected item info)
        self._detail = TextDisplay(self, content=inv_data.get("detail", ""))
        self._detail.pack(fill=tk.X, padx=4, pady=(0, 2))

        # Item list
        self._items = MenuList(
            self,
            items=inv_data.get("items", []),
            on_select=self._handle_select,
        )
        self._items.pack(fill=tk.BOTH, expand=True, padx=4, pady=(2, 2))

        # Action button row (Use / Equip / Unequip / Sell)
        self._action_frame = tk.Frame(self, bg=const.CARD_BG)
        self._action_frame.pack(fill=tk.X, padx=4, pady=(2, 6))
        self._action_buttons: list = []
        self._rebuild_action_buttons(inv_data.get("item_actions", []))

    # ── callbacks ─────────────────────────────────────────────────────

    def _handle_select(self, item_id: str) -> None:
        if self._logger:
            self._logger.data("inventory_select", item_id)
        if self._on_select:
            self._on_select(item_id)

    def _handle_action(self, action_id: str) -> None:
        if self._logger:
            self._logger.data("inventory_action", action_id)
        if self._on_action:
            self._on_action(action_id)

    # ── update helpers ─────────────────────────────────────────────────

    def update_items(self, items: list) -> None:
        self._items.set_items(items)

    def update_detail(self, text: str) -> None:
        self._detail.set_content(text)

    def update_actions(self, actions: list) -> None:
        self._rebuild_action_buttons(actions)

    def _rebuild_action_buttons(self, actions: list) -> None:
        for btn in self._action_buttons:
            btn.destroy()
        self._action_buttons.clear()
        for action in actions:
            btn = tk.Button(
                self._action_frame,
                text=action.get("label", action.get("id", "?")),
                font=("Segoe UI", 9),
                bg="#3a3a4a",
                fg="#e0e0e0",
                activebackground="#555568",
                relief=tk.FLAT,
                padx=6,
                pady=3,
                command=lambda aid=action["id"]: self._handle_action(aid),
            )
            btn.pack(side=tk.LEFT, padx=(0, 4))
            self._action_buttons.append(btn)
