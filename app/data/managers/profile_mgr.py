"""Reads, writes, and deletes player profile files. One job: profile persistence."""
import json, os
from datetime import datetime
from typing import Dict, List, Optional

from app.paths import data_path


class ProfileMgr:
    @property
    def _DIR(self) -> str:
        return str(data_path("player", "profiles"))

    def __init__(self):
        os.makedirs(self._DIR, exist_ok=True)

    def list(self) -> List[str]:
        try:
            return sorted(f[:-5] for f in os.listdir(self._DIR) if f.endswith(".json"))
        except OSError:
            return []

    def exists(self, name: str) -> bool:
        return os.path.exists(self._path(name))

    def load(self, name: str) -> Optional[Dict]:
        path = self._path(name)
        if not os.path.exists(path):
            return None
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("player_state")

    def save(self, name: str, player_state: Dict) -> bool:
        try:
            with open(self._path(name), "w", encoding="utf-8") as f:
                json.dump({"profile_name": name,
                           "last_saved": datetime.now().isoformat(),
                           "player_state": player_state}, f, indent=2)
            return True
        except OSError:
            return False

    def delete(self, name: str) -> bool:
        path = self._path(name)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False

    def create(self, name: str, defaults: Dict) -> Optional[Dict]:
        state = dict(defaults)
        state.update({"tax_paid": False, "year": 1, "hp": defaults.get("max_hp", 20)})
        return state if self.save(name, state) else None

    def _path(self, name: str) -> str:
        return os.path.join(self._DIR, f"{name}.json")
