"""Data binding and refresh logic for UI components."""
from typing import Dict, Any

class DataBinder:
    @staticmethod
    def get_nested(data: Dict, path: str, default=None):
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

    @classmethod
    def bind_initial_data(cls, widget, comp_type: str, desc: Dict, state: Dict, bindings: Dict):
        data_desc = desc.get("data", {})
        if comp_type == "TextDisplay":
            src = data_desc.get("data_source")
            if src:
                bindings["data_source"] = src
                text = cls.get_nested(state, src, "")
                widget.set_content(text)

        elif comp_type == "MenuList":
            src = data_desc.get("items_source")
            if src:
                bindings["items_source"] = src
                items = cls.get_nested(state, src, [])
                widget.set_items(items)

        elif comp_type == "StatBar":
            label_src = data_desc.get("label_source")
            value_src = data_desc.get("value_source")
            if label_src:
                bindings["label_source"] = label_src
                label = cls.get_nested(state, label_src, "")
                widget.set_label(label)
            if value_src:
                bindings["value_source"] = value_src
                value = cls.get_nested(state, value_src, 0)
                widget.set_value(value)

        elif comp_type == "LocationPanel":
            data_sources = {}
            for key, src in data_desc.items():
                if key.endswith("_source"):
                    field = key.replace("_source", "")
                    data_sources[field] = src
            if data_sources:
                bindings["data_sources"] = data_sources
                initial_data = {field: cls.get_nested(state, src, "") for field, src in data_sources.items()}
                widget.update_data(initial_data)

        elif comp_type == "CombatPanel":
            for src_name in ["log_source", "enemy_name_source", "enemy_hp_source", "actions_source"]:
                if src_name in data_desc:
                    bindings[src_name] = data_desc[src_name]
            cls._update_combat_panel(widget, state, bindings)

        elif comp_type == "InventoryPanel":
            items_src = data_desc.get("items_source")
            detail_src = data_desc.get("detail_source")
            if items_src:
                bindings["items_source"] = items_src
                items = cls.get_nested(state, items_src, [])
                widget.update_items(items)
            if detail_src:
                bindings["detail_source"] = detail_src
                detail = cls.get_nested(state, detail_src, "")
                widget.update_detail(detail)

        elif comp_type == "LorePanel":
            entries_src = data_desc.get("entries_source")
            if entries_src:
                bindings["entries_source"] = entries_src
                entries = cls.get_nested(state, entries_src, [])
                widget.update_entries(entries)

    @classmethod
    def bind_callbacks(cls, widget, comp_type: str, desc: Dict, callbacks: Dict):
        if comp_type in ("MenuList", "InventoryPanel"):
            on_select = desc.get("on_select")
            if on_select and on_select in callbacks:
                widget._on_select = callbacks[on_select]
        elif comp_type in ("LocationPanel", "CombatPanel"):
            on_action = desc.get("on_action")
            if on_action and on_action in callbacks:
                widget._on_action = callbacks[on_action]

    @classmethod
    def refresh_component(cls, widget, comp_type: str, state: Dict, bindings: Dict):
        if comp_type == "TextDisplay":
            src = bindings.get("data_source")
            if src:
                widget.set_content(cls.get_nested(state, src, ""))
        elif comp_type == "MenuList":
            src = bindings.get("items_source")
            if src:
                widget.set_items(cls.get_nested(state, src, []))
        elif comp_type == "StatBar":
            label_src = bindings.get("label_source")
            value_src = bindings.get("value_source")
            if label_src:
                widget.set_label(cls.get_nested(state, label_src, ""))
            if value_src:
                widget.set_value(cls.get_nested(state, value_src, 0))
        elif comp_type == "LocationPanel":
            data_sources = bindings.get("data_sources", {})
            if data_sources:
                data = {field: cls.get_nested(state, src, "") for field, src in data_sources.items()}
                widget.update_data(data)
        elif comp_type == "CombatPanel":
            cls._update_combat_panel(widget, state, bindings)
        elif comp_type == "InventoryPanel":
            items_src = bindings.get("items_source")
            detail_src = bindings.get("detail_source")
            if items_src:
                widget.update_items(cls.get_nested(state, items_src, []))
            if detail_src:
                widget.update_detail(cls.get_nested(state, detail_src, ""))
        elif comp_type == "LorePanel":
            entries_src = bindings.get("entries_source")
            if entries_src:
                widget.update_entries(cls.get_nested(state, entries_src, []))

    @staticmethod
    def _update_combat_panel(panel, state, bindings):
        log_source = bindings.get("log_source")
        if log_source:
            log_text = DataBinder.get_nested(state, log_source, "")
            panel.set_log(log_text)

        enemy_name_source = bindings.get("enemy_name_source")
        enemy_hp_source = bindings.get("enemy_hp_source")
        if enemy_name_source and enemy_hp_source:
            name = DataBinder.get_nested(state, enemy_name_source, "Enemy")
            hp = DataBinder.get_nested(state, enemy_hp_source, 0)
            panel.update_enemy_hp(name, hp)

        player_hp = DataBinder.get_nested(state, "combat.player_hp", None)
        if player_hp is not None and hasattr(panel, "update_player_hp"):
            panel.update_player_hp(player_hp)

        actions_source = bindings.get("actions_source")
        if actions_source:
            actions = DataBinder.get_nested(state, actions_source, [])
            panel.set_actions(actions)