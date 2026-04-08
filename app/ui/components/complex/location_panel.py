# app/ui/components/complex/location_panel.py
import tkinter as tk
from ..basic.text_display import TextDisplay
from ..basic.menu_list import MenuList
from ..basic.theme import PANEL_BG


class LocationPanel(tk.Frame):
    """TextDisplay (description) + MenuList (actions) in a configurable grid."""

    BG = PANEL_BG

    def __init__(self, parent, data=None, on_action=None, logger=None, columns=5, **kwargs):
        """
        Args:
            data: dict with keys "description" (str) and "actions" (list of {id, label})
            on_action: callback(action_id: str)
            columns: number of columns in the action button grid (default 5)
        """
        bg = kwargs.pop('bg', self.BG)
        super().__init__(parent, bg=bg, **kwargs)
        self._logger = logger
        self._on_action = on_action
        self._columns = columns

        data = data or {}

        # Description area (scrollable text)
        self._description = TextDisplay(self, content=data.get("description", ""))
        self._description.pack(fill=tk.BOTH, expand=True, padx=4, pady=(4, 2))

        # Action buttons in a grid
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
        """Refresh description text and action buttons."""
        self._description.set_content(data.get("description", ""))
        self._actions.set_items(data.get("actions", []))