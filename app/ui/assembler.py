import tkinter as tk
from typing import Dict, Any, Callable, Optional

from app.ui.theme import load_theme
from app.ui.view_registry import ViewRegistry
from app.ui.style_manager import StyleManager

class UIAssembler:
    def __init__(
        self,
        root: tk.Widget,
        callbacks: Dict[str, Callable],
        theme_path: str = "data/ui/themes.json",
        layouts_dir: str = "data/ui/layouts",
        logger=None,
    ):
        self._root = root
        self._callbacks = callbacks
        self._layouts_dir = layouts_dir
        self._logger = logger
        self._theme = load_theme(theme_path, logger)
        # Initialize ttk styles from the loaded theme
        StyleManager.init_styles(root, self._theme)
        self._registry = ViewRegistry(root, callbacks, self._theme, layouts_dir, logger)

    def get_or_build_view(self, view_name: str, state: Dict) -> tk.Widget:
        return self._registry.get_or_build(view_name, state)

    def refresh_view(self, view_name: str, state: Dict):
        self._registry.refresh(view_name, state)

    def destroy_view(self, view_name: str):
        self._registry.destroy(view_name)