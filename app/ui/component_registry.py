"""Registry of component classes for the UI builder."""
from tkinter import ttk

from app.ui.components.basic.text_display import TextDisplay
from app.ui.components.basic.menu_list import MenuList
from app.ui.components.basic.stat_bar import StatBar
from app.ui.components.complex.location_panel import LocationPanel
from app.ui.components.complex.combat_panel import CombatPanel
from app.ui.components.complex.inventory_panel import InventoryPanel
from app.ui.components.complex.lore_panel import LorePanel

COMPONENT_REGISTRY = {
    "TextDisplay": TextDisplay,
    "MenuList": MenuList,
    "StatBar": StatBar,
    "LocationPanel": LocationPanel,
    "CombatPanel": CombatPanel,
    "InventoryPanel": InventoryPanel,
    "LorePanel": LorePanel,
    "Frame": ttk.Frame,
}

def get_component_class(comp_type: str):
    return COMPONENT_REGISTRY.get(comp_type)