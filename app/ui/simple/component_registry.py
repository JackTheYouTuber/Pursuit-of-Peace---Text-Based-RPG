"""Registry of component classes for the UI builder."""
import tkinter as tk
from tkinter import ttk

from app.ui.simple.basic.text_display import TextDisplay
from app.ui.simple.basic.menu_list import MenuList
from app.ui.simple.basic.stat_bar import StatBar
from app.ui.simple.panels.location_panel import LocationPanel
from app.ui.simple.panels.combat_panel import CombatPanel
from app.ui.simple.panels.inventory_panel import InventoryPanel
from app.ui.simple.panels.lore_panel import LorePanel

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