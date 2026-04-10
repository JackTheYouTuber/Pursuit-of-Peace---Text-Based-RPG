"""
state.py — the single source of truth for game state.

Holds player_state dict and dungeon_state dict.
Does not validate. Does not decide. Just stores and serves.
"""
from typing import Dict, Optional


class State:
    def __init__(self, defaults: Dict):
        self._player: Dict        = dict(defaults)
        self._dungeon: Optional[Dict] = None

    # -- Player ---------------------------------------------------------
    def player(self) -> Dict:          return self._player
    def set_player(self, p: Dict):     self._player = dict(p)
    def reset_player(self, defaults: Dict): self._player = dict(defaults)

    # -- Dungeon --------------------------------------------------------
    def dungeon(self) -> Optional[Dict]:   return self._dungeon
    def set_dungeon(self, d: Optional[Dict]): self._dungeon = d
    def clear_dungeon(self):               self._dungeon = None
