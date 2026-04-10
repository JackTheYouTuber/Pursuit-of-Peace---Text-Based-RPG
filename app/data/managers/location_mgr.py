"""Knows city locations and their available actions. One job: answer navigation questions."""
from typing import Dict, List


class LocationMgr:
    def __init__(self, config_loader):
        self._services  = config_loader.services()
        self._locations = {loc["id"]: loc for loc in config_loader.locations()}

    def exists(self, location_id: str) -> bool:
        return location_id in self._locations

    def actions(self, location_id: str) -> List[str]:
        return list(self._services.get(location_id, {}).get("actions", []))

    def service_cfg(self, location_id: str) -> Dict:
        return dict(self._services.get(location_id, {}))

    def all_location_ids(self) -> List[str]:
        return list(self._locations.keys())
