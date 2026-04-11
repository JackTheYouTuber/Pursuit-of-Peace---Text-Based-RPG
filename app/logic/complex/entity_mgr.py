"""
EntityMgr — controller for non-player entities (enemies, companions).

The player does NOT use this manager. Player uses PlayerMgr.

Both managers call the same simples when they need the same operations —
that is how shared functionality works. The simples are the common ground.
The managers are separate controllers for separate entity types.

Validates orders. Calls simples. Returns (new_state, message).
Never raises. An impossible order returns unchanged state + reason.
"""
import random
from typing import Dict, List, Optional, Tuple

from app.logic.simple.heal_entity       import heal_entity
from app.logic.simple.damage_entity     import damage_entity
from app.logic.simple.apply_buff        import apply_buff
from app.logic.simple.remove_buff       import remove_buff
from app.logic.simple.tick_buffs        import tick_buffs
from app.logic.simple.expire_run_buffs  import expire_run_buffs
from app.logic.simple.add_item          import add_item
from app.logic.simple.remove_item       import remove_item
from app.logic.simple.decay_durability  import decay_durability
from app.logic.simple.resolve_equip     import resolve_equip
from app.logic.simple.resolve_unequip   import resolve_unequip
from app.logic.simple.apply_consumable  import apply_consumable
from app.logic.simple.get_weapon_bonus  import get_weapon_bonus
from app.logic.simple.get_armor_defense import get_armor_defense
from app.logic.simple.get_buff_bonus    import get_buff_bonus
from app.logic.simple.get_buff_summary  import get_buff_summary
from app.logic.simple.get_effective_max_hp import get_effective_max_hp
from app.logic.simple.is_alive          import is_alive
from app.logic.simple.hp_ratio          import hp_ratio


class EntityMgr:
    """Manages the body of a non-player entity."""

    def __init__(self, item_loader):
        self._items = item_loader

    # -- HP -------------------------------------------------------------

    def heal(self, state: Dict, amount: int) -> Tuple[Dict, int]:
        return heal_entity(state, amount)

    def damage(self, state: Dict, amount: int) -> Tuple[Dict, bool]:
        return damage_entity(state, amount)

    def is_alive(self, state: Dict) -> bool:
        return is_alive(state)

    def hp_ratio(self, state: Dict) -> float:
        return hp_ratio(state)

    def effective_max_hp(self, state: Dict) -> int:
        return get_effective_max_hp(state)

    # -- Equipment ------------------------------------------------------

    def equip(self, state: Dict, item_id: str) -> Tuple[Dict, str]:
        item = self._items.get(item_id)
        if item is None:
            return state, f"Unknown item: {item_id}"
        s, msg, _ = resolve_equip(state, item_id, item)
        return s, msg

    def unequip(self, state: Dict, slot: str) -> Tuple[Dict, str]:
        s, msg, _ = resolve_unequip(state, slot)
        return s, msg

    def weapon_bonus(self, state: Dict) -> Tuple[int, str]:
        return get_weapon_bonus(state)

    def armor_defense(self, state: Dict) -> Tuple[int, str]:
        return get_armor_defense(state)

    # -- Durability -----------------------------------------------------

    def decay(self, state: Dict, slot: str) -> Tuple[Dict, bool]:
        """Reduce slot durability by 1. Auto-nulls slot on break."""
        s, broke = decay_durability(state, slot)
        if broke:
            s[slot] = None
        return s, broke

    # -- Inventory ------------------------------------------------------

    def give_item(self, state: Dict, item_id: str) -> Dict:
        return add_item(state, item_id)

    def take_item(self, state: Dict, item_id: str) -> Tuple[Dict, bool]:
        return remove_item(state, item_id)

    # -- Consumable use -------------------------------------------------

    def use_item(self, state: Dict, item_id: str) -> Tuple[Dict, str]:
        if item_id not in state.get("inventory", []):
            return state, "Item not in inventory."
        item = self._items.get(item_id)
        if item is None:
            return state, f"Unknown item: {item_id}"
        if item.get("type") != "consumable":
            return state, f"{item.get('name', item_id)} is not usable."
        s, _ = remove_item(state, item_id)
        s, msg, _ = apply_consumable(s, item.get("name", item_id), item.get("effect") or "")
        return s, msg

    # -- Buff lifecycle -------------------------------------------------

    def add_buff(self, state: Dict, buff: Dict) -> Dict:
        return apply_buff(state, buff)

    def remove_buff(self, state: Dict, buff_id: str) -> Dict:
        return remove_buff(state, buff_id)

    def tick_buffs(self, state: Dict) -> Tuple[Dict, List[str]]:
        return tick_buffs(state)

    def expire_run_buffs(self, state: Dict) -> Tuple[Dict, List[str]]:
        return expire_run_buffs(state)

    # -- Stat queries ---------------------------------------------------

    def damage_bonus(self, state: Dict) -> int:
        return get_buff_bonus(state, "damage_bonus")

    def defense_bonus(self, state: Dict) -> int:
        return get_buff_bonus(state, "defense_bonus")

    def max_hp_bonus(self, state: Dict) -> int:
        return get_buff_bonus(state, "max_hp")

    def buff_summary(self, state: Dict) -> str:
        return get_buff_summary(state)

    # -- Entity state builder -------------------------------------------

    @staticmethod
    def from_def(enemy_def: Dict) -> Dict:
        """
        Build a fresh entity state dict from an enemies.json definition.
        Enemies get the same state shape as the player — EntityMgr and
        PlayerMgr both operate on identical state dicts.
        """
        return {
            "hp":              enemy_def.get("hp", 10),
            "max_hp":          enemy_def.get("hp", 10),
            "buffs":           [],
            "inventory":       [],
            "equipped_weapon": None,
            "equipped_armor":  None,
        }
