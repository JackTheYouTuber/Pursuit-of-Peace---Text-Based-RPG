"""Loads enemies.json. One job: serve enemy dicts by id, depth, or all."""
import json, os
from typing import Dict, List, Optional


class EnemyLoader:
    _PATH = os.path.join("data", "dungeon", "enemies", "enemies.json")

    def __init__(self):
        self._enemies: List[Dict] = self._load()

    def _load(self) -> List[Dict]:
        if not os.path.exists(self._PATH):
            return []
        with open(self._PATH, encoding="utf-8") as f:
            return json.load(f)

    def get(self, enemy_id: str) -> Optional[Dict]:
        for e in self._enemies:
            if e.get("id") == enemy_id:
                return dict(e)
        return None

    def all(self) -> List[Dict]:
        return list(self._enemies)

    def at_depth(self, depth: int) -> List[Dict]:
        return [dict(e) for e in self._enemies
                if e.get("min_depth", 1) <= depth <= e.get("max_depth", 99)]
