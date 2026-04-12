"""
action_types.py — core AAD data structures.

ActionContext  : frozen snapshot passed into every resolver.
ActionResult   : what every resolver returns.

Resolvers must never mutate their input ActionContext.
They produce a new ActionResult containing updated state dicts.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class ActionContext:
    """Immutable bag of everything a resolver might need."""
    player_state:   Dict        = field(default_factory=dict)
    dungeon_state:  Optional[Dict] = None
    location_state: Optional[Dict] = None  # current services.json entry
    entity_id:      str         = "0"      # "0" = player; enemy id string for NPCs
    quantity:       int         = 0
    reference:      Any         = None     # item_id, buff_dict, etc.
    action_id:      str         = ""
    data_registry:  Any         = None     # DataRegistry (read-only)


@dataclass
class ActionResult:
    """Mutable result produced by a resolver."""
    new_player_state:  Dict                         = field(default_factory=dict)
    new_dungeon_state: Optional[Dict]               = None
    messages:          List[str]                    = field(default_factory=list)
    # (action_id, context_override_dict) — dispatcher will chain these
    dispatched_actions: List[Tuple[str, Dict]]      = field(default_factory=list)
