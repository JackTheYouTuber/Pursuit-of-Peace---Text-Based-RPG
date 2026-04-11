"""
view_builder.py — transforms game state into UI state dicts.

One job: read state, produce dicts. No mutation. No game logic.
Uses fragment simples for stat queries rather than managers.
"""
import random
from typing import Dict, List, Optional

from app.logic.simple.get_buff_bonus       import get_buff_bonus
from app.logic.simple.get_buff_summary     import get_buff_summary
from app.logic.simple.get_effective_max_hp import get_effective_max_hp


class ViewBuilder:
    def __init__(self, data_registry, player_mgr):
        self._reg    = data_registry
        self._player = player_mgr   # only used for build_player_panel

    def build_city(self, player_state: Dict, location_mgr, lore_loader) -> Dict:
        loc_id  = player_state.get("current_location_id", "city_entrance")
        entries = lore_loader.by_type(loc_id, "description")
        desc    = random.choice(entries)["text"] if entries else ""
        actions = [{"id": a, "label": _label(a)}
                   for a in location_mgr.actions(loc_id)]
        return {"location": {"description": desc, "actions": actions}}

    def build_dungeon(self, dungeon: Optional[Dict], dungeon_mgr) -> Dict:
        if not dungeon:
            return {"location": {"description": "", "actions": []}}
        room = dungeon_mgr.current_room(dungeon)
        if not room:
            return {"location": {"description": "", "actions": []}}
        idx   = dungeon.get("current_index", 0) + 1
        total = dungeon.get("total_rooms", 1)
        lore  = dungeon_mgr.room_lore(room)
        desc  = f"[ Room {idx}/{total}  Depth {room.get('depth', 1)} ]\n\n{lore}"
        return {"location": {"description": desc,
                             "actions": _dungeon_actions(room, idx, total)}}

    def build_inventory(self, player_state: Dict, detail: str = "") -> Dict:
        items = []
        for iid in player_state.get("inventory", []):
            item = self._reg.items.get(iid)
            items.append({"id": iid, "label": item["name"] if item else iid})

        ew = player_state.get("equipped_weapon")
        ea = player_state.get("equipped_armor")
        lines = []
        if ew:
            dmg = ew.get("item", {}).get("stat_bonus", {}).get("damage", 0)
            bar = _dur_bar(ew.get("current_durability", 0), ew.get("max_durability", 1))
            lines.append(f"⚔ {ew.get('item',{}).get('name','?')}  +{dmg} dmg\n  {bar}")
        else:
            lines.append("⚔ Weapon: — (unarmed)")
        if ea:
            dfn = ea.get("item", {}).get("stat_bonus", {}).get("defense", 0)
            bar = _dur_bar(ea.get("current_durability", 0), ea.get("max_durability", 1))
            lines.append(f"🛡 {ea.get('item',{}).get('name','?')}  +{dfn} def\n  {bar}")
        else:
            lines.append("🛡 Armor: — (no armor)")

        equip_actions = []
        if ew:
            equip_actions.append({"id": "unequip:equipped_weapon",
                                   "label": f"Unequip {ew.get('item',{}).get('name','weapon')}"})
        if ea:
            equip_actions.append({"id": "unequip:equipped_armor",
                                   "label": f"Unequip {ea.get('item',{}).get('name','armor')}"})

        return {"inventory": {
            "items": items,
            "detail": "\n".join(lines) + ("\n\n" + detail if detail else ""),
            "item_actions": equip_actions,
        }}

    def build_lore(self, lore_loader) -> Dict:
        return {"lore": {"entries": lore_loader.get("global")}}

    def build_combat(self, combat_snapshot: Optional[Dict],
                     player_state: Optional[Dict] = None) -> Dict:
        if not combat_snapshot:
            return {}
        enemy = combat_snapshot["enemy"]

        actions = [{"id": "attack", "label": "⚔ Attack"},
                   {"id": "flee",   "label": "🏃 Flee"}]
        if player_state:
            for iid in player_state.get("inventory", []):
                item = self._reg.items.get(iid)
                if item and item.get("type") == "consumable":
                    actions.append({"id": f"use_item:{iid}",
                                    "label": f"Use: {item['name']}"})

        equip_parts = []
        if player_state:
            ew = player_state.get("equipped_weapon")
            ea = player_state.get("equipped_armor")
            if ew:
                dmg = ew.get("item", {}).get("stat_bonus", {}).get("damage", 0)
                equip_parts.append(
                    f"⚔ +{dmg} ({ew.get('current_durability', 0)} dur)")
            if ea:
                dfn = ea.get("item", {}).get("stat_bonus", {}).get("defense", 0)
                equip_parts.append(
                    f"🛡 +{dfn} ({ea.get('current_durability', 0)} dur)")

        log = combat_snapshot.get("log_text", "")
        if equip_parts:
            log = "  ".join(equip_parts) + "\n" + "─" * 30 + "\n" + log

        return {"combat": {
            "log":          log,
            "enemy_name":   enemy.get("name", "Enemy"),
            "enemy_hp":     combat_snapshot.get("enemy_current_hp", 0),
            "player_hp":    combat_snapshot.get("player_current_hp", 0),
            "player_max_hp": combat_snapshot.get("player_max_hp", 20),
            "actions":      actions,
        }}

    def build_player_panel(self, player_state: Dict, player_mgr=None) -> Dict:
        max_hp_bonus = get_buff_bonus(player_state, "max_hp")
        ew = player_state.get("equipped_weapon")
        ea = player_state.get("equipped_armor")
        equip_parts = []
        if ew:
            dmg = ew.get("item", {}).get("stat_bonus", {}).get("damage", 0)
            equip_parts.append(
                f"+{dmg}⚔ [{ew.get('current_durability',0)}/{ew.get('max_durability',1)}]")
        if ea:
            dfn = ea.get("item", {}).get("stat_bonus", {}).get("defense", 0)
            equip_parts.append(
                f"+{dfn}🛡 [{ea.get('current_durability',0)}/{ea.get('max_durability',1)}]")
        return {
            "hp":        player_state.get("hp", 20),
            "max_hp":    player_state.get("max_hp", 20) + max_hp_bonus,
            "gold":      player_state.get("gold", 50),
            "level":     player_state.get("level", 1),
            "equipment": "  ".join(equip_parts) if equip_parts else "—",
            "kills":     player_state.get("kills", 0),
            "buffs":     get_buff_summary(player_state),
        }


# ── Helpers ────────────────────────────────────────────────────────────

def _dur_bar(cur: int, mx: int, width: int = 10) -> str:
    if mx <= 0:
        return "[" + "░" * width + "] 0/0"
    filled = round(width * cur / mx)
    pct    = cur / mx
    char   = "█" if pct > 0.5 else "▓" if pct > 0.2 else "▒"
    return "[" + char * filled + "░" * (width - filled) + f"] {cur}/{mx}"


def _dungeon_actions(room: Dict, idx: int, total: int) -> List[Dict]:
    actions = []
    if room.get("has_enemy") and not room.get("cleared"):
        enemy = room.get("enemy")
        if enemy:
            actions.append({"id": "enter_combat",
                             "label": f"Fight: {enemy.get('name', '?')}"})
    if room.get("has_item") and not room.get("cleared"):
        item = room.get("item")
        if item:
            actions.append({"id": "take_item",
                             "label": f"Take: {item.get('name', '?')}"})
    if room.get("cleared") or (not room.get("has_enemy") and not room.get("has_item")):
        if idx < total:
            actions.append({"id": "next_room", "label": "Press deeper"})
        else:
            actions.append({"id": "dungeon_exit",
                             "label": "Ascend — leave the dungeon"})
    actions.append({"id": "flee_dungeon", "label": "Flee the dungeon"})
    return actions


_LABELS = {
    "rest": "Rest", "hear_rumors": "Rumors", "sell_item": "Sell Item",
    "repair_weapon": "Repair Weapon", "repair_armor": "Repair Armor",
    "pay_taxes": "Pay Taxes", "view_debt": "View Debt",
    "take_bath": "Bath", "go_fishing": "Fish",
    "enter_dungeon": "Enter Dungeon", "go_city": "← City",
    "go_tavern": "Tavern", "go_marketplace": "Market",
    "go_alchemy_hall": "Alchemy", "go_blacksmiths_street": "Smithy",
    "go_city_hall": "City Hall", "go_coliseum": "Coliseum",
    "go_public_bath": "Bathhouse", "go_the_river": "River",
    "go_dungeon": "Dungeon Gate",
}

def _label(action_id: str) -> str:
    return _LABELS.get(action_id, action_id.replace("_", " ").title())
