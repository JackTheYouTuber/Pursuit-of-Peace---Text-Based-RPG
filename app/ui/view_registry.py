import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional

from app.ui.layout_loader import load_layout
from app.ui.component_builder import ComponentBuilder


class ViewRegistry:
    def __init__(self, root: tk.Widget, callbacks: Dict, theme: Dict, layouts_dir: str, logger=None):
        self._root = root
        self._builder = ComponentBuilder(theme, callbacks, logger)
        self._layouts_dir = layouts_dir
        self._logger = logger
        self._views: Dict[str, Dict] = {}  # name -> {"frame": widget, "components": {comp_name: {widget, bindings}}}

    def get_or_build(self, view_name: str, state: Dict) -> tk.Widget:
        if view_name in self._views:
            return self._views[view_name]["frame"]

        layout = load_layout(view_name, self._layouts_dir, self._logger)
        if not layout:
            frame = ttk.Frame(self._root)
            ttk.Label(frame, text=f"View '{view_name}' not found", foreground="red").pack()
            self._views[view_name] = {"frame": frame, "components": {}}
            return frame

        frame, components = self._builder.build(layout, self._root, state)
        frame.grid(row=0, column=0, sticky="nsew")
        self._views[view_name] = {"frame": frame, "components": components}
        return frame

    def refresh(self, view_name: str, state: Dict):
        view_info = self._views.get(view_name)
        if not view_info:
            if self._logger:
                self._logger.warn(f"refresh_view called for unknown view: {view_name}")
            return

        for comp_name, info in view_info["components"].items():
            widget = info["widget"]
            bindings = info.get("bindings", {})
            if not bindings:
                continue
            comp_type = self._get_component_type(widget)
            if comp_type:
                self._builder.refresh_component(widget, comp_type, state, bindings)

    def destroy(self, view_name: str):
        view_info = self._views.pop(view_name, None)
        if view_info:
            view_info["frame"].destroy()

    @staticmethod
    def _get_component_type(widget) -> Optional[str]:
        classname = widget.__class__.__name__
        mapping = {
            "TextDisplay": "TextDisplay",
            "MenuList": "MenuList",
            "StatBar": "StatBar",
            "LocationPanel": "LocationPanel",
            "CombatPanel": "CombatPanel",
            "InventoryPanel": "InventoryPanel",
            "LorePanel": "LorePanel",
        }
        return mapping.get(classname)