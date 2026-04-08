import json
import os
from typing import Dict, Optional, Any

def load_theme(theme_path: str = "data/ui/themes.json", logger: Optional[Any] = None) -> Dict:
    """Load theme JSON, return dict with defaults."""
    default = {"global": {"bg": "#0d1b2a", "fg": "#d4c9a8"}}
    if not os.path.exists(theme_path):
        return default
    try:
        with open(theme_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        if logger:
            logger.error(f"Failed to load theme: {e}")
        return default