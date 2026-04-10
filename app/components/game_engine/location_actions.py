# app/components/game_engine/location_actions.py
"""
LocationActions — handles all service/city actions plus item management.

Tier 1: rest, hear_rumors, take_bath, go_fishing, pay_taxes, view_debt,
        process_year_rollover, enter_dungeon.
Tier 2: use_item (consumables), buff on bath/rest.
Tier 3: equip_item, unequip_item, repair_equipment.
Tier 4: buy_item, sell_item.
"""
import random
from typing import Dict, Tuple, Optional, List

from app.components.game_engine.effect_resolver import EffectResolver
from app.components.game_engine.buff_system import BuffSystem


class LocationActions:
    def __init__(self, data_loader, location_manager, logger=None):
        self._loader = data_loader
        self._location_mgr = location_manager
        self._logger = logger
        self._prices = self._loader.get_prices()
        self._services = self._loader.get_services()
        self._effect_resolver = EffectResolver(logger)
        self._buff_sys = BuffSystem(logger)

    # ══════════════════════════════════════════════════════════════════
    # TIER 1 — basic city actions
    # ══════════════════════════════════════════════════════════════════

    def rest(self, player_state: Dict) -> Tuple[Dict, str]:
        state = dict(player_state)
        cost = self._prices.get("rest", 10)
        if state.get("gold", 0) < cost:
            return state, f"You cannot afford the {cost} gold to rest here."
        state["gold"] -= cost
        max_hp = state.get("max_hp", 20) + self._buff_sys.get_max_hp_bonus(state)
        state["hp"] = max_hp
        # Tick one_run buffs don't expire on rest (only dungeon exit)
        if self._logger:
            self._logger.data("rest", {"gold_spent": cost})
        return state, f"You rest through the night. ({cost}g spent. HP fully restored.)"

    def hear_rumors(self, player_state: Dict) -> Tuple[Dict, str]:
        lore_entries = self._loader.get_lore("tavern")
        rumors = [e for e in lore_entries if e.get("type") == "rumor"]
        if not rumors:
            return player_state, "The tavern is quiet tonight."
        return player_state, random.choice(rumors).get("text", "")

    def take_bath(self, player_state: Dict) -> Tuple[Dict, str]:
        state = dict(player_state)
        cost = self._prices.get("bath", 15)
        if state.get("gold", 0) < cost:
            return state, f"You cannot afford the {cost} gold for a bath."
        state["gold"] -= cost
        buff = {
            "id": "refreshed",
            "label": "Refreshed",
            "stat_mods": {"max_hp": 5},
            "duration": "one_run",
        }
        state = self._buff_sys.add_buff(state, buff)
        if self._logger:
            self._logger.data("bath", {"gold_spent": cost})
        return state, f"You soak in the warm water. ({cost}g. Max HP +5 for this dungeon run.)"

    def go_fishing(self, player_state: Dict) -> Tuple[Dict, str]:
        state = dict(player_state)
        fishing_items = [i for i in self._loader.get_all_items() if i.get("source") == "fishing"]
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
        return state, f"Taxes paid. ({tax}g. You are clear until next year.)"

    def view_debt(self, player_state: Dict) -> str:
        tax = self._prices.get("tax", 100)
        paid = player_state.get("tax_paid", False)
        year = player_state.get("year", 1)
        if paid:
            return f"Year {year} taxes: PAID."
        return f"Year {year} taxes: {tax}g outstanding — due at year end."

    def process_year_rollover(self, player_state: Dict) -> Tuple[Optional[Dict], str]:
        state = dict(player_state)
        if not state.get("tax_paid", False):
            if self._logger:
                self._logger.data("exile_triggered", {"year": state.get("year", 1)})
            return None, ("The city guards arrive at dawn. Your taxes were unpaid. "
                          "You are escorted beyond the gates. "
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
            self._logger.info(f"Dungeon entered. {dungeon_state['total_rooms']} rooms.")
        return state, dungeon_state

    # ══════════════════════════════════════════════════════════════════
    # TIER 2 — consumable use
    # ══════════════════════════════════════════════════════════════════

    def use_item(self, player_state: Dict, item_id: str) -> Tuple[Dict, str]:
        """Use a consumable item from inventory. Removes it on use."""
        state = dict(player_state)
        inventory = list(state.get("inventory", []))
        if item_id not in inventory:
            return state, "You don't have that item."
        try:
            item = self._loader.get_item(item_id)
        except ValueError:
            return state, f"Unknown item: {item_id}"
        if item.get("type") != "consumable":
            return state, f"{item.get('name', item_id)} cannot be used — try Equip instead."
        # Apply effect
        state, msg = self._effect_resolver.apply_item_effect(state, item)
        # Remove from inventory (consume)
        inventory.remove(item_id)
        state["inventory"] = inventory
        if self._logger:
            self._logger.data("item_used", {"item": item_id})
        return state, msg

    # ══════════════════════════════════════════════════════════════════
    # TIER 3 — equipment management
    # ══════════════════════════════════════════════════════════════════

    def equip_item(self, player_state: Dict, item_id: str) -> Tuple[Dict, str]:
        """Equip a weapon or armor from inventory."""
        state = dict(player_state)
        inventory = list(state.get("inventory", []))
        if item_id not in inventory:
            return state, "You don't have that item."
        try:
            item = self._loader.get_item(item_id)
        except ValueError:
            return state, f"Unknown item: {item_id}"

        item_type = item.get("type")
        if item_type not in ("weapon", "armor"):
            return state, f"{item.get('name', item_id)} cannot be equipped."

        slot = "equipped_weapon" if item_type == "weapon" else "equipped_armor"

        # Unequip current item into inventory
        current = state.get(slot)
        if current:
            old_id = current.get("item_id")
            inventory.append(old_id)

        # Equip new item
        inventory.remove(item_id)
        state["inventory"] = inventory
        state[slot] = {
            "item_id": item_id,
            "item": item,
            "current_durability": item.get("durability", 30),
            "max_durability": item.get("durability", 30),
        }

        stat_bonus = item.get("stat_bonus", {})
        bonus_str = ""
        if "damage" in stat_bonus:
            bonus_str = f" (+{stat_bonus['damage']} damage)"
        elif "defense" in stat_bonus:
            bonus_str = f" (+{stat_bonus['defense']} defense)"

        if self._logger:
            self._logger.data("equip", {"item": item_id, "slot": slot})
        return state, f"Equipped {item.get('name', item_id)}{bonus_str}."

    def unequip_item(self, player_state: Dict, slot: str) -> Tuple[Dict, str]:
        """Unequip weapon or armor, returning it to inventory."""
        if slot not in ("equipped_weapon", "equipped_armor"):
            return player_state, "Invalid slot."
        state = dict(player_state)
        current = state.get(slot)
        if not current:
            return state, "Nothing equipped in that slot."
        item_id = current.get("item_id")
        inventory = list(state.get("inventory", []))
        inventory.append(item_id)
        state["inventory"] = inventory
        state[slot] = None
        item_name = current.get("item", {}).get("name", item_id)
        if self._logger:
            self._logger.data("unequip", {"item": item_id, "slot": slot})
        return state, f"Unequipped {item_name}."

    def repair_equipment(self, player_state: Dict, slot: str) -> Tuple[Dict, str]:
        """Repair equipped weapon or armor at the blacksmith."""
        if slot not in ("equipped_weapon", "equipped_armor"):
            return player_state, "Invalid slot."
        state = dict(player_state)
        equipped = state.get(slot)
        if not equipped:
            return state, "Nothing equipped in that slot."
        current_dur = equipped.get("current_durability", 0)
        max_dur = equipped.get("max_durability", 1)
        if current_dur >= max_dur:
            return state, "That item is already at full durability."
        damage = max_dur - current_dur
        repair_cost_per_point = self._prices.get("repair_per_point", 5)
        cost = damage * repair_cost_per_point
        if state.get("gold", 0) < cost:
            return state, f"Not enough gold. Repair costs {cost}g (you have {state.get('gold', 0)}g)."
        state["gold"] -= cost
        equipped["current_durability"] = max_dur
        item_name = equipped.get("item", {}).get("name", "item")
        if self._logger:
            self._logger.data("repair", {"item": equipped.get("item_id"), "cost": cost})
        return state, f"Repaired {item_name} to full. Cost: {cost}g."

    # ══════════════════════════════════════════════════════════════════
    # TIER 4 — buy / sell
    # ══════════════════════════════════════════════════════════════════

    def buy_item(self, player_state: Dict, item_id: str) -> Tuple[Dict, str]:
        """Buy an item from the current shop."""
        state = dict(player_state)
        try:
            item = self._loader.get_item(item_id)
        except ValueError:
            return state, f"Item not found: {item_id}"
        price = item.get("value", 0)
        if state.get("gold", 0) < price:
            return state, f"Not enough gold. {item.get('name', item_id)} costs {price}g."
        state["gold"] -= price
        inventory = list(state.get("inventory", []))
        inventory.append(item_id)
        state["inventory"] = inventory
        if self._logger:
            self._logger.data("buy", {"item": item_id, "price": price})
        return state, f"Purchased {item.get('name', item_id)} for {price}g."

    def sell_item(self, player_state: Dict, item_id: str) -> Tuple[Dict, str]:
        """Sell an item from inventory for 40% of its value."""
        state = dict(player_state)
        inventory = list(state.get("inventory", []))
        if item_id not in inventory:
            return state, "You don't have that item."
        # Cannot sell equipped items
        for slot in ("equipped_weapon", "equipped_armor"):
            eq = state.get(slot)
            if eq and eq.get("item_id") == item_id:
                return state, "That item is currently equipped. Unequip it first."
        try:
            item = self._loader.get_item(item_id)
        except ValueError:
            return state, f"Unknown item: {item_id}"
        sell_price = max(1, int(item.get("value", 0) * 0.4))
        inventory.remove(item_id)
        state["inventory"] = inventory
        state["gold"] = state.get("gold", 0) + sell_price
        if self._logger:
            self._logger.data("sell", {"item": item_id, "price": sell_price})
        return state, f"Sold {item.get('name', item_id)} for {sell_price}g."

    # ══════════════════════════════════════════════════════════════════
    # Helpers used by external systems
    # ══════════════════════════════════════════════════════════════════

    def get_equipped_weapon(self, player_state: Dict) -> Optional[Dict]:
        return player_state.get("equipped_weapon")

    def get_equipped_armor(self, player_state: Dict) -> Optional[Dict]:
        return player_state.get("equipped_armor")
