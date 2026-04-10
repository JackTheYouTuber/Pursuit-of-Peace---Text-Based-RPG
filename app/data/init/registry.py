"""Single entry point that builds and holds all data objects."""
from app.data.loaders.item_loader   import ItemLoader
from app.data.loaders.enemy_loader  import EnemyLoader
from app.data.loaders.lore_loader   import LoreLoader
from app.data.loaders.config_loader import ConfigLoader
from app.data.managers.profile_mgr  import ProfileMgr
from app.data.managers.dungeon_gen  import DungeonGen
from app.data.managers.location_mgr import LocationMgr


class DataRegistry:
    """Build once at startup. Pass around. Never rebuild."""

    def __init__(self):
        self.config   = ConfigLoader()
        self.items    = ItemLoader()
        self.enemies  = EnemyLoader()
        self.lore     = LoreLoader()
        self.profiles = ProfileMgr()
        self.dungeon  = DungeonGen(self.config, self.items, self.enemies, self.lore)
        self.location = LocationMgr(self.config)
