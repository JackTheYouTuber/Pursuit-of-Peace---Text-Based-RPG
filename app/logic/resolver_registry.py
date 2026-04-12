"""
resolver_registry.py — scans app/logic/resolvers/ recursively and
builds a {resolver_string: callable} lookup table.

Each resolver module must export:
    resolve(context: ActionContext) -> ActionResult

Resolver strings mirror the directory path, e.g.:
    app/logic/resolvers/location/bath.py  →  "location.bath"
    app/logic/resolvers/heal_player.py    →  "heal_player"
    app/logic/resolvers/combat/attack.py  →  "combat.attack"
"""
import importlib
import pathlib
import logging
from typing import Callable, Dict, Optional

from app.logic.action_types import ActionContext, ActionResult

_log = logging.getLogger(__name__)

# Root of the resolvers package (relative to project root)
_RESOLVERS_ROOT = pathlib.Path(__file__).parent / "resolvers"
_RESOLVERS_PKG  = "app.logic.resolvers"


class ResolverRegistry:
    """Singleton-style registry (create once, pass around)."""

    def __init__(self):
        self._table: Dict[str, Callable[[ActionContext], ActionResult]] = {}
        self._unavailable: set = set()
        self._scan()

    # ── Public API ──────────────────────────────────────────────────────

    def get(self, resolver_name: str) -> Optional[Callable[[ActionContext], ActionResult]]:
        return self._table.get(resolver_name)

    def is_available(self, resolver_name: str) -> bool:
        return resolver_name in self._table

    def all_names(self):
        return list(self._table.keys())

    def unavailable(self):
        return set(self._unavailable)

    # ── Internal ────────────────────────────────────────────────────────

    def _scan(self):
        if not _RESOLVERS_ROOT.exists():
            _log.warning("Resolvers directory not found: %s", _RESOLVERS_ROOT)
            return

        for py_file in sorted(_RESOLVERS_ROOT.rglob("*.py")):
            if py_file.stem.startswith("_"):
                continue
            resolver_name = self._path_to_name(py_file)
            module_path   = self._path_to_module(py_file)
            try:
                mod = importlib.import_module(module_path)
                fn  = getattr(mod, "resolve", None)
                if callable(fn):
                    self._table[resolver_name] = fn
                    _log.debug("Registered resolver: %s", resolver_name)
                else:
                    _log.warning("Module %s has no callable 'resolve'", module_path)
                    self._unavailable.add(resolver_name)
            except Exception as exc:
                _log.warning("Cannot load resolver %s: %s", module_path, exc)
                self._unavailable.add(resolver_name)

    @staticmethod
    def _path_to_name(py_file: pathlib.Path) -> str:
        """Convert resolvers/location/bath.py → 'location.bath'."""
        rel = py_file.relative_to(_RESOLVERS_ROOT)
        parts = list(rel.with_suffix("").parts)
        return ".".join(parts)

    @staticmethod
    def _path_to_module(py_file: pathlib.Path) -> str:
        """Convert resolvers/location/bath.py → 'app.logic.resolvers.location.bath'."""
        rel = py_file.relative_to(_RESOLVERS_ROOT.parent.parent.parent)
        parts = list(rel.with_suffix("").parts)
        return ".".join(parts)
