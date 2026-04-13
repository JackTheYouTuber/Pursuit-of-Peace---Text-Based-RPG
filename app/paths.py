"""
paths.py — Robust base-directory resolver.

Works correctly in three environments:
  1. Running as a plain Python script  (python main.pyw)
  2. Running as a PyInstaller one-dir bundle  (PursuitOfPeace.exe)
  3. Running DevTools.pyw from the project root

Usage:
    from app.paths import get_base_dir, data_path

    cfg = data_path("city", "services.json")   # → Path(...)/data/city/services.json
    actions_dir = data_path("actions")          # → Path(...)/data/actions
"""
from __future__ import annotations

import sys
from pathlib import Path


def get_base_dir() -> Path:
    """Return the project root (the folder that contains the 'data/' directory).

    • Frozen (PyInstaller):  the directory that holds the .exe file.
    • Script mode:           two levels up from this file  (app/paths.py → project root).
    """
    if getattr(sys, "frozen", False):
        # sys.executable is the .exe; its parent is the dist/<name>/ folder
        # which must sit next to the 'data/' directory.
        return Path(sys.executable).parent
    # __file__ is  <project_root>/app/paths.py
    return Path(__file__).resolve().parent.parent


def data_path(*parts: str) -> Path:
    """Return an absolute Path inside the project's data/ folder.

    Example:
        data_path("city", "services.json")
        → /abs/path/to/project/data/city/services.json
    """
    return get_base_dir() / "data" / Path(*parts)
