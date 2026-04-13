# app/version.py
VERSION       = "1.0.0-stable"
VERSION_LABEL = f"v{VERSION}"

CHANGELOG = {
    "1.0.0-stable": [
        "BUG FIX: PyInstaller 'Unknown or unavailable action' — added app/paths.py with get_base_dir()/data_path().",
        "BUG FIX: do_combat_action ValueError in DevTools AuditRunner — corrected 4-value unpack.",
        "BUG FIX: shop.sell crash when item equipped — isinstance guard on equipment slot value.",
        "BUG FIX: get_weapon_bonus/get_armor_defense/resolve_unequip crash on non-dict slot values.",
        "BUG FIX: view_builder crash rendering inventory/combat/player-panel with malformed slots.",
        "BUG FIX: 31 unused imports removed (pyflakes clean); dead local variables removed.",
        "FEATURE: ProfileSelectorFrame — embedded profile UI, no Toplevel or popups.",
        "FEATURE: MainWindow.post_message() — inline message strip replaces all showinfo popups.",
        "FEATURE: MainWindow.show_confirm() — inline Yes/No bar replaces askyesno.",
        "FEATURE: Build Tool — UPX, architecture, custom dist folder, debug symbols, BUILD BOTH.",
        "FEATURE: JSON Workshop tab — visual form editor for items, enemies, services, actions.",
        "FEATURE: File Auditor tab — AST-based unused-file scanner with inline delete confirmation.",
        "FEATURE: DevTools ttk refactor — tk.Frame/Label/Entry/Button replaced with ttk equivalents.",
        "DOCS: ARCHITECTURE.md, CONTRIBUTING.md, DATA_SCHEMA.md, README.md, CHANGELOG.md rewritten.",
        "DOCS: UI_SYSTEM.md, BUILD_PROCESS.md, DEVTOOLS_GUIDE.md, MIGRATION_GUIDE.md added.",
        "AUDIT: 10,000-step × 5-seed headless audit on AAD engine — zero crashes.",
    ],
    "1.0.0-alpha": [
        "Active Action Dispatch (AAD) — all actions described in data/actions/*.json.",
        "ResolverRegistry auto-discovers resolvers; no manual registration required.",
        "ActionDispatcher validates, loads, and chains 40 action JSON files.",
        "30 resolver modules; 0 unavailable at startup.",
        "Engine fully wired to AAD — zero hardcoded if/elif action chains.",
        "Tier 4: shop economy — buy/sell at marketplace, alchemy hall, blacksmith.",
        "Tier 4: data-driven loot — all 12 enemies have full loot fields.",
        "DevTools: Validate Actions tab + Generate Resolver tab.",
    ],
    "0.9.6": [
        "Trinity architecture: Data / Logic / UI with PlayerMgr, EntityMgr, CombatMgr.",
        "22 atomic simple units, complex managers, core orchestrators.",
    ],
}
