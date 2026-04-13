import json
import os
from datetime import datetime
from typing import Dict, List, Optional

from app.paths import data_path


class ProfileManager:
    """Manage player profiles stored as JSON files in data/player/profiles/"""

    @property
    def PROFILES_DIR(self) -> str:
        return str(data_path("player", "profiles"))

    def __init__(self, logger=None):
        self._logger = logger
        os.makedirs(self.PROFILES_DIR, exist_ok=True)

    def list_profiles(self) -> List[str]:
        """Return list of profile names (without .json extension)."""
        try:
            files = [f for f in os.listdir(self.PROFILES_DIR) if f.endswith(".json")]
            return sorted([os.path.splitext(f)[0] for f in files])
        except OSError:
            return []

    def profile_exists(self, name: str) -> bool:
        """Check if a profile with given name exists."""
        path = os.path.join(self.PROFILES_DIR, f"{name}.json")
        return os.path.exists(path)

    def load_profile(self, name: str) -> Optional[Dict]:
        """Load player state from profile file. Returns None if not found or corrupt."""
        path = os.path.join(self.PROFILES_DIR, f"{name}.json")
        if not os.path.exists(path):
            if self._logger:
                self._logger.warn(f"Profile not found: {name}")
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Ensure required fields exist
            if "player_state" not in data:
                raise ValueError("Missing player_state in profile")
            return data["player_state"]
        except (json.JSONDecodeError, ValueError, OSError) as e:
            if self._logger:
                self._logger.error(f"Failed to load profile {name}: {e}")
            return None

    def save_profile(self, name: str, player_state: Dict) -> bool:
        """Save player state to profile file. Returns success."""
        path = os.path.join(self.PROFILES_DIR, f"{name}.json")
        data = {
            "profile_name": name,
            "last_saved": datetime.now().isoformat(),
            "player_state": player_state,
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            if self._logger:
                self._logger.info(f"Saved profile: {name}")
            return True
        except OSError as e:
            if self._logger:
                self._logger.error(f"Failed to save profile {name}: {e}")
            return False

    def delete_profile(self, name: str) -> bool:
        """Delete profile file. Returns success."""
        path = os.path.join(self.PROFILES_DIR, f"{name}.json")
        try:
            if os.path.exists(path):
                os.remove(path)
                if self._logger:
                    self._logger.info(f"Deleted profile: {name}")
                return True
            return False
        except OSError as e:
            if self._logger:
                self._logger.error(f"Failed to delete profile {name}: {e}")
            return False

    def create_new_profile(self, name: str, default_state: Dict) -> Optional[Dict]:
        """Create a new profile with default player state and save it. Returns saved state."""
        if self.profile_exists(name):
            if self._logger:
                self._logger.warn(f"Profile {name} already exists, not overwriting")
            return None
        # Ensure no internal references are shared
        saved_state = dict(default_state)
        # Reset any runtime flags if needed
        saved_state["tax_paid"] = False
        saved_state["year"] = 1
        saved_state["hp"] = saved_state.get("max_hp", 20)
        success = self.save_profile(name, saved_state)
        if success:
            return saved_state
        return None