"""Generates dungeon runs from config and templates. One job: produce dungeon state dicts."""
import random
from typing import Dict, List, Optional


class DungeonGen:
    def __init__(self, config_loader, item_loader, enemy_loader, lore_loader):
        self._cfg     = config_loader
        self._items   = item_loader
        self._enemies = enemy_loader
        self._lore    = lore_loader

    def generate(self) -> Dict:
        cfg = self._cfg.dungeon()
        templates = self._cfg.rooms()
        total = random.randint(cfg.get("min_rooms", 5), cfg.get("max_rooms", 12))
        max_d = cfg.get("max_depth", 5)

        rooms = []
        for i in range(total):
            depth = max(1, round(1 + (max_d - 1) * i / max(total - 1, 1)))
            tpl   = random.choice(templates) if templates else {}
            rooms.append(self._build_room(depth, tpl))

        return {"rooms": rooms, "total_rooms": total, "current_index": 0, "active": True}

    def _build_room(self, depth: int, tpl: Dict) -> Dict:
        enemy = self._pick_enemy(depth) if tpl.get("has_enemy") else None
        item  = self._pick_item(depth)  if tpl.get("has_item")  else None
        return {
            "depth": depth,
            "template_id": tpl.get("id", "room_unknown"),
            "lore_key": tpl.get("lore_key", ""),
            "has_enemy": enemy is not None,
            "has_item":  item  is not None,
            "enemy": enemy,
            "item":  item,
            "cleared": False,
        }

    def _pick_enemy(self, depth: int) -> Optional[Dict]:
        pool = self._enemies.at_depth(depth)
        return dict(random.choice(pool)) if pool else None

    def _pick_item(self, depth: int) -> Optional[Dict]:
        pool = [i for i in self._items.all()
                if i.get("min_depth", 0) <= depth and i.get("source") is None]
        return dict(random.choice(pool)) if pool else None

    # -- Room navigation helpers --
    def current_room(self, dungeon: Dict) -> Optional[Dict]:
        idx = dungeon.get("current_index", 0)
        rooms = dungeon.get("rooms", [])
        return rooms[idx] if idx is not None and idx < len(rooms) else None

    def advance(self, dungeon: Dict):
        d = dict(dungeon)
        d["current_index"] = d.get("current_index", 0) + 1
        return d

    def mark_cleared(self, dungeon: Dict) -> Dict:
        d = dict(dungeon)
        rooms = list(d.get("rooms", []))
        idx = d.get("current_index", 0)
        if idx < len(rooms):
            r = dict(rooms[idx])
            r["cleared"] = True
            rooms[idx] = r
        d["rooms"] = rooms
        return d

    def at_exit(self, dungeon: Dict) -> bool:
        return dungeon.get("current_index", 0) >= dungeon.get("total_rooms", 0)

    def room_lore_text(self, room: Dict) -> str:
        key = room.get("lore_key", "")
        entries = self._lore.get("dungeon")
        for e in entries:
            if e.get("id") == key:
                return e.get("text", "")
        return ""
