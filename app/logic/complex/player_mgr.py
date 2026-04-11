"""
PlayerMgr — controller exclusively for the player entity.

Enemies do NOT use this manager. They use EntityMgr.

The player is a special entity: it has city services, taxes, year
tracking, and a human giving it orders. None of that applies to enemies.

Where the player and enemies share operations (equip, heal, use item),
both managers call the same simples independently — the simples are the
shared ground. There is no cross-delegation between managers.

Validates all orders. Calls simples directly. Returns (new_state, message).
Never raises.
"""
import random
from typing import Dict, List, Optional, Tuple

from app.logic.simple.heal_entity          import heal_entity
from app.logic.simple.damage_entity        import damage_entity
from app.logic.simple.apply_buff           import apply_buff
from app.logic.simple.remove_buff          import remove_buff
from app.logic.simple.tick_buffs           import tick_buffs
from app.logic.simple.expire_run_buffs     import expire_run_buffs
from app.logic.simple.add_item             import add_item
from app.logic.simple.remove_item          import remove_item
from app.logic.simple.add_gold             import add_gold
from app.logic.simple.remove_gold          import remove_gold
from app.logic.simple.decay_durability     import decay_durability
from app.logic.simple.resolve_equip        import resolve_equip
from app.logic.simple.resolve_unequip      import resolve_unequip
from app.logic.simple.apply_consumable     import apply_consumable
from app.logic.simple.get_weapon_bonus     import get_weapon_bonus
from app.logic.simple.get_armor_defense    import get_armor_defense
from app.logic.simple.get_buff_bonus       import get_buff_bonus
from app.logic.simple.get_buff_summary     import get_buff_summary
from app.logic.simple.get_effective_max_hp import get_effective_max_hp
from app.logic.simple.is_alive             import is_alive
from app.logic.simple.hp_ratio             import hp_ratio
from app.logic.simple.set_year             import set_year


class PlayerMgr:
    """Manages the player entity — body operations and city services."""

    def __init__(self, item_loader, lore_loader, config_loader):
        self._items  = item_loader
        self._lore   = lore_loader
        self._prices = config_loader.prices()

    # ── HP (same simples as EntityMgr, called independently) ──────────

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

    # ── Equipment ─────────────────────────────────────────────────────

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

    # ── Durability ────────────────────────────────────────────────────

    def decay(self, state: Dict, slot: str) -> Tuple[Dict, bool]:
        """Reduce slot durability by 1. Auto-nulls slot on break."""
        s, broke = decay_durability(state, slot)
        if broke:
            s[slot] = None
        return s, broke

    # ── Inventory ─────────────────────────────────────────────────────

    def give_item(self, state: Dict, item_id: str) -> Dict:
        return add_item(state, item_id)

    def take_item(self, state: Dict, item_id: str) -> Tuple[Dict, bool]:
        return remove_item(state, item_id)

    # ── Consumable use ────────────────────────────────────────────────

    def use_item(self, state: Dict, item_id: str) -> Tuple[Dict, str]:
        if item_id not in state.get("inventory", []):
            return state, "You don't have that item."
        item = self._items.get(item_id)
        if item is None:
            return state, f"Unknown item: {item_id}"
        if item.get("type") != "consumable":
            return state, f"{item.get('name', item_id)} isn't usable — try Equip."
        s, _ = remove_item(state, item_id)
        s, msg, _ = apply_consumable(s, item.get("name", item_id), item.get("effect") or "")
        return s, msg

    # ── Buff lifecycle ─────────────────────────────────────────────────

    def add_buff(self, state: Dict, buff: Dict) -> Dict:
        return apply_buff(state, buff)

    def remove_buff(self, state: Dict, buff_id: str) -> Dict:
        return remove_buff(state, buff_id)

    def tick_buffs(self, state: Dict) -> Tuple[Dict, List[str]]:
        return tick_buffs(state)

    def expire_run_buffs(self, state: Dict) -> Tuple[Dict, List[str]]:
        return expire_run_buffs(state)

    # ── Stat queries ──────────────────────────────────────────────────

    def damage_bonus(self, state: Dict) -> int:
        return get_buff_bonus(state, "damage_bonus")

    def defense_bonus(self, state: Dict) -> int:
        return get_buff_bonus(state, "defense_bonus")

    def max_hp_bonus(self, state: Dict) -> int:
        return get_buff_bonus(state, "max_hp")

    def buff_summary(self, state: Dict) -> str:
        return get_buff_summary(state)

    # ── Economy ───────────────────────────────────────────────────────

    def spend_gold(self, state: Dict, amount: int) -> Tuple[Dict, bool]:
        """Deduct gold if affordable. Returns (new_state, success)."""
        if state.get("gold", 0) < amount:
            return state, False
        s, _ = remove_gold(state, amount)
        return s, True

    def earn_gold(self, state: Dict, amount: int) -> Dict:
        s, _ = add_gold(state, amount)
        return s

    # ── City services (player-exclusive) ──────────────────────────────

    def rest(self, state: Dict) -> Tuple[Dict, str]:
        cost = self._prices.get("rest", 10)
        s, ok = self.spend_gold(state, cost)
        if not ok:
            return state, f"You need {cost}g to rest."
        s["hp"] = get_effective_max_hp(s)
        return s, f"You rest. HP restored. ({cost}g)"

    def take_bath(self, state: Dict) -> Tuple[Dict, str]:
        cost = self._prices.get("bath", 15)
        s, ok = self.spend_gold(state, cost)
        if not ok:
            return state, f"You need {cost}g for a bath."
        buff = {"id": "refreshed", "label": "Refreshed",
                "stat_mods": {"max_hp": 5}, "duration": "one_run"}
        s = apply_buff(s, buff)
        return s, f"You bathe. Max HP +5 for this run. ({cost}g)"

    def fish(self, state: Dict) -> Tuple[Dict, str]:
        pool = self._items.by_source("fishing")
        if not pool:
            return state, "Nothing bites today."
        caught = random.choice(pool)
        s = add_item(state, caught["id"])
        return s, f"You catch: {caught['name']}."

    def pay_taxes(self, state: Dict) -> Tuple[Dict, str]:
        if state.get("tax_paid"):
            return state, "Taxes already paid this year."
        tax = self._prices.get("tax", 100)
        s, ok = self.spend_gold(state, tax)
        if not ok:
            return state, f"You need {tax}g to pay taxes."
        s["tax_paid"] = True
        return s, f"Taxes paid. ({tax}g)"

    def view_debt(self, state: Dict) -> str:
        tax  = self._prices.get("tax", 100)
        year = state.get("year", 1)
        if state.get("tax_paid"):
            return f"Year {year} taxes: PAID."
        return f"Year {year} taxes: {tax}g due at year end."

    def hear_rumors(self, state: Dict) -> Tuple[Dict, str]:
        rumors = self._lore.by_type("tavern", "rumor")
        if not rumors:
            return state, "The tavern is quiet tonight."
        return state, random.choice(rumors).get("text", "")

    # ── Buy / sell (player-exclusive economy) ─────────────────────────

    def buy_item(self, state: Dict, item_id: str) -> Tuple[Dict, str]:
        item = self._items.get(item_id)
        if item is None:
            return state, f"Unknown item: {item_id}"
        price = item.get("value", 0)
        s, ok = self.spend_gold(state, price)
        if not ok:
            return state, f"Need {price}g (you have {state.get('gold', 0)}g)."
        s = add_item(s, item_id)
        return s, f"Bought {item['name']} for {price}g."

    def sell_item(self, state: Dict, item_id: str) -> Tuple[Dict, str]:
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

    def repair(self, state: Dict, slot: str) -> Tuple[Dict, str]:
        if slot not in ("equipped_weapon", "equipped_armor"):
            return state, "Invalid slot."
        equipped = state.get(slot)
        if not equipped:
            return state, "Nothing equipped there."
        cur = equipped.get("current_durability", 0)
        mx  = equipped.get("max_durability", 1)
        if cur >= mx:
            return state, "Already at full durability."
        cost = (mx - cur) * self._prices.get("repair_per_point", 5)
        s, ok = self.spend_gold(state, cost)
        if not ok:
            return state, f"Need {cost}g to repair (you have {state.get('gold', 0)}g)."
        eq = dict(s[slot])
        eq["current_durability"] = mx
        s[slot] = eq
        return s, f"Repaired {equipped.get('item', {}).get('name', 'item')} for {cost}g."

    # ── Year cycle (player-exclusive) ─────────────────────────────────

    def year_rollover(self, state: Dict) -> Tuple[Optional[Dict], str]:
        if not state.get("tax_paid"):
            return None, ("Taxes unpaid. The guards escort you beyond the gates. "
                          "GAME OVER — Exiled for tax debt.")
        s = set_year(state, state.get("year", 1) + 1)
        return s, f"A new year begins. Year {s['year']} tax is now due."
