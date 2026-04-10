"""Builds the Engine with a DataRegistry. One job: wire it all together at startup."""
from app.data.init.registry      import DataRegistry
from app.logic.core.engine       import Engine


class EngineFactory:
    @staticmethod
    def create(profile_state: dict, profile_name: str = None, logger=None) -> Engine:
        reg    = DataRegistry()
        engine = Engine(reg, profile_name=profile_name, logger=logger)
        engine._state.set_player(profile_state)
        return engine
