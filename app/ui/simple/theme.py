import json
import os
from typing import Dict, Any, Optional

# Default fallback theme (hardcoded, user‑friendly)
DEFAULT_THEME = {
    "global": {
        "bg": "#0f172a",
        "fg": "#e2e8f0",
        "font_family": "Segoe UI",
        "font_size": 10,
    },
    "TextDisplay": {
        "bg": "#334155",
        "fg": "#e2e8f0",
    },
    "MenuList": {
        "bg": "#1e293b",
    },
    "StatBar": {
        "bg": "#1e293b",
        "label_fg": "#94a3b8",
        "value_fg": "#fbbf24",
    },
    "ActionButton": {
        "bg": "#3b82f6",
        "fg": "#ffffff",
    },
    "DialogBox": {
        "bg": "#1e293b",
        "title_fg": "#fbbf24",
        "body_fg": "#e2e8f0",
        "button_bg": "#3b82f6",
        "button_fg": "#ffffff",
    },
    "CombatPanel": {
        "bg": "#1a0a0a",
        "header_fg": "#e94560",
    },
    "InventoryPanel": {"bg": "#16213e"},
    "LocationPanel": {"bg": "#16213e"},
    "LorePanel": {"bg": "#16213e"},
    "PlayerPanel": {"bg": "#16213e"},
}

def load_theme(theme_path: str = "data/ui/themes.json", logger: Optional[Any] = None) -> Dict:
    """Load theme from JSON, merge with defaults, write back if incomplete."""
    theme = DEFAULT_THEME.copy()
    
    if os.path.exists(theme_path):
        try:
            with open(theme_path, "r", encoding="utf-8") as f:
                user_theme = json.load(f)
            # Recursive merge (user overrides defaults)
            theme = _deep_merge(theme, user_theme)
        except Exception as e:
            if logger:
                logger.error(f"Failed to load theme JSON: {e}")
    else:
        if logger:
            logger.info(f"Theme file not found, using defaults and creating {theme_path}")
    
    # Write back merged theme to ensure JSON is complete
    try:
        os.makedirs(os.path.dirname(theme_path), exist_ok=True)
        with open(theme_path, "w", encoding="utf-8") as f:
            json.dump(theme, f, indent=2)
    except Exception as e:
        if logger:
            logger.error(f"Failed to write theme JSON: {e}")
    
    return theme

def _deep_merge(base: Dict, overrides: Dict) -> Dict:
    """Recursively merge two dictionaries."""
    result = base.copy()
    for key, value in overrides.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result