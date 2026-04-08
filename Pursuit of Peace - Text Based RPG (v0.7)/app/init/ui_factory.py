import tkinter as tk
from app.ui_assembler import UIAssembler
from app.view_coordinator import ViewCoordinator
from app.ui.main_window import MainWindow
from app.ui.menu import GameMenu


class UIFactory:
    """Builds the main window, menu, assembler, and coordinator."""

    @staticmethod
    def create(root: tk.Tk, engine, callbacks: dict, logger=None):
        """
        Returns (assembler, coordinator, main_window).
        """
        # MainWindow already built the root? Actually MainWindow creates its own root.
        # But we already have root from the app. So we need to adapt.
        # Better: MainWindow should accept an existing root or be built after root exists.
        # Let's assume MainWindow is built elsewhere and we just get content frame.
        # For simplicity, we'll have UIFactory accept a content frame.
        pass