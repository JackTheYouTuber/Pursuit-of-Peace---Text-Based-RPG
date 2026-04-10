"""Loads lore files on demand and caches them. One job: serve lore entries."""
import json, os
from typing import Dict, List


class LoreLoader:
    _DIR = os.path.join("data", "lore")

    def __init__(self):
        self._cache: Dict[str, List[Dict]] = {}

    def get(self, location_id: str) -> List[Dict]:
        if location_id in self._cache:
            return self._cache[location_id]
        path = os.path.join(self._DIR, f"{location_id}.json")
        entries = []
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                entries = json.load(f)
        self._cache[location_id] = entries
        return entries

    def by_type(self, location_id: str, entry_type: str) -> List[Dict]:
        return [e for e in self.get(location_id) if e.get("type") == entry_type]
