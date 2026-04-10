"""
ItemMgr — middle management for inventory and equipment.

Validates orders (does the player own the item? is it equippable?).
Coordinates Simples (add_item, remove_item, equip_item, unequip_item, parse_effect).
Coordinates BuffMgr for consumable effects.
Returns (new_state, message). Never raises. Invalid orders return unchanged state + reason.
"""
from typing import Dict, Tuple

from app.logic.simple.add_item      import add_item
from app.logic.simple.remove_item   import remove_item
from app.logic.simple.equip_item    import equip_item as _equip
from app.logic.simple.unequip_item  import unequip_item as _unequip
from app.logic.simple.add_gold      import add_gold
from app.logic.simple.remove_gold   import remove_gold
from app.logic.simple.heal_player   import heal_player
from app.logic.simple.parse_effect  import parse_effect


class ItemMgr:
    def __init__(self, item_loader, buff_mgr, config_loader):
        self._items  = item_loader
        self._buffs  = buff_mgr
        self._prices = config_loader.prices()

    # -- Use ------------------------------------------------------------
    def use(self, state: Dict, item_id: str) -> Tuple[Dict, str]:
        if item_id not in state.get("inventory", []):
            return state, "You don't have that item."
        item = self._items.get(item_id)
        if item is None:
            return state, f"Unknown item: {item_id}"
        if item.get("type") != "consumable":
            return state, f"{item.get('name', item_id)} isn't usable — try Equip."

        effect_text = item.get("effect") or ""
        parsed = parse_effect(effect_text)
        s, _ = remove_item(state, item_id)

        if parsed is None:
            return s, f"Used {item.get('name', item_id)}. (No effect.)"

        if parsed.get("type") == "heal":
            amount = parsed["value"]
            s, gained = heal_player(s, amount)
            hp = s.get("hp", 0)
            max_hp = s.get("max_hp", 20) + self._buffs.max_hp_bonus(s)
            msg = f"Used {item['name']}. HP +{gained} ({hp}/{max_hp})."
            return s, msg

        s, msg = self._buffs.apply_effect(s, parsed)
        prefix = f"Used {item.get('name', item_id)}."
        return s, f"{prefix} {msg}".strip()

    # -- Equip / unequip ------------------------------------------------
    def equip(self, state: Dict, item_id: str) -> Tuple[Dict, str]:
        if item_id not in state.get("inventory", []):
            return state, "You don't have that item."
        item = self._items.get(item_id)
        if item is None:
            return state, f"Unknown item: {item_id}"
        itype = item.get("type")
        if itype not in ("weapon", "armor"):
            return state, f"{item.get('name', item_id)} cannot be equipped."

        slot = "equipped_weapon" if itype == "weapon" else "equipped_armor"
        s, _ = _equip(state, item_id, item, slot)

        bonus = item.get("stat_bonus", {})
        bonus_str = (f" (+{bonus['damage']} dmg)" if "damage" in bonus
                     else f" (+{bonus['defense']} def)" if "defense" in bonus else "")
        return s, f"Equipped {item['name']}{bonus_str}."

    def unequip(self, state: Dict, slot: str) -> Tuple[Dict, str]:
        if slot not in ("equipped_weapon", "equipped_armor"):
            return state, "Invalid equipment slot."
        equipped = state.get(slot)
        if not equipped:
            return state, "Nothing equipped there."
        name = equipped.get("item", {}).get("name", slot)
        s, _ = _unequip(state, slot)
        return s, f"Unequipped {name}."

    # -- Repair ---------------------------------------------------------
    def repair(self, state: Dict, slot: str) -> Tuple[Dict, str]:
        if slot not in ("equipped_weapon", "equipped_armor"):
            return state, "Invalid equipment slot."
        equipped = state.get(slot)
        if not equipped:
            return state, "Nothing equipped there."
        cur = equipped.get("current_durability", 0)
        mx  = equipped.get("max_durability", 1)
        if cur >= mx:
            return state, "Already at full durability."
        cost = (mx - cur) * self._prices.get("repair_per_point", 5)
        if state.get("gold", 0) < cost:
            return state, f"Need {cost}g to repair (you have {state.get('gold', 0)}g)."

        s, _ = remove_gold(state, cost)
        eq = dict(s[slot])
        eq["current_durability"] = mx
        s[slot] = eq
        return s, f"Repaired {equipped.get('item',{}).get('name','item')} for {cost}g."

    # -- Buy / sell -----------------------------------------------------
    def buy(self, state: Dict, item_id: str) -> Tuple[Dict, str]:
        item = self._items.get(item_id)
        if item is None:
            return state, f"Unknown item: {item_id}"
        price = item.get("value", 0)
        if state.get("gold", 0) < price:
            return state, f"Need {price}g (you have {state.get('gold',0)}g)."
        s, _ = remove_gold(state, price)
        s = add_item(s, item_id)
        return s, f"Bought {item['name']} for {price}g."

    def sell(self, state: Dict, item_id: str) -> Tuple[Dict, str]:
        if item_id not in state.get("inventory", []):
            return state, "You don't have that item."
        for slot in ("equipped_weapon", "equipped_armor"):
            eq = state.get(slot)
            if eq and eq.get("item_id") == item_id:
                return state, "Unequip it first."
        item = self._items.get(item_id)
        if item is None:
            return state, f"Unknown item: {item_id}"
        mult  = self._prices.get("sell_price_multiplier", 0.4)
        price = max(1, int(item.get("value", 0) * mult))
        s, _ = remove_item(state, item_id)
        s, _ = add_gold(s, price)
        return s, f"Sold {item['name']} for {price}g."
