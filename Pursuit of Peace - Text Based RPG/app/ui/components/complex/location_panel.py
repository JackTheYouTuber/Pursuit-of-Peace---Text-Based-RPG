import tkinter as tk

from app.ui.components.basic.text_display import TextDisplay
from app.ui.components.basic.menu_list import MenuList


class LocationPanel(tk.Frame):
    """TextDisplay (description) + MenuList (actions). Layer 2."""

    BG = "#16213e"

    def __init__(self, parent, data=None, on_action=None, logger=None, **kwargs):
        """
        data — {"description": str, "actions": [{"id": str, "label": str}]}
        on_action — callback(action_id: str)
        """
        bg = kwargs.pop('bg', self.BG)
        super().__init__(parent, bg=bg, **kwargs)
        self._logger = logger
        self._on_action = on_action

        data = data or {}

        self._description = TextDisplay(self, content=data.get("description", ""))
        self._description.pack(fill=tk.BOTH, expand=True, padx=4, pady=(4, 2))

        self._actions = MenuList(
            self,
            items=data.get("actions", []),
            on_select=self._handle_action,
        )
        self._actions.pack(fill=tk.X, padx=4, pady=(2, 4))

    def _handle_action(self, action_id):
        if self._logger:
            self._logger.data("location_action", action_id)
        if self._on_action:
            self._on_action(action_id)

    def update_data(self, data):
        self._description.set_content(data.get("description", ""))
        self._actions.set_items(data.get("actions", []))
