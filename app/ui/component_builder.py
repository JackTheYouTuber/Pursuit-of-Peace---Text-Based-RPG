import tkinter as tk
from typing import Dict, Any, Callable, Tuple, Optional

from app.ui.components.basic.text_display import TextDisplay
from app.ui.components.basic.menu_list import MenuList
from app.ui.components.basic.stat_bar import StatBar
from app.ui.components.complex.location_panel import LocationPanel
from app.ui.components.complex.combat_panel import CombatPanel
from app.ui.components.complex.inventory_panel import InventoryPanel
from app.ui.components.complex.lore_panel import LorePanel

class ComponentBuilder:
    _REGISTRY = {
        "TextDisplay": TextDisplay,
        "MenuList": MenuList,
        "StatBar": StatBar,
        "LocationPanel": LocationPanel,
        "CombatPanel": CombatPanel,
        "InventoryPanel": InventoryPanel,
        "LorePanel": LorePanel,
        "Frame": tk.Frame,
    }

    def __init__(self, theme: Dict, callbacks: Dict[str, Callable], logger=None):
        self._theme = theme
        self._callbacks = callbacks
        self._logger = logger

    def build(self, desc: Dict, parent: tk.Widget, state: Dict) -> Tuple[tk.Widget, Dict]:
        """
        Recursively build a component tree.
        Returns (top_widget, components_dict) where components_dict maps
        component names to {widget, bindings}.
        """
        comp_type = desc.get("type")
        if not comp_type:
            raise ValueError("Component missing 'type'")

        comp_class = self._REGISTRY.get(comp_type)
        if not comp_class:
            if self._logger:
                self._logger.error(f"Unknown component type: {comp_type}")
            comp_class = tk.Frame

        # Theme lookups
        theme = self._theme.get(comp_type, {})
        global_theme = self._theme.get("global", {})

        # Prepare kwargs
        kwargs = {}
        if comp_type == "TextDisplay":
            kwargs["bg"] = theme.get("bg", global_theme.get("bg", "#1a1a2e"))
            kwargs["fg"] = theme.get("fg", global_theme.get("fg", "#d4c9a8"))
            kwargs["font"] = (global_theme.get("font_family", "Courier"),
                              global_theme.get("font_size", 11))
        elif comp_type == "MenuList":
            kwargs["bg"] = theme.get("bg", global_theme.get("bg", "#16213e"))
            # columns may be passed in desc
            if "columns" in desc:
                kwargs["columns"] = desc["columns"]
        elif comp_type == "StatBar":
            kwargs["bg"] = theme.get("bg", global_theme.get("bg", "#16213e"))
        elif comp_type in ("LocationPanel", "CombatPanel", "InventoryPanel", "LorePanel"):
            kwargs["bg"] = theme.get("bg", global_theme.get("bg", "#16213e"))
            kwargs["logger"] = self._logger
        else:
            kwargs["bg"] = theme.get("bg", global_theme.get("bg", "#0d1b2a"))

        widget = comp_class(parent, **kwargs)
        bindings = {}
        components = {}

        # Handle data sources and callbacks
        self._bind_data(widget, comp_type, desc, state, bindings)
        self._bind_callbacks(widget, comp_type, desc)

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

    def _bind_data(self, widget, comp_type, desc, state, bindings):
        data_desc = desc.get("data", {})
        if comp_type == "TextDisplay":
            src = data_desc.get("data_source")
            if src:
                bindings["data_source"] = src
                text = self._get_nested(state, src, "")
                widget.set_content(text)

        elif comp_type == "MenuList":
            src = data_desc.get("items_source")
            if src:
                bindings["items_source"] = src
                items = self._get_nested(state, src, [])
                widget.set_items(items)

        elif comp_type == "StatBar":
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
            data_sources = {}
            for key, src in data_desc.items():
                if key.endswith("_source"):
                    field = key.replace("_source", "")
                    data_sources[field] = src
            if data_sources:
                bindings["data_sources"] = data_sources
                initial_data = {}
                for field, src in data_sources.items():
                    initial_data[field] = self._get_nested(state, src, "")
                widget.update_data(initial_data)

        elif comp_type == "CombatPanel":
            for src_name in ["log_source", "enemy_name_source", "enemy_hp_source", "actions_source"]:
                if src_name in data_desc:
                    bindings[src_name] = data_desc[src_name]
            self._update_combat_panel(widget, state, bindings)

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

        elif comp_type == "LorePanel":
            entries_src = data_desc.get("entries_source")
            if entries_src:
                bindings["entries_source"] = entries_src
                entries = self._get_nested(state, entries_src, [])
                widget.update_entries(entries)

    def _bind_callbacks(self, widget, comp_type, desc):
        if comp_type in ("MenuList", "InventoryPanel"):
            on_select = desc.get("on_select")
            if on_select:
                callback = self._callbacks.get(on_select)
                if callback:
                    widget._on_select = callback
        elif comp_type in ("LocationPanel", "CombatPanel"):
            on_action = desc.get("on_action")
            if on_action:
                callback = self._callbacks.get(on_action)
                if callback:
                    widget._on_action = callback

    def _update_combat_panel(self, panel, state, bindings):
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

        player_hp = self._get_nested(state, "combat.player_hp", None)
        if player_hp is not None and hasattr(panel, "update_player_hp"):
            panel.update_player_hp(player_hp)

        actions_source = bindings.get("actions_source")
        if actions_source:
            actions = self._get_nested(state, actions_source, [])
            panel.set_actions(actions)

    @staticmethod
    def _get_nested(data: Dict, path: str, default=None):
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

    def refresh_component(self, widget, comp_type, state, bindings):
        """Update a single component with fresh state."""
        if comp_type == "TextDisplay":
            src = bindings.get("data_source")
            if src:
                text = self._get_nested(state, src, "")
                widget.set_content(text)
        elif comp_type == "MenuList":
            src = bindings.get("items_source")
            if src:
                items = self._get_nested(state, src, [])
                widget.set_items(items)
        elif comp_type == "StatBar":
            label_src = bindings.get("label_source")
            value_src = bindings.get("value_source")
            if label_src:
                label = self._get_nested(state, label_src, "")
                widget.set_label(label)
            if value_src:
                value = self._get_nested(state, value_src, 0)
                widget.set_value(value)
        elif comp_type == "LocationPanel":
            data_sources = bindings.get("data_sources", {})
            if data_sources:
                data = {}
                for field, src in data_sources.items():
                    data[field] = self._get_nested(state, src, "")
                widget.update_data(data)
        elif comp_type == "CombatPanel":
            self._update_combat_panel(widget, state, bindings)
        elif comp_type == "InventoryPanel":
            items_src = bindings.get("items_source")
            detail_src = bindings.get("detail_source")
            if items_src:
                items = self._get_nested(state, items_src, [])
                widget.update_items(items)
            if detail_src:
                detail = self._get_nested(state, detail_src, "")
                widget.update_detail(detail)
        elif comp_type == "LorePanel":
            entries_src = bindings.get("entries_source")
            if entries_src:
                entries = self._get_nested(state, entries_src, [])
                widget.update_entries(entries)