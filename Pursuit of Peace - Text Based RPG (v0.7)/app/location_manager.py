import random


class LocationManager:
    """
    Manages player navigation between city locations and dungeon entry.

    Responsibilities:
    - Track current_location_id in player state.
    - Resolve available actions from services data (no hardcoding).
    - Dispatch service actions: rest, rumor, bath, fishing, tax, exile check.
    - Delegate dungeon generation to DungeonManager.
    - Keep location logic and lore completely separate.
    """

    def __init__(self, data_loader, dungeon_manager, logger=None):
        self._loader = data_loader
        self._dungeon = dungeon_manager
        self._logger = logger

        self._services = self._loader.get_services()
        self._prices = self._loader.get_prices()
        self._locations = {loc["id"]: loc for loc in self._loader.get_all_locations()}

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def navigate_to(self, player_state, location_id):
        """
        Update player's current_location_id.
        Returns updated player_state dict (does not mutate the original).
        Raises ValueError if location_id is unknown.
        """
        if location_id not in self._locations:
            raise ValueError(f"Unknown location id: '{location_id}'")

        state = dict(player_state)
        state["current_location_id"] = location_id

        if self._logger:
            self._logger.info(f"Player navigated to: {location_id}")

        return state

    def get_location_actions(self, location_id):
        """
        Return action id list for a location from services data.
        Never hardcoded here — always driven by services.json.
        """
        loc_service = self._services.get(location_id, {})
        return list(loc_service.get("actions", []))

    def get_location_meta(self, location_id):
        """Return the raw location dict from locations.json."""
        return dict(self._locations.get(location_id, {}))

    # ------------------------------------------------------------------
    # Service actions
    # ------------------------------------------------------------------

    def action_rest(self, player_state):
        """
        Tavern rest: costs gold, restores hp.
        Returns (updated_state, result_message).
        """
        state = dict(player_state)
        cost = self._prices.get("rest", 10)

        if state.get("gold", 0) < cost:
            return state, f"You cannot afford the {cost} gold to rest here."

        state["gold"] -= cost
        state["hp"] = state.get("max_hp", 20)

        if self._logger:
            self._logger.data("rest", {"gold_spent": cost})

        return state, f"You rest through the night. ({cost} gold spent. HP fully restored.)"

    def action_hear_rumor(self, player_state):
        """
        Return a random rumor lore entry text from data/lore/tavern.json.
        """
        lore_entries = self._loader.get_lore("tavern")
        rumors = [e for e in lore_entries if e.get("type") == "rumor"]

        if not rumors:
            return player_state, "The tavern is quiet tonight. No one has anything to say."

        rumor = random.choice(rumors)
        return player_state, rumor.get("text", "")

    def action_take_bath(self, player_state):
        """
        Public Bath: costs gold, grants one-run stat buff from services.json.
        Returns (updated_state, result_message).
        """
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

        return state, (
            f"You soak in the warm water. ({cost} gold spent. "
            f"Gained buff: {buff.get('label', 'Refreshed')}.)"
        )

    def action_go_fishing(self, player_state):
        """
        The River fishing: random draw from items where source == 'fishing'.
        Returns (updated_state, result_message).
        """
        state = dict(player_state)
        fishing_items = [
            item for item in self._loader.get_all_items()
            if item.get("source") == "fishing"
        ]

        if not fishing_items:
            return state, "You wait patiently, but nothing bites today."

        caught = random.choice(fishing_items)
        inventory = list(state.get("inventory", []))
        inventory.append(caught["id"])
        state["inventory"] = inventory

        if self._logger:
            self._logger.data("fishing", {"item_caught": caught["id"]})

        return state, f"You cast your line and pull out: {caught['name']}."

    def action_pay_taxes(self, player_state):
        """
        City Hall: pay annual tax. Returns (updated_state, result_message).
        """
        state = dict(player_state)

        if state.get("tax_paid", False):
            return state, "You have already paid your taxes this year."

        tax = self._prices.get("tax", 100)

        if state.get("gold", 0) < tax:
            return state, (
                f"You cannot afford the {tax} gold tax. "
                "Return before year end or face exile."
            )

        state["gold"] -= tax
        state["tax_paid"] = True

        if self._logger:
            self._logger.data("tax_paid", {"amount": tax})

        return state, f"Taxes paid. ({tax} gold. You are clear until the next year.)"

    def get_tax_debt_status(self, player_state):
        """Return a description of current tax obligation."""
        tax = self._prices.get("tax", 100)
        paid = player_state.get("tax_paid", False)
        year = player_state.get("year", 1)

        if paid:
            return f"Year {year} taxes paid. You owe nothing further."
        return f"Year {year} taxes outstanding: {tax} gold due at year end."

    # ------------------------------------------------------------------
    # Year rollover and exile
    # ------------------------------------------------------------------

    def process_year_rollover(self, player_state):
        """
        Called by the App at year end.
        If tax_paid is false: triggers exile (returns None, exile_message).
        If tax_paid is true: increments year, resets tax_paid, returns (state, message).
        """
        state = dict(player_state)

        if not state.get("tax_paid", False):
            if self._logger:
                self._logger.data("exile_triggered", {"year": state.get("year", 1)})
            return None, (
                "The city guards arrive at dawn. Your taxes were unpaid. "
                "You are escorted beyond the gates and the doors are barred behind you. "
                "GAME OVER — Exiled for tax debt."
            )

        state["year"] = state.get("year", 1) + 1
        state["tax_paid"] = False

        if self._logger:
            self._logger.data("year_rollover", {"new_year": state["year"]})

        return state, f"A new year begins. Year {state['year']} tax is now due."

    # ------------------------------------------------------------------
    # Dungeon entry
    # ------------------------------------------------------------------

    def enter_dungeon(self, player_state):
        """
        Generate a new dungeon run and set location to dungeon.
        Returns (updated_state, dungeon_state).
        """
        state = dict(player_state)
        dungeon_state = self._dungeon.generate()
        state["current_location_id"] = "dungeon_entrance"

        if self._logger:
            self._logger.info(
                f"Dungeon entered. {dungeon_state['total_rooms']} rooms generated."
            )

        return state, dungeon_state

    def exit_dungeon(self, player_state):
        """Return player to city entrance after leaving dungeon."""
        return self.navigate_to(player_state, "city_entrance")
