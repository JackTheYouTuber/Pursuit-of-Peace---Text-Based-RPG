import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Callable, Tuple

from app.ui.component_registry import get_component_class
from app.ui.data_binder import DataBinder
from app.ui.style_manager import StyleManager

class ComponentBuilder:
    def __init__(self, theme: Dict, callbacks: Dict[str, Callable], logger=None):
        self._theme = theme
        self._callbacks = callbacks
        self._logger = logger

    def build(self, desc: Dict, parent: tk.Widget, state: Dict) -> Tuple[tk.Widget, Dict]:
        comp_type = desc.get("type")
        if not comp_type:
            raise ValueError("Component missing 'type'")

        comp_class = get_component_class(comp_type)
        if not comp_class:
            if self._logger:
                self._logger.error(f"Unknown component type: {comp_type}")
            comp_class = ttk.Frame

        # Apply theme lookups (fallback)
        theme = self._theme.get(comp_type, {})
        global_theme = self._theme.get("global", {})

        kwargs = {}
        # StyleManager already applied to root; we only pass style name if needed
        if comp_type in ("LocationPanel", "CombatPanel", "InventoryPanel", "LorePanel"):
            kwargs["logger"] = self._logger

        widget = comp_class(parent, **kwargs)
        bindings = {}
        components = {}

        # Bind data and callbacks
        DataBinder.bind_initial_data(widget, comp_type, desc, state, bindings)
        DataBinder.bind_callbacks(widget, comp_type, desc, self._callbacks)

        # Store component if named
        comp_name = desc.get("name")
        if comp_name:
            components[comp_name] = {"widget": widget, "bindings": bindings}

        # Handle children
        children = desc.get("children", [])
        if children:
            layout_dir = desc.get("layout", "vertical")
            for child_desc in children:
                child_widget, child_comps = self.build(child_desc, widget, state)
                if layout_dir == "vertical":
                    child_widget.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)
                else:
                    child_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=4)
                components.update(child_comps)

        return widget, components

    def refresh_component(self, widget, comp_type: str, state: Dict, bindings: Dict):
        DataBinder.refresh_component(widget, comp_type, state, bindings)