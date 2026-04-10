import tkinter as tk
from tkinter import ttk
from app.ui.simple.style_manager import StyleManager

from app.ui.simple.basic.text_display import TextDisplay
from app.ui.simple.basic.menu_list import MenuList


class LocationPanel(ttk.Frame):
    def __init__(self, parent, data=None, on_action=None, logger=None, columns=5, **kwargs):
        super().__init__(parent, **kwargs)
        self._logger = logger
        self._on_action = on_action
        self._columns = columns

        data = data or {}

        self._description = TextDisplay(self, content=data.get("description", ""))
        self._description.pack(fill=tk.BOTH, expand=True, padx=4, pady=(4, 2))

        self._actions = MenuList(
            self,
            items=data.get("actions", []),
            on_select=self._handle_action,
            columns=self._columns,
        )
        self._actions.pack(fill=tk.BOTH, expand=True, padx=4, pady=(2, 4))

    def _handle_action(self, action_id: str) -> None:
        if self._logger:
            self._logger.data("location_action", action_id)
        if self._on_action:
            self._on_action(action_id)

    def update_data(self, data: dict) -> None:
        self._description.set_content(data.get("description", ""))
        self._actions.set_items(data.get("actions", []))