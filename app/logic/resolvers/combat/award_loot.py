"""combat.award_loot — roll and award gold + item drops after enemy death."""
import random
from app.logic.action_types import ActionContext, ActionResult
from app.logic.simple.add_gold import add_gold
from app.logic.simple.add_item  import add_item
from app.logic.simple.increment_stat import increment_stat


def resolve(ctx: ActionContext) -> ActionResult:
    ps    = dict(ctx.player_state)
    enemy = ctx.reference or {}
    msgs  = []

    # Increment kill counter
    ps = increment_stat(ps, "kills", 1)

    # Gold reward
    gold_min = enemy.get("gold_min")
    gold_max = enemy.get("gold_max")
    if gold_min is None or gold_max is None:
        hp = enemy.get("hp", 10)
        gold_min, gold_max = max(1, hp // 4), max(2, hp // 2)
    gold_earned = random.randint(int(gold_min), int(gold_max))
    ps, _ = add_gold(ps, gold_earned)
    msgs.append(f"You loot {gold_earned}g from the body.")

    # Item loot
    loot_table  = enemy.get("loot_table", [])
    loot_chance = enemy.get("loot_chance", 0.6)
    loot_count  = enemy.get("loot_count", 1)
    if loot_table and random.random() < loot_chance:
        reg = ctx.data_registry
        names = []
        for _ in range(int(loot_count)):
            item_id = random.choice(loot_table)
            ps = add_item(ps, item_id)
            if reg:
                item = reg.items.get(item_id)
                names.append(item["name"] if item else item_id)
            else:
                names.append(item_id)
        if names:
            msgs.append(f"Dropped: {', '.join(names)}.")

    return ActionResult(ps, ctx.dungeon_state, msgs)
