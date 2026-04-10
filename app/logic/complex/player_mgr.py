"""
PlayerMgr — middle management for city service actions.

Validates affordability. Coordinates Simples (remove_gold, heal_player,
add_item, set_year, apply_buff). Returns (new_state, message).
"""
import random
from typing import Dict, Optional, Tuple

from app.logic.simple.remove_gold   import remove_gold
from app.logic.simple.add_gold      import add_gold
from app.logic.simple.heal_player   import heal_player
from app.logic.simple.add_item      import add_item
from app.logic.simple.set_year      import set_year
from app.logic.simple.apply_buff    import apply_buff


class PlayerMgr:
    def __init__(self, item_loader, lore_loader, buff_mgr, config_loader):
        self._items  = item_loader
        self._lore   = lore_loader
        self._buffs  = buff_mgr
        self._prices = config_loader.prices()

    def rest(self, state: Dict) -> Tuple[Dict, str]:
        cost = self._prices.get("rest", 10)
        if state.get("gold", 0) < cost:
            return state, f"You need {cost}g to rest."
        s, _ = remove_gold(state, cost)
        max_hp = s.get("max_hp", 20) + self._buffs.max_hp_bonus(s)
        s["hp"] = max_hp
        return s, f"You rest. HP restored. ({cost}g)"

    def take_bath(self, state: Dict) -> Tuple[Dict, str]:
        cost = self._prices.get("bath", 15)
        if state.get("gold", 0) < cost:
            return state, f"You need {cost}g for a bath."
        s, _ = remove_gold(state, cost)
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
        if state.get("gold", 0) < tax:
            return state, f"You need {tax}g to pay taxes."
        s, _ = remove_gold(state, tax)
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

    def year_rollover(self, state: Dict) -> Tuple[Optional[Dict], str]:
        if not state.get("tax_paid"):
            return None, ("Taxes unpaid. The guards escort you beyond the gates. "
                          "GAME OVER — Exiled for tax debt.")
        s = set_year(state, state.get("year", 1) + 1)
        return s, f"A new year begins. Year {s['year']} tax is now due."
