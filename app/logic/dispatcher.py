"""
dispatcher.py — the Active Action Dispatch (AAD) system core.

ActionDispatcher does three things:
  1. load_actions()  — reads every JSON in data/actions/, validates schema,
                       stores metadata keyed by action id.
  2. dispatch()      — merges global state with overrides, finds the resolver,
                       calls it, applies state changes, chains sub-actions.
  3. Reports unavailable actions (bad resolver reference or broken module).

The dispatcher never writes to disk. It only produces new state dicts.
Callers (Engine, managers) are responsible for persisting state.
"""
from __future__ import annotations

import json
import logging
import pathlib
from typing import Any, Dict, List, Optional, Tuple

from app.logic.action_types     import ActionContext, ActionResult
from app.logic.resolver_registry import ResolverRegistry

_log = logging.getLogger(__name__)

_ACTIONS_DIR = pathlib.Path(__file__).parent.parent.parent / "data" / "actions"

# Minimal required fields in every action JSON
_REQUIRED_FIELDS = {"id", "resolver"}


class ActionDispatcher:
    """Load action metadata and dispatch action_ids through resolvers."""

    def __init__(self, registry: Optional[ResolverRegistry] = None,
                 data_registry: Any = None,
                 logger=None):
        self._reg     = registry or ResolverRegistry()
        self._data    = data_registry   # DataRegistry (items, config, etc.)
        self._logger  = logger
        self._actions: Dict[str, Dict] = {}   # action_id → metadata dict
        self._unavailable: set = set()
        self.load_actions()

    # ── Public API ──────────────────────────────────────────────────────

    def load_actions(self):
        """Read all data/actions/*.json, validate, register."""
        self._actions.clear()
        self._unavailable.clear()

        if not _ACTIONS_DIR.exists():
            _log.warning("Actions directory not found: %s", _ACTIONS_DIR)
            return

        for json_file in sorted(_ACTIONS_DIR.rglob("*.json")):
            try:
                with open(json_file, encoding="utf-8") as f:
                    meta = json.load(f)
            except Exception as exc:
                _log.warning("Cannot parse action file %s: %s", json_file.name, exc)
                continue

            # Validate required fields
            missing = _REQUIRED_FIELDS - set(meta.keys())
            if missing:
                _log.warning("Action file %s missing fields: %s", json_file.name, missing)
                self._unavailable.add(json_file.stem)
                continue

            action_id = meta["id"]
            resolver  = meta["resolver"]

            if not self._reg.is_available(resolver):
                _log.warning(
                    "Action '%s' references unavailable resolver '%s' — skipped.",
                    action_id, resolver
                )
                self._unavailable.add(action_id)
                continue

            self._actions[action_id] = meta
            _log.debug("Loaded action: %s (resolver=%s)", action_id, resolver)

        _log.info("ActionDispatcher: %d actions loaded, %d unavailable.",
                  len(self._actions), len(self._unavailable))

    def is_available(self, action_id: str) -> bool:
        return action_id in self._actions

    def get_meta(self, action_id: str) -> Optional[Dict]:
        return self._actions.get(action_id)

    def dispatch(
        self,
        action_id: str,
        player_state: Dict,
        dungeon_state: Optional[Dict] = None,
        location_state: Optional[Dict] = None,
        context_overrides: Optional[Dict] = None,
    ) -> ActionResult:
        """
        Resolve action_id against current state.

        Returns ActionResult with updated state dicts and messages.
        Recursively resolves any dispatched_actions in the result.
        """
        meta = self._actions.get(action_id)
        if meta is None:
            msg = f"Unknown or unavailable action: '{action_id}'"
            _log.warning(msg)
            return ActionResult(
                new_player_state=dict(player_state),
                new_dungeon_state=dungeon_state,
                messages=[msg],
            )

        overrides = context_overrides or {}

        ctx = ActionContext(
            player_state   = dict(player_state),
            dungeon_state  = dungeon_state,
            location_state = location_state,
            entity_id      = overrides.get("entity_id", "0"),
            quantity       = overrides.get("quantity",  meta.get("cost", {}).get("gold", 0)),
            reference      = overrides.get("reference", meta.get("reference")),
            action_id      = action_id,
            data_registry  = self._data,
        )

        resolver_fn = self._reg.get(meta["resolver"])
        if resolver_fn is None:
            msg = f"Resolver missing at runtime: '{meta['resolver']}'"
            _log.error(msg)
            return ActionResult(
                new_player_state=dict(player_state),
                new_dungeon_state=dungeon_state,
                messages=[msg],
            )

        # DATA log
        if self._logger:
            self._logger.data(f"dispatch:{action_id}", {
                "resolver": meta["resolver"],
                "entity_id": ctx.entity_id,
            })

        try:
            result: ActionResult = resolver_fn(ctx)
        except Exception as exc:
            _log.exception("Resolver '%s' raised: %s", meta["resolver"], exc)
            return ActionResult(
                new_player_state=dict(player_state),
                new_dungeon_state=dungeon_state,
                messages=[f"Error in resolver '{meta['resolver']}': {exc}"],
            )

        # Chain dispatched sub-actions
        current_ps = result.new_player_state
        current_ds = result.new_dungeon_state
        all_msgs   = list(result.messages)

        for (sub_id, sub_overrides) in result.dispatched_actions:
            sub_result = self.dispatch(
                sub_id,
                player_state   = current_ps,
                dungeon_state  = current_ds,
                location_state = location_state,
                context_overrides = sub_overrides,
            )
            current_ps = sub_result.new_player_state
            current_ds = sub_result.new_dungeon_state
            all_msgs.extend(sub_result.messages)

        return ActionResult(
            new_player_state  = current_ps,
            new_dungeon_state = current_ds,
            messages          = all_msgs,
            dispatched_actions= [],   # already chained
        )
