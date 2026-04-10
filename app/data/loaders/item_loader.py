"""Loads items.json. One job: serve item dicts by id or all at once."""
import json, os
from typing import Dict, List, Optional


class ItemLoader:
    _PATH = os.path.join("data", "dungeon", "items", "items.json")

    def __init__(self):
        self._items: List[Dict] = self._load()

    def _load(self) -> List[Dict]:
        if not os.path.exists(self._PATH):
            return []
        with open(self._PATH, encoding="utf-8") as f:
            return json.load(f)

    def get(self, item_id: str) -> Optional[Dict]:
        for item in self._items:
            if item.get("id") == item_id:
                return dict(item)
        return None

    def all(self) -> List[Dict]:
        return list(self._items)

    def by_source(self, source: str) -> List[Dict]:
        return [dict(i) for i in self._items if i.get("source") == source]

    def by_type(self, item_type: str) -> List[Dict]:
        return [dict(i) for i in self._items if i.get("type") == item_type]
