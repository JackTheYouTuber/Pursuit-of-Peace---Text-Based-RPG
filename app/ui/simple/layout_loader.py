import json
import os
from typing import Dict, Optional, Any

def load_layout(view_name: str, layouts_dir: str = "data/ui/layouts", logger: Optional[Any] = None) -> Optional[Dict]:
    """Load layout JSON for a view, return None on failure."""
    path = os.path.join(layouts_dir, f"{view_name}.json")
    if not os.path.exists(path):
        if logger:
            logger.warn(f"Layout not found: {path}")
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        if logger:
            logger.error(f"Failed to load layout {view_name}: {e}")
        return None