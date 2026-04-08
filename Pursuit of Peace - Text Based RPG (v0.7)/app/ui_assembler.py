import json
import os
import tkinter as tk
from typing import Dict, Any, Callable, Optional

# Import all component classes
from app.ui.components.basic.text_display import TextDisplay
from app.ui.components.basic.menu_list import MenuList
from app.ui.components.basic.stat_bar import StatBar
from app.ui.components.complex.location_panel import LocationPanel
from app.ui.components.complex.combat_panel import CombatPanel
from app.ui.components.complex.inventory_panel import InventoryPanel
from app.ui.components.complex.lore_panel import LorePanel

class UIAssembler:
    """
    Data‑driven UI builder for Pursuit of Peace.
    Reads layout JSON files and dynamically constructs tkinter widgets.
    Supports caching, data binding, and themed styling.
    """

    # Registry of component types -> class
    _COMPONENT_REGISTRY = {
        "TextDisplay": TextDisplay,
        "MenuList": MenuList,
        "StatBar": StatBar,
        "LocationPanel": LocationPanel,
        "CombatPanel": CombatPanel,
        "InventoryPanel": InventoryPanel,
        "LorePanel": LorePanel,
        # Basic containers
        "Frame": tk.Frame,
    }

    def __init__(
        self,
        root: tk.Widget,
        callbacks: Dict[str, Callable],
        theme_path: str = "data/ui/themes.json",
        layouts_dir: str = "data/ui/layouts",
        logger=None,
    ):
        """
        Args:
            root: The parent widget (usually the content frame).
            callbacks: Mapping from logical names (e.g. "location_action") to actual handler methods.
            theme_path: Path to JSON theme file.
            layouts_dir: Directory containing view layout JSON files.
            logger: Optional GameLogger instance.
        """
        self._root = root
        self._callbacks = callbacks
        self._layouts_dir = layouts_dir
        self._logger = logger
        self._theme = self._load_theme(theme_path)

        # Cached views: view_name -> {"frame": widget, "components": {name: info}}
        self._views: Dict[str, Dict] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_or_build_view(self, view_name: str, state: Dict) -> tk.Widget:
        """
        Return the top-level widget for the requested view.
        Builds and caches it if not already present.
        """
        if view_name in self._views:
            return self._views[view_name]["frame"]

        layout = self._load_layout(view_name)
        if not layout:
            # Fallback: create an empty error frame
            frame = tk.Frame(self._root, bg=self._theme["global"]["bg"])
            tk.Label(frame, text=f"View '{view_name}' not found", fg="red").pack()
            self._views[view_name] = {"frame": frame, "components": {}}
            return frame

        # Build the component tree
        frame, components = self._build_component(
            layout, parent=self._root, state=state
        )
        # Grid it in the root (row=0, col=0, sticky)
        frame.grid(row=0, column=0, sticky="nsew")
        self._views[view_name] = {"frame": frame, "components": components}
        return frame

    def refresh_view(self, view_name: str, state: Dict):
        """Update all data-bound components in the view."""
        view_info = self._views.get(view_name)
        if not view_info:
            if self._logger:
                self._logger.warn(f"refresh_view called for unknown view: {view_name}")
            return

        components = view_info["components"]
        for comp_name, info in components.items():
            widget = info["widget"]
            bindings = info.get("bindings", {})
            if not bindings:
                continue

            # Update the component based on its type and bindings
            if isinstance(widget, TextDisplay):
                source = bindings.get("data_source")
                if source:
                    text = self._get_nested(state, source, "")
                    widget.set_content(text)

            elif isinstance(widget, MenuList):
                source = bindings.get("items_source")
                if source:
                    items = self._get_nested(state, source, [])
                    widget.set_items(items)

            elif isinstance(widget, StatBar):
                label_source = bindings.get("label_source")
                value_source = bindings.get("value_source")
                if label_source:
                    label = self._get_nested(state, label_source, "")
                    widget.set_label(label)
                if value_source:
                    value = self._get_nested(state, value_source, 0)
                    widget.set_value(value)

            elif isinstance(widget, LocationPanel):
                # LocationPanel expects update_data({"description": ..., "actions": ...})
                data = {}
                for key, src in bindings.get("data_sources", {}).items():
                    data[key] = self._get_nested(state, src, "")
                widget.update_data(data)

            elif isinstance(widget, CombatPanel):
                # Update all combat panel fields
                self._update_combat_panel(widget, state, bindings)

            elif isinstance(widget, InventoryPanel):
                items_source = bindings.get("items_source")
                detail_source = bindings.get("detail_source")
                if items_source:
                    items = self._get_nested(state, items_source, [])
                    widget.update_items(items)
                if detail_source:
                    detail = self._get_nested(state, detail_source, "")
                    widget.update_detail(detail)

            elif isinstance(widget, LorePanel):
                entries_source = bindings.get("entries_source")
                if entries_source:
                    entries = self._get_nested(state, entries_source, [])
                    widget.update_entries(entries)

    def destroy_view(self, view_name: str):
        """Remove the view and free references."""
        view_info = self._views.pop(view_name, None)
        if view_info:
            view_info["frame"].destroy()

    # ------------------------------------------------------------------
    # Internal builders
    # ------------------------------------------------------------------

    def _load_theme(self, path: str) -> Dict:
        """Load theme JSON, return dict with defaults."""
        default = {"global": {"bg": "#0d1b2a", "fg": "#d4c9a8"}}
        if not os.path.exists(path):
            return default
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            if self._logger:
                self._logger.error(f"Failed to load theme: {e}")
            return default

    def _load_layout(self, view_name: str) -> Optional[Dict]:
        """Load layout JSON for a view, return None on failure."""
        path = os.path.join(self._layouts_dir, f"{view_name}.json")
        if not os.path.exists(path):
            if self._logger:
                self._logger.warn(f"Layout not found: {path}")
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            if self._logger:
                self._logger.error(f"Failed to load layout {view_name}: {e}")
            return None

    def _build_component(
        self, desc: Dict, parent: tk.Widget, state: Dict
    ) -> (tk.Widget, Dict):
        """
        Recursively build a component tree.
        Returns (top_widget, components_dict) where components_dict maps
        component names to {widget, bindings}.
        """
        comp_type = desc.get("type")
        if not comp_type:
            raise ValueError("Component missing 'type'")

        comp_class = self._COMPONENT_REGISTRY.get(comp_type)
        if not comp_class:
            if self._logger:
                self._logger.error(f"Unknown component type: {comp_type}")
            # Fallback to Frame
            comp_class = tk.Frame

        # Apply theme defaults
        theme = self._theme.get(comp_type, {})
        global_theme = self._theme.get("global", {})

        # Prepare kwargs for the widget
        kwargs = {}
        if comp_type == "TextDisplay":
            kwargs["bg"] = theme.get("bg", global_theme.get("bg", "#1a1a2e"))
            kwargs["fg"] = theme.get("fg", global_theme.get("fg", "#d4c9a8"))
            kwargs["font"] = (global_theme.get("font_family", "Courier"),
                              global_theme.get("font_size", 11))
        elif comp_type == "MenuList":
            kwargs["bg"] = theme.get("bg", global_theme.get("bg", "#16213e"))
            # MenuList uses its own defaults, we pass items later
        elif comp_type == "StatBar":
            kwargs["bg"] = theme.get("bg", global_theme.get("bg", "#16213e"))
            # label_fg, value_fg handled inside StatBar defaults
        elif comp_type in ("LocationPanel", "CombatPanel", "InventoryPanel", "LorePanel"):
            kwargs["bg"] = theme.get("bg", global_theme.get("bg", "#16213e"))
            kwargs["logger"] = self._logger
        else:
            kwargs["bg"] = theme.get("bg", global_theme.get("bg", "#0d1b2a"))

        # Create the widget
        widget = comp_class(parent, **kwargs)

        # Store bindings and callbacks
        bindings = {}
        components = {}

        # Handle data sources
        data_desc = desc.get("data", {})
        if comp_type in ("TextDisplay",):
            src = data_desc.get("data_source")
            if src:
                bindings["data_source"] = src
                # Set initial value
                text = self._get_nested(state, src, "")
                widget.set_content(text)

        elif comp_type in ("MenuList",):
            src = data_desc.get("items_source")
            if src:
                bindings["items_source"] = src
                items = self._get_nested(state, src, [])
                widget.set_items(items)
            # Set callback
            on_select = desc.get("on_select")
            if on_select:
                callback = self._callbacks.get(on_select)
                if callback:
                    # MenuList expects on_select callback with item_id
                    widget._on_select = callback  # replace internal handler
                    # Better: override the _handle_select method? We'll assign to a new attribute
                    # But MenuList uses self._on_select. We'll replace it.
                    widget._on_select = callback

        elif comp_type in ("StatBar",):
            label_src = data_desc.get("label_source")
            value_src = data_desc.get("value_source")
            if label_src:
                bindings["label_source"] = label_src
                label = self._get_nested(state, label_src, "")
                widget.set_label(label)
            if value_src:
                bindings["value_source"] = value_src
                value = self._get_nested(state, value_src, 0)
                widget.set_value(value)

        elif comp_type == "LocationPanel":
            # data: {description_source, actions_source}
            data_sources = {}
            for key, src in data_desc.items():
                if key.endswith("_source"):
                    field = key.replace("_source", "")
                    data_sources[field] = src
            if data_sources:
                bindings["data_sources"] = data_sources
                # Build initial data dict
                initial_data = {}
                for field, src in data_sources.items():
                    initial_data[field] = self._get_nested(state, src, "")
                widget.update_data(initial_data)
            # Set callback
            on_action = desc.get("on_action")
            if on_action:
                callback = self._callbacks.get(on_action)
                if callback:
                    widget._on_action = callback

        elif comp_type == "CombatPanel":
            # Store all sources
            for src_name in ["log_source", "enemy_name_source", "enemy_hp_source", "actions_source"]:
                if src_name in data_desc:
                    bindings[src_name] = data_desc[src_name]
            # Initial update
            self._update_combat_panel(widget, state, bindings)
            # Set callback
            on_action = desc.get("on_action")
            if on_action:
                callback = self._callbacks.get(on_action)
                if callback:
                    widget._on_action = callback

        elif comp_type == "InventoryPanel":
            items_src = data_desc.get("items_source")
            detail_src = data_desc.get("detail_source")
            if items_src:
                bindings["items_source"] = items_src
                items = self._get_nested(state, items_src, [])
                widget.update_items(items)
            if detail_src:
                bindings["detail_source"] = detail_src
                detail = self._get_nested(state, detail_src, "")
                widget.update_detail(detail)
            # Set callback
            on_select = desc.get("on_select")
            if on_select:
                callback = self._callbacks.get(on_select)
                if callback:
                    widget._on_select = callback

        elif comp_type == "LorePanel":
            entries_src = data_desc.get("entries_source")
            if entries_src:
                bindings["entries_source"] = entries_src
                entries = self._get_nested(state, entries_src, [])
                widget.update_entries(entries)

        # Store this component if it has a name
        comp_name = desc.get("name")
        if comp_name:
            components[comp_name] = {"widget": widget, "bindings": bindings}

        # Handle children (for containers like Frame)
        children_desc = desc.get("children", [])
        if children_desc:
            # Determine layout direction
            layout_dir = desc.get("layout", "vertical")  # vertical or horizontal
            for child_desc in children_desc:
                child_widget, child_comps = self._build_component(child_desc, widget, state)
                # Pack the child
                if layout_dir == "vertical":
                    child_widget.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)
                else:  # horizontal
                    child_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=4)
                components.update(child_comps)

        return widget, components

    def _update_combat_panel(self, panel: CombatPanel, state: Dict, bindings: Dict):
        """Update combat panel with fresh log, enemy stats, and player HP."""
        log_source = bindings.get("log_source")
        if log_source:
            log_text = self._get_nested(state, log_source, "")
            panel.set_log(log_text)

        enemy_name_source = bindings.get("enemy_name_source")
        enemy_hp_source = bindings.get("enemy_hp_source")
        if enemy_name_source and enemy_hp_source:
            name = self._get_nested(state, enemy_name_source, "Enemy")
            hp = self._get_nested(state, enemy_hp_source, 0)
            panel.update_enemy_hp(name, hp)

        # v0.7 — update player HP bar after enemy counter-attack
        player_hp = self._get_nested(state, "combat.player_hp", None)
        if player_hp is not None and hasattr(panel, "update_player_hp"):
            panel.update_player_hp(player_hp)

        actions_source = bindings.get("actions_source")
        if actions_source:
            actions = self._get_nested(state, actions_source, [])
            panel.set_actions(actions)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get_nested(data: Dict, path: str, default=None):
        """Retrieve a value from a nested dict using dot notation."""
        if not path:
            return default
        keys = path.split(".")
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
            if value is None:
                return default
        return value