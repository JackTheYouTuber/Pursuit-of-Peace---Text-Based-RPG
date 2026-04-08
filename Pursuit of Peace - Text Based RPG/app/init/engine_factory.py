from app.data_loader import DataLoader
from app.dungeon_manager import DungeonManager
from app.location_manager import LocationManager
from app.game_engine import GameEngine


class EngineFactory:
    """Creates a GameEngine with a loaded profile state."""

    @staticmethod
    def create(profile_state: dict, data_loader: DataLoader, logger=None):
        dungeon_mgr = DungeonManager(data_loader, logger=logger)
        location_mgr = LocationManager(data_loader, dungeon_mgr, logger=logger)
        engine = GameEngine(data_loader, location_mgr, dungeon_mgr, logger=logger)
        engine._state_mgr.update_player(profile_state)
        return engine