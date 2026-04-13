import tkinter as tk
from typing import Dict, Callable

from app.ui.simple.theme import load_theme
from app.ui.simple.view_registry import ViewRegistry
from app.ui.simple.style_manager import StyleManager
from app.paths import data_path

class UIAssembler:
    def __init__(
        self,
        root: tk.Widget,
        callbacks: Dict[str, Callable],
        theme_path: str = None,
        layouts_dir: str = None,
        logger=None,
    ):
        self._root = root
        self._callbacks = callbacks
        if theme_path is None:
            theme_path = str(data_path("ui", "themes.json"))
        if layouts_dir is None:
            layouts_dir = str(data_path("ui", "layouts"))
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