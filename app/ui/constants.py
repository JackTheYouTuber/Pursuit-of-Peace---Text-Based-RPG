"""
Dynamic theme constants – always fetch from StyleManager at runtime.
Usage: import app.ui.constants as const
       bg = const.CARD_BG
"""

from app.ui.style_manager import StyleManager

class _ThemeConstants:
    """Proxy that reads values from the current theme on each access."""

    @staticmethod
    def _get(path: str, default):
        try:
            theme = StyleManager.get_theme()
            keys = path.split('.')
            val = theme
            for k in keys:
                val = val.get(k, {})
                if val is None:
                    return default
            return val if val != {} else default
        except Exception:
            return default

    # Colors
    @property
    def CARD_BG(self):
        return self._get("global.card_bg", "#1e293b")

    @property
    def TEXT_FG(self):
        return self._get("global.fg", "#e2e8f0")

    @property
    def MUTED_FG(self):
        return self._get("global.muted_fg", "#94a3b8")

    @property
    def ACCENT_FG(self):
        return self._get("global.accent_fg", "#fbbf24")

    @property
    def ACTIVE_BG(self):
        return self._get("global.active_bg", "#3b82f6")

    @property
    def ACTIVE_FG(self):
        return self._get("global.active_fg", "#ffffff")

    # Fonts
    @property
    def FONT_FAMILY(self):
        return self._get("global.font_family", "Segoe UI")

    @property
    def FONT_SIZE(self):
        return self._get("global.font_size", 10)

    @property
    def FONT_BODY(self):
        return (self.FONT_FAMILY, self.FONT_SIZE)

    @property
    def FONT_BOLD(self):
        return (self.FONT_FAMILY, self.FONT_SIZE, "bold")

    @property
    def FONT_TITLE(self):
        return (self.FONT_FAMILY, self.FONT_SIZE + 4, "bold")

    # Padding – kept as properties for consistency (can be themed later)
    @property
    def PAD_SMALL(self): return 4
    @property
    def PAD_MEDIUM(self): return 8
    @property
    def PAD_LARGE(self): return 12
    @property
    def BUTTON_PADX(self): return 12
    @property
    def BUTTON_PADY(self): return 6


# Internal instance
_theme_constants = _ThemeConstants()

# Expose all attributes from the instance at the module level
def __getattr__(name):
    """Delegate any attribute not found in the module to the theme constants instance."""
    return getattr(_theme_constants, name)

# Optional: help IDEs with autocompletion
def __dir__():
    return dir(_theme_constants)