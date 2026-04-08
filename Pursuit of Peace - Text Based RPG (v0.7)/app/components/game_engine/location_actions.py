# app/components/game_engine/location_actions.py
import random
from typing import Dict, Tuple, Optional

class LocationActions:
    """Handle service actions in city locations (rest, rumors, bath, fishing, tax)."""

    def __init__(self, data_loader, location_manager, logger=None):
        self._loader = data_loader
        self._location_mgr = location_manager
        self._logger = logger
        self._prices = self._loader.get_prices()
        self._services = self._loader.get_services()

    def rest(self, player_state: Dict) -> Tuple[Dict, str]:
        state = dict(player_state)
        cost = self._prices.get("rest", 10)
        if state.get("gold", 0) < cost:
            return state, f"You cannot afford the {cost} gold to rest here."
        state["gold"] -= cost
        state["hp"] = state.get("max_hp", 20)
        if self._logger:
            self._logger.data("rest", {"gold_spent": cost})
        return state, f"You rest through the night. ({cost} gold spent. HP fully restored.)"

    def hear_rumors(self, player_state: Dict) -> Tuple[Dict, str]:
        lore_entries = self._loader.get_lore("tavern")
        rumors = [e for e in lore_entries if e.get("type") == "rumor"]
        if not rumors:
            return player_state, "The tavern is quiet tonight. No one has anything to say."
        rumor = random.choice(rumors)
        return player_state, rumor.get("text", "")

    def take_bath(self, player_state: Dict) -> Tuple[Dict, str]:
        state = dict(player_state)
        cost = self._prices.get("bath", 15)
        if state.get("gold", 0) < cost:
            return state, f"You cannot afford the {cost} gold for a bath."
        state["gold"] -= cost
        bath_service = self._services.get("public_bath", {})
        buff = bath_service.get("bath_buff", {})
        if buff:
            buffs = list(state.get("buffs", []))
            buffs.append(dict(buff))
            state["buffs"] = buffs
        if self._logger:
            self._logger.data("bath", {"gold_spent": cost, "buff": buff})
        return state, (f"You soak in the warm water. ({cost} gold spent. "
                       f"Gained buff: {buff.get('label', 'Refreshed')}.)")

    def go_fishing(self, player_state: Dict) -> Tuple[Dict, str]:
        state = dict(player_state)
        fishing_items = [item for item in self._loader.get_all_items() if item.get("source") == "fishing"]
        if not fishing_items:
            return state, "You wait patiently, but nothing bites today."
        caught = random.choice(fishing_items)
        inventory = list(state.get("inventory", []))
        inventory.append(caught["id"])
        state["inventory"] = inventory
        if self._logger:
            self._logger.data("fishing", {"item_caught": caught["id"]})
        return state, f"You cast your line and pull out: {caught['name']}."

    def pay_taxes(self, player_state: Dict) -> Tuple[Dict, str]:
        state = dict(player_state)
        if state.get("tax_paid", False):
            return state, "You have already paid your taxes this year."
        tax = self._prices.get("tax", 100)
        if state.get("gold", 0) < tax:
            return state, (f"You cannot afford the {tax} gold tax. "
                           "Return before year end or face exile.")
        state["gold"] -= tax
        state["tax_paid"] = True
        if self._logger:
            self._logger.data("tax_paid", {"amount": tax})
        return state, f"Taxes paid. ({tax} gold. You are clear until the next year.)"

    def view_debt(self, player_state: Dict) -> str:
        tax = self._prices.get("tax", 100)
        paid = player_state.get("tax_paid", False)
        year = player_state.get("year", 1)
        if paid:
            return f"Year {year} taxes paid. You owe nothing further."
        return f"Year {year} taxes outstanding: {tax} gold due at year end."

    def process_year_rollover(self, player_state: Dict) -> Tuple[Optional[Dict], str]:
        state = dict(player_state)
        if not state.get("tax_paid", False):
            if self._logger:
                self._logger.data("exile_triggered", {"year": state.get("year", 1)})
            return None, ("The city guards arrive at dawn. Your taxes were unpaid. "
                          "You are escorted beyond the gates and the doors are barred behind you. "
                          "GAME OVER — Exiled for tax debt.")
        state["year"] = state.get("year", 1) + 1
        state["tax_paid"] = False
        if self._logger:
            self._logger.data("year_rollover", {"new_year": state["year"]})
        return state, f"A new year begins. Year {state['year']} tax is now due."

    def enter_dungeon(self, player_state: Dict, dungeon_state_generator) -> Tuple[Dict, Dict]:
        state = dict(player_state)
        dungeon_state = dungeon_state_generator()
        state["current_location_id"] = "dungeon_entrance"
        if self._logger:
            self._logger.info(f"Dungeon entered. {dungeon_state['total_rooms']} rooms generated.")
        return state, dungeon_state