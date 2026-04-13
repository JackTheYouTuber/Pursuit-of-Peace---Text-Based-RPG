import json
import os

from app.paths import data_path


class DataLoader:
    """Central JSON loader and in-memory data cache."""

    def __init__(self, logger=None):
        self._logger = logger
        self._locations = []
        self._services = {}
        self._dungeon_config = {}
        self._room_templates = []
        self._enemies = []
        self._items = []
        self._prices = {}
        self._inventory_templates = []
        self._events = []
        self._player_defaults = {}
        self._lore_cache = {}

        self._load_all()

    # ------------------------------------------------------------------
    # Safe JSON loading
    # ------------------------------------------------------------------

    def safe_load_json(self, path, default):
        """Load a JSON file safely, never raising to the caller."""
        if not os.path.exists(path):
            if self._logger:
                self._logger.warn(
                    f"File not found, creating with default: {path}",
                    context="safe_load_json",
                )
            self._write_default(path, default)
            return default

        try:
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, ValueError) as exc:
            if self._logger:
                self._logger.error(
                    f"Invalid JSON in {path}: {exc}. Overwriting with default.",
                    context="safe_load_json",
                )
            self._write_default(path, default)
            return default

    def _write_default(self, path, default):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(default, fh, indent=2)

    # ------------------------------------------------------------------
    # Load all data at init
    # ------------------------------------------------------------------

    def _load_all(self):
        def p(*parts):
            return str(data_path(*parts))

        self._locations = self.safe_load_json(
            p("city", "locations.json"), []
        )
        self._services = self.safe_load_json(
            p("city", "services.json"), {}
        )
        self._dungeon_config = self.safe_load_json(
            p("dungeon", "config.json"),
            {"min_rooms": 5, "max_rooms": 10, "max_depth": 5},
        )
        self._room_templates = self.safe_load_json(
            p("dungeon", "rooms", "room_templates.json"), []
        )
        self._enemies = self.safe_load_json(
            p("dungeon", "enemies", "enemies.json"), []
        )
        self._items = self.safe_load_json(
            p("dungeon", "items", "items.json"), []
        )
        self._prices = self.safe_load_json(
            p("economy", "prices.json"),
            {"rest": 10, "bath": 15, "tax": 100, "repair_per_point": 5},
        )
        self._inventory_templates = self.safe_load_json(
            p("economy", "inventory_templates.json"), []
        )
        self._events = self.safe_load_json(
            p("events", "events.json"), []
        )
        self._player_defaults = self.safe_load_json(
            p("player", "defaults.json"),
            {
                "hp": 20,
                "max_hp": 20,
                "gold": 50,
                "level": 1,
                "inventory": [],
                "year": 1,
                "tax_paid": False,
                "buffs": [],
            },
        )

        if self._logger:
            self._logger.system("All data files loaded.")

    # ------------------------------------------------------------------
    # Lore loader (on-demand, cached)
    # ------------------------------------------------------------------

    def load_lore(self, location):
        """Load lore for a specific location key (e.g. 'tavern' or 'global')."""
        if location in self._lore_cache:
            return self._lore_cache[location]
        path = str(data_path("lore", f"{location}.json"))
        entries = self.safe_load_json(path, [])
        self._lore_cache[location] = entries
        return entries

    # ------------------------------------------------------------------
    # Typed getters
    # ------------------------------------------------------------------

    def get_location(self, location_id):
        for loc in self._locations:
            if loc.get("id") == location_id:
                return loc
        raise ValueError(f"Location id not found: '{location_id}'")

    def get_all_locations(self):
        return list(self._locations)

    def get_enemy(self, enemy_id):
        for enemy in self._enemies:
            if enemy.get("id") == enemy_id:
                return enemy
        raise ValueError(f"Enemy id not found: '{enemy_id}'")

    def get_all_enemies(self):
        return list(self._enemies)

    def get_item(self, item_id):
        for item in self._items:
            if item.get("id") == item_id:
                return item
        raise ValueError(f"Item id not found: '{item_id}'")

    def get_all_items(self):
        return list(self._items)

    def get_event(self, event_id):
        for event in self._events:
            if event.get("id") == event_id:
                return event
        raise ValueError(f"Event id not found: '{event_id}'")

    def get_events_for_location(self, location):
        return [e for e in self._events if e.get("location") == location]

    def get_lore(self, location):
        return self.load_lore(location)

    def get_services(self):
        return dict(self._services)

    def get_dungeon_config(self):
        return dict(self._dungeon_config)

    def get_room_templates(self):
        return list(self._room_templates)

    def get_prices(self):
        return dict(self._prices)

    def get_inventory_templates(self):
        return list(self._inventory_templates)

    def get_player_defaults(self):
        return dict(self._player_defaults)
