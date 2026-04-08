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
        return {"inventory": {"items": items, "detail": detail}}

    def build_lore_state(self) -> Dict:
        return {"lore": {"entries": self._loader.get_lore("global")}}

    def build_combat_state(self, combat_state: Dict) -> Dict:
        enemy = combat_state["enemy"]
        return {
            "combat": {
                "log": combat_state.get("log_text", ""),
                "enemy_name": enemy.get("name", "Enemy"),
                "enemy_hp": combat_state.get("enemy_current_hp", 0),
                "actions": [
                    {"id": "attack", "label": "Attack"},
                    {"id": "flee", "label": "Flee"},
                ],
            }
        }

    def build_player_panel_data(self, player_state: Dict) -> Dict:
        return {
            "hp": player_state.get("hp", 20),
            "max_hp": player_state.get("max_hp", 20),
            "gold": player_state.get("gold", 50),
            "level": player_state.get("level", 1),
        }

    # ---------- internal helpers ----------
    def _get_location_description(self, location_id: str) -> str:
        entries = self._loader.get_lore(location_id)
        descriptions = [e for e in entries if e.get("type") == "description"]
        if descriptions:
            return descriptions[0].get("text", "")
        ambient = [e for e in entries if e.get("type") == "ambient"]
        if ambient:
            return ambient[0].get("text", "")
        return ""

    def _build_action_list(self, location_id: str) -> List[Dict]:
        action_ids = self._location_mgr.get_location_actions(location_id)
        return [{"id": aid, "label": self._action_label(aid)} for aid in action_ids]

    def _build_dungeon_actions(self, room: Dict, dungeon_state: Dict, idx: int, total: int) -> List[Dict]:
        actions = []
        if room.get("has_enemy") and not room.get("cleared"):
            enemy = room.get("enemy")
            if enemy:
                actions.append({"id": "enter_combat", "label": f"Fight: {enemy.get('name', 'Unknown')}"})
        if room.get("has_item") and not room.get("cleared"):
            item = room.get("item")
            if item:
                actions.append({"id": "take_item", "label": f"Take: {item.get('name', 'Item')}"})
        if room.get("cleared") or (not room.get("has_enemy") and not room.get("has_item")):
            if idx < total:
                actions.append({"id": "next_room", "label": "Press deeper"})
            else:
                actions.append({"id": "dungeon_exit", "label": "Ascend -- leave the dungeon"})
        actions.append({"id": "flee_dungeon", "label": "Flee the dungeon"})
        return actions

    @staticmethod
    def _action_label(action_id: str) -> str:
        labels = {
            "rest": "Rest for the night (costs gold)",
            "hear_rumors": "Listen for rumors",
            "buy_item": "Browse goods",
            "sell_item": "Sell an item",
            "buy_potion": "Buy a potion",
            "sell_reagent": "Sell reagents",
            "craft_consumable": "Craft a consumable",
            "buy_weapon": "Buy a weapon",
            "buy_armor": "Buy armor",
            "repair_equipment": "Repair equipment",
            "pay_taxes": "Pay annual taxes",
            "view_debt": "View tax status",
            "enter_combat_event": "Enter the arena",
            "watch_combat_event": "Watch a bout",
            "place_wager": "Place a wager",
            "take_bath": "Take a bath (costs gold)",
            "go_fishing": "Go fishing",
            "enter_dungeon": "Descend into the dungeon",
            "go_city": "Return to the city gates",
            "go_tavern": "Go to the Tavern",
            "go_marketplace": "Go to the Marketplace",
            "go_alchemy_hall": "Go to the Alchemy Hall",
            "go_blacksmiths_street": "Go to Blacksmiths Street",
            "go_city_hall": "Go to City Hall",
            "go_coliseum": "Go to the Coliseum",
            "go_public_bath": "Go to the Public Bath",
            "go_the_river": "Go to the River",
            "go_dungeon": "Go to the Dungeon Entrance",
        }
        return labels.get(action_id, action_id.replace("_", " ").title())