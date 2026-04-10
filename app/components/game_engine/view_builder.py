# app/components/game_engine/view_builder.py
from typing import Dict, List, Optional


class ViewBuilder:
    """Construct UI state dictionaries for different views."""

    def __init__(self, data_loader, location_manager, dungeon_manager, logger=None):
        self._loader = data_loader
        self._location_mgr = location_manager
        self._dungeon_mgr = dungeon_manager
        self._logger = logger

    def build_city_state(self, player_state: Dict) -> Dict:
        loc_id = player_state.get("current_location_id", "city_entrance")
        return {
            "location": {
                "description": self._get_location_description(loc_id),
                "actions": self._build_action_list(loc_id),
            }
        }

    def build_dungeon_state(self, dungeon_state: Optional[Dict]) -> Dict:
        if not dungeon_state:
            return {"location": {"description": "", "actions": []}}
        room = self._dungeon_mgr.get_current_room(dungeon_state)
        if not room:
            return {"location": {"description": "", "actions": []}}
        lore_text = self._dungeon_mgr.get_room_lore_text(room)
        depth = room.get("depth", 1)
        idx = dungeon_state.get("current_index", 0) + 1
        total = dungeon_state.get("total_rooms", 1)
        description = f"[ DUNGEON  Room {idx}/{total}  Depth {depth} ]\n\n{lore_text}"
        actions = self._build_dungeon_actions(room, dungeon_state, idx, total)
        return {"location": {"description": description, "actions": actions}}

    def build_inventory_state(self, player_state: Dict, detail: str = "") -> Dict:
        items = []
        for item_id in player_state.get("inventory", []):
            try:
                item = self._loader.get_item(item_id)
                items.append({"id": item_id, "label": item.get("name", item_id)})
            except ValueError:
                items.append({"id": item_id, "label": item_id})

        # Equipment slots summary with durability bar
        equipped_lines = []
        ew = player_state.get("equipped_weapon")
        ea = player_state.get("equipped_armor")
        if ew:
            item = ew.get("item", {})
            cur = ew.get("current_durability", 0)
            mx = ew.get("max_durability", 1)
            dmg = item.get("stat_bonus", {}).get("damage", 0)
            bar = self._durability_bar(cur, mx)
            equipped_lines.append(f"⚔ {item.get('name','?')}  +{dmg} dmg\n  {bar} {cur}/{mx}")
        else:
            equipped_lines.append("⚔ Weapon: — (unarmed)")
        if ea:
            item = ea.get("item", {})
            cur = ea.get("current_durability", 0)
            mx = ea.get("max_durability", 1)
            dfn = item.get("stat_bonus", {}).get("defense", 0)
            bar = self._durability_bar(cur, mx)
            equipped_lines.append(f"🛡 {item.get('name','?')}  +{dfn} def\n  {bar} {cur}/{mx}")
        else:
            equipped_lines.append("🛡 Armor:  — (no armor)")

        equipment_actions = []
        if ew:
            equipment_actions.append({
                "id": "unequip:equipped_weapon",
                "label": f"Unequip {ew.get('item', {}).get('name', 'weapon')}"
            })
        if ea:
            equipment_actions.append({
                "id": "unequip:equipped_armor",
                "label": f"Unequip {ea.get('item', {}).get('name', 'armor')}"
            })

        return {
            "inventory": {
                "items": items,
                "detail": "\n".join(equipped_lines) + ("\n\n" + detail if detail else ""),
                "item_actions": equipment_actions,
            }
        }

    @staticmethod
    def _durability_bar(current: int, maximum: int, width: int = 10) -> str:
        """Return a text durability bar like [████░░░░░░] 4/10."""
        if maximum <= 0:
            return "[" + "░" * width + "]"
        filled = round(width * current / maximum)
        filled = max(0, min(width, filled))
        empty = width - filled
        pct = current / maximum
        if pct > 0.5:
            char = "█"
        elif pct > 0.2:
            char = "▓"
        else:
            char = "▒"
        return "[" + char * filled + "░" * empty + "]"

    def build_lore_state(self) -> Dict:
        return {"lore": {"entries": self._loader.get_lore("global")}}

    def build_combat_state(self, combat_state: Dict,
                           player_state: Optional[Dict] = None) -> Dict:
        enemy = combat_state["enemy"]

        # Build action list including consumables if player has any
        actions = [
            {"id": "attack", "label": "⚔ Attack"},
            {"id": "flee",   "label": "🏃 Flee"},
        ]
        if player_state:
            for item_id in player_state.get("inventory", []):
                try:
                    item = self._loader.get_item(item_id)
                    if item.get("type") == "consumable":
                        actions.append({
                            "id": f"use_item:{item_id}",
                            "label": f"Use: {item.get('name', item_id)}"
                        })
                except ValueError:
                    pass

        # Equipment summary for display
        equip_summary = ""
        if player_state:
            ew = player_state.get("equipped_weapon")
            ea = player_state.get("equipped_armor")
            parts = []
            if ew:
                dmg = ew.get("item", {}).get("stat_bonus", {}).get("damage", 0)
                dur = ew.get("current_durability", 0)
                parts.append(f"⚔ +{dmg}dmg ({dur} dur)")
            if ea:
                dfn = ea.get("item", {}).get("stat_bonus", {}).get("defense", 0)
                dur = ea.get("current_durability", 0)
                parts.append(f"🛡 +{dfn}def ({dur} dur)")
            if parts:
                equip_summary = "  ".join(parts)

        log = combat_state.get("log_text", "")
        if equip_summary:
            log = equip_summary + "\n" + "─" * 30 + "\n" + log

        return {
            "combat": {
                "log": log,
                "enemy_name": enemy.get("name", "Enemy"),
                "enemy_hp": combat_state.get("enemy_current_hp", 0),
                "player_hp": combat_state.get("player_current_hp", 0),
                "player_max_hp": combat_state.get("player_max_hp", 20),
                "actions": actions,
            }
        }

    def build_player_panel_data(self, player_state: Dict) -> Dict:
        from app.components.game_engine.buff_system import BuffSystem
        buff_sys = BuffSystem()
        max_hp_bonus = buff_sys.get_max_hp_bonus(player_state)
        buff_summary = buff_sys.get_buff_summary(player_state)

        ew = player_state.get("equipped_weapon")
        ea = player_state.get("equipped_armor")
        equip_parts = []
        if ew:
            dmg = ew.get("item", {}).get("stat_bonus", {}).get("damage", 0)
            dur = ew.get("current_durability", 0)
            max_dur = ew.get("max_durability", 1)
            equip_parts.append(f"+{dmg}⚔ [{dur}/{max_dur}]")
        if ea:
            dfn = ea.get("item", {}).get("stat_bonus", {}).get("defense", 0)
            dur = ea.get("current_durability", 0)
            max_dur = ea.get("max_durability", 1)
            equip_parts.append(f"+{dfn}🛡 [{dur}/{max_dur}]")
        equip_label = "  ".join(equip_parts) if equip_parts else "—"

        return {
            "hp": player_state.get("hp", 20),
            "max_hp": player_state.get("max_hp", 20) + max_hp_bonus,
            "gold": player_state.get("gold", 50),
            "level": player_state.get("level", 1),
            "equipment": equip_label,
            "kills": player_state.get("kills", 0),
            "buffs": "" if buff_summary == "No active effects." else buff_summary,
        }

    # ── internal helpers ──────────────────────────────────────────────

    def _get_location_description(self, location_id: str) -> str:
        entries = self._loader.get_lore(location_id)
        for kind in ("description", "ambient"):
            matches = [e for e in entries if e.get("type") == kind]
            if matches:
                return matches[0].get("text", "")
        return ""

    def _build_action_list(self, location_id: str) -> List[Dict]:
        action_ids = self._location_mgr.get_location_actions(location_id)
        return [{"id": aid, "label": self._action_label(aid)} for aid in action_ids]

    def _build_dungeon_actions(self, room: Dict, dungeon_state: Dict,
                               idx: int, total: int) -> List[Dict]:
        actions = []
        if room.get("has_enemy") and not room.get("cleared"):
            enemy = room.get("enemy")
            if enemy:
                actions.append({
                    "id": "enter_combat",
                    "label": f"Fight: {enemy.get('name', 'Unknown')}"
                })
        if room.get("has_item") and not room.get("cleared"):
            item = room.get("item")
            if item:
                actions.append({
                    "id": "take_item",
                    "label": f"Take: {item.get('name', 'Item')}"
                })
        if room.get("cleared") or (not room.get("has_enemy") and not room.get("has_item")):
            if idx < total:
                actions.append({"id": "next_room", "label": "Press deeper"})
            else:
                actions.append({"id": "dungeon_exit", "label": "Ascend — leave the dungeon"})
        actions.append({"id": "flee_dungeon", "label": "Flee the dungeon"})
        return actions

    @staticmethod
    def _action_label(action_id: str) -> str:
        labels = {
            "rest": "Rest",
            "hear_rumors": "Rumors",
            "sell_item": "Sell Item",
            "repair_weapon": "Repair Weapon",
            "repair_armor": "Repair Armor",
            "pay_taxes": "Pay Taxes",
            "view_debt": "View Debt",
            "take_bath": "Bath",
            "go_fishing": "Fish",
            "enter_dungeon": "Enter Dungeon",
            "go_city": "← City",
            "go_tavern": "Tavern",
            "go_marketplace": "Market",
            "go_alchemy_hall": "Alchemy",
            "go_blacksmiths_street": "Smithy",
            "go_city_hall": "City Hall",
            "go_coliseum": "Coliseum",
            "go_public_bath": "Bathhouse",
            "go_the_river": "River",
            "go_dungeon": "Dungeon Gate",
        }
        return labels.get(action_id, action_id.replace("_", " ").title())
