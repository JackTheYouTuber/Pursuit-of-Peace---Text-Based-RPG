"""
view_coordinator.py

Responsible for:
- Managing which UI view is currently displayed.
- Requesting view state from the game engine.
- Using the UIAssembler to build or retrieve views.
- Refreshing the active view when the game state changes.

Does NOT contain game logic or direct UI widget creation.
"""

import tkinter as tk
from typing import Any, Optional

from app.ui.complex.assembler import UIAssembler


class ViewCoordinator:
    """
    Coordinates all content views in the main content frame.

    The coordinator maintains a reference to the content frame, the
    UIAssembler, and the game engine (which provides view states).
    It provides methods to switch views and refresh the current view.
    """

    def __init__(
        self,
        content_frame: tk.Frame,
        assembler: UIAssembler,
        game_engine: Any,  # Duck‑typed: must have get_view_state(view_name) -> dict
        logger: Optional[Any] = None,
    ):
        """
        Args:
            content_frame: The tkinter frame where views are displayed.
            assembler: The UIAssembler instance for building/updating views.
            game_engine: The game logic object. Must implement get_view_state(view_name).
            logger: Optional GameLogger instance.
        """
        self._content_frame = content_frame
        self._assembler = assembler
        self._engine = game_engine
        self._logger = logger

        self._active_view: Optional[str] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def show_view(self, view_name: str) -> None:
        """
        Switch to the requested view.

        Retrieves the current state for that view from the game engine,
        asks the assembler to build or retrieve the view widget, and raises it.
        """
        if self._logger:
            self._logger.info(f"Showing view: {view_name}")

        # Get the current state for this view from the game engine
        state = self._engine.get_view_state(view_name)

        # Build or retrieve the view widget
        widget = self._assembler.get_or_build_view(view_name, state)

        # Ensure the widget is placed in the content frame (if not already)
        # The assembler should have already gridded it, but we raise it.
        widget.tkraise()
        self._active_view = view_name

    def refresh_active_view(self) -> None:
        """Refresh the currently active view with fresh state from the game engine."""
        if self._active_view is None:
            if self._logger:
                self._logger.warn("refresh_active_view called but no active view set")
            return

        if self._logger:
            self._logger.info(f"Refreshing active view: {self._active_view}")

        state = self._engine.get_view_state(self._active_view)
        self._assembler.refresh_view(self._active_view, state)

    def refresh_view(self, view_name: str) -> None:
        """
        Refresh a specific view (even if it is not currently active).
        Useful for updating background views before they are shown.
        """
        if self._logger:
            self._logger.info(f"Refreshing view: {view_name}")

        state = self._engine.get_view_state(view_name)
        self._assembler.refresh_view(view_name, state)

    def get_active_view(self) -> Optional[str]:
        """Return the name of the currently active view, or None."""
        return self._active_view

    def destroy_view(self, view_name: str) -> None:
        """Completely remove a view from memory (free resources)."""
        if self._logger:
            self._logger.info(f"Destroying view: {view_name}")
        self._assembler.destroy_view(view_name)
        if self._active_view == view_name:
            self._active_view = None

    # ------------------------------------------------------------------
    # Optional: view existence check
    # ------------------------------------------------------------------

    def view_exists(self, view_name: str) -> bool:
        """Check if the assembler has already built this view."""
        # This could be exposed by the assembler; for now we rely on internal.
        # We can add a method to UIAssembler if needed.
        return view_name in self._assembler._views  # May need public method