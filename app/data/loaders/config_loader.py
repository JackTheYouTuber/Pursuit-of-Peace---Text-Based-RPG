"""Loads all small config JSONs. One job: serve config dicts."""
import json, os
from typing import Dict


def _load(path: str, default: Dict) -> Dict:
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class ConfigLoader:
    def __init__(self):
        self._prices    = _load(os.path.join("data","economy","prices.json"),
                                {"rest":10,"bath":15,"tax":100,"repair_per_point":5,"sell_price_multiplier":0.4})
        self._services  = _load(os.path.join("data","city","services.json"), {})
        self._locations = _load(os.path.join("data","city","locations.json"), [])
        self._dungeon   = _load(os.path.join("data","dungeon","config.json"),
                                {"min_rooms":5,"max_rooms":12,"max_depth":5})
        self._rooms     = _load(os.path.join("data","dungeon","rooms","room_templates.json"), [])
        self._defaults  = _load(os.path.join("data","player","defaults.json"), {})
        self._themes    = _load(os.path.join("data","ui","themes.json"), {})

    def prices(self)    -> Dict: return dict(self._prices)
    def services(self)  -> Dict: return dict(self._services)
    def locations(self) -> list: return list(self._locations)
    def dungeon(self)   -> Dict: return dict(self._dungeon)
    def rooms(self)     -> list: return list(self._rooms)
    def defaults(self)  -> Dict: return dict(self._defaults)
    def themes(self)    -> Dict: return dict(self._themes)
