# app/version.py
VERSION       = "1.0.0"
VERSION_LABEL = f"v{VERSION}"

CHANGELOG = {
    "1.0.0": [
        "Active Action Dispatch (AAD) — all actions described in data/actions/*.json.",
        "ResolverRegistry auto-discovers resolvers; no manual registration required.",
        "ActionDispatcher validates, loads, and chains 40 action JSON files.",
        "30 resolver modules; 0 unavailable at startup.",
        "Engine fully wired to AAD — zero hardcoded if/elif action chains.",
        "Tier 4: shop economy — buy/sell at marketplace, alchemy hall, blacksmith.",
        "Tier 4: data-driven loot — all 12 enemies have full loot fields.",
        "Tick_buffs dispatched after every combat round.",
        "advance_year dispatched via _tick_year() every 30 actions.",
        "Fishing stubs — cast_line + fishing_tick resolvers; fish_pool.json.",
        "DevTools: Validate Actions tab + Generate Resolver tab.",
        "--debug flag for verbose dispatcher output.",
        "Full documentation rewrite: ARCHITECTURE, CONTRIBUTING, DATA_SCHEMA, ROADMAP.",
    ],
    "0.9.6": [
        "Trinity architecture: Data / Logic / UI with PlayerMgr, EntityMgr, CombatMgr.",
        "22 atomic simple units, complex managers, core orchestrators.",
    ],
}
