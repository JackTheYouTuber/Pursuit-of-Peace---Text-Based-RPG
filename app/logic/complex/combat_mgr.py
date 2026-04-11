"""
CombatMgr — manages a combat session between the player and an enemy.

Player actions are sent in by the human controller (the UI).
Enemy actions are decided by entity_ai (the AI controller).

Player body operations go through PlayerMgr.
Enemy body operations go through EntityMgr.
Neither manager knows about the other. CombatMgr coordinates both.
"""
import random
from typing import Dict, List, Optional, Tuple

from app.logic.simple.entity_ai      import decide_combat_action
from app.logic.simple.increment_stat import increment_stat
from app.logic.simple.add_gold       import add_gold
from app.logic.simple.add_item       import add_item
from app.logic.simple.get_weapon_bonus  import get_weapon_bonus
from app.logic.simple.get_armor_defense import get_armor_defense
from app.logic.simple.get_buff_bonus    import get_buff_bonus


class CombatMgr:
    def __init__(self, player_mgr, entity_mgr):
        self._player = player_mgr   # PlayerMgr  — for player body ops
        self._entity = entity_mgr   # EntityMgr  — for enemy body ops
        self._cs:    Optional[Dict] = None
        self._log:   List[str]      = []

    # ── Session ────────────────────────────────────────────────────────

    def start(self, player_state: Dict, enemy_def: Dict) -> Dict:
        """Open a combat session. Build enemy entity state from its definition."""
        enemy_state = self._entity.from_def(enemy_def)
        self._log = [f"A {enemy_def.get('name', '?')} bars your path!"]
        self._cs = {
            "player":       dict(player_state),
            "enemy":        enemy_state,
            "enemy_def":    enemy_def,
            "round":        0,
            "player_dead":  False,
            "enemy_dead":   False,
        }
        return self._snapshot()

    def clear(self):
        self._cs  = None
        self._log = []

    def active(self) -> bool:
        return self._cs is not None

    def snapshot(self) -> Optional[Dict]:
        return self._snapshot() if self._cs else None

    # ── Player turn ────────────────────────────────────────────────────

    def player_turn(self, player_state: Dict,
                    action: str) -> Tuple[Dict, Dict, bool, bool]:
        """
        Execute one full combat round initiated by the player's action,
        followed by the enemy's AI-chosen response.

        Returns (updated_player_state, combat_snapshot, combat_ended, player_dead).
        """
        assert self._cs, "No active combat"
        self._cs["round"] += 1
        self._cs["player"] = dict(player_state)

        # ── Player acts ────────────────────────────────────────────────
        ended, player_dead = self._resolve_player_action(action)
        if ended:
            self._cs["player_dead"] = player_dead
            self._cs["enemy_dead"]  = not player_dead
            if not player_dead:
                self._cs["player"] = self._award_victory(
                    self._cs["player"], self._cs["enemy_def"])
            return self._cs["player"], self._snapshot(), True, player_dead

        # ── Enemy acts ─────────────────────────────────────────────────
        enemy_action = self._decide_enemy_action()
        ended, enemy_dead = self._resolve_enemy_action(enemy_action)
        if ended:
            player_dead = not enemy_dead
            self._cs["player_dead"] = player_dead
            self._cs["enemy_dead"]  = enemy_dead
            if not player_dead:
                self._cs["player"] = self._award_victory(
                    self._cs["player"], self._cs["enemy_def"])
            return self._cs["player"], self._snapshot(), True, player_dead

        return self._cs["player"], self._snapshot(), False, False

    def flee(self) -> str:
        self._log.append("You flee!")
        return "You flee from combat."

    # ── Player action resolution ───────────────────────────────────────

    def _resolve_player_action(self, action: str) -> Tuple[bool, bool]:
        """Returns (combat_ended, player_is_dead)."""
        ps = self._cs["player"]
        es = self._cs["enemy"]
        edef = self._cs["enemy_def"]

        # Use item
        if action.startswith("use_item:"):
            item_id = action.split(":", 1)[1]
            ps, msg = self._player.use_item(ps, item_id)
            self._log.append(f"You: {msg}")
            self._cs["player"] = ps
            return False, False

        # Attack
        if action == "attack":
            base         = random.randint(4, 8)
            buff_bonus   = get_buff_bonus(ps, "damage_bonus")
            w_bonus, w_name = get_weapon_bonus(ps)
            total = base + buff_bonus + w_bonus

            detail = (f" ({base}+{buff_bonus}b+{w_bonus} {w_name})"
                      if (buff_bonus or w_bonus) else "")
            self._log.append(
                f"You strike {edef.get('name','?')} for {total}.{detail}")

            # Decay player weapon
            if ps.get("equipped_weapon"):
                ps, broke = self._player.decay(ps, "equipped_weapon")
                if broke:
                    self._log.append(f"⚠ Your {w_name} breaks!")
            self._cs["player"] = ps

            # Deal damage to enemy through EntityMgr
            a_val, a_name = get_armor_defense(es)
            absorbed = min(total - 1, a_val)
            received = total - absorbed
            if absorbed > 0:
                self._log.append(f"{a_name} absorbs {absorbed}. "
                                 f"Enemy takes {received}.")
                es, broke = self._entity.decay(es, "equipped_armor")
                if broke:
                    self._log.append(f"⚠ Enemy's {a_name} breaks!")
            es, dead = self._entity.damage(es, received)
            self._cs["enemy"] = es
            if dead:
                self._log.append(f"The {edef.get('name','?')} falls.")
            # Tick player turn buffs
            ps, expired = self._player.tick_buffs(self._cs["player"])
            self._cs["player"] = ps
            if expired:
                self._log.append("Buff expired: " + ", ".join(expired))
            return dead, False

        self._log.append("You hesitate.")
        return False, False

    # ── Enemy action resolution ────────────────────────────────────────

    def _decide_enemy_action(self) -> str:
        es = self._cs["enemy"]
        ps = self._cs["player"]
        context = {
            "entity_hp":       es.get("hp", 0),
            "entity_max_hp":   es.get("max_hp", 1),
            "opponent_hp":     ps.get("hp", 0),
            "opponent_max_hp": ps.get("max_hp", 20),
            "round":           self._cs["round"],
        }
        return decide_combat_action(es, context)

    def _resolve_enemy_action(self, action: str) -> Tuple[bool, bool]:
        """Returns (combat_ended, enemy_is_dead — always False here)."""
        ps   = self._cs["player"]
        es   = self._cs["enemy"]
        edef = self._cs["enemy_def"]
        name = edef.get("name", "Enemy")

        if action.startswith("use_item:"):
            item_id = action.split(":", 1)[1]
            es, msg = self._entity.use_item(es, item_id)
            self._log.append(f"{name}: {msg}")
            self._cs["enemy"] = es
            return False, False

        if action == "attack":
            raw     = random.randint(edef.get("damage_min", 1),
                                     edef.get("damage_max", 3))
            w_b, _  = get_weapon_bonus(es)
            total   = raw + w_b

            a_val, a_name = get_armor_defense(ps)
            buff_def = get_buff_bonus(ps, "defense_bonus")
            absorbed = min(total - 1, a_val + buff_def)
            received = total - absorbed

            if absorbed > 0:
                self._log.append(f"{name} strikes {total}. "
                                 f"{a_name} absorbs {absorbed}. "
                                 f"You take {received}.")
                ps, broke = self._player.decay(ps, "equipped_armor")
                if broke:
                    self._log.append(f"⚠ Your {a_name} breaks!")
            else:
                self._log.append(f"{name} strikes you for {received}.")

            ps, dead = self._player.damage(ps, received)
            self._cs["player"] = ps
            if dead:
                self._log.append("You collapse. Everything goes dark.")
            # Tick enemy buffs
            es, expired = self._entity.tick_buffs(es)
            self._cs["enemy"] = es
            if expired:
                self._log.append(f"{name} buff expired: " + ", ".join(expired))
            return dead, False

        self._log.append(f"{name} hesitates.")
        return False, False

    # ── Victory rewards ────────────────────────────────────────────────

    def _award_victory(self, player_state: Dict, enemy_def: Dict) -> Dict:
        ps = increment_stat(player_state, "kills")
        gmin = enemy_def.get("gold_min", max(1, enemy_def.get("hp", 10) // 4))
        gmax = enemy_def.get("gold_max", max(2, enemy_def.get("hp", 10) // 2))
        gold = random.randint(int(gmin), int(gmax))
        ps, _ = add_gold(ps, gold)
        self._log.append(f"You loot {gold}g.")

        loot_table = enemy_def.get("loot_table", [])
        chance     = enemy_def.get("loot_chance", 0.6)
        count      = int(enemy_def.get("loot_count", 1))
        if loot_table and random.random() < chance:
            for _ in range(count):
                item_id = random.choice(loot_table)
                item    = self._entity._items.get(item_id)
                if item:
                    ps = add_item(ps, item_id)
                    self._log.append(f"Dropped: {item['name']}.")
        return ps

    # ── Snapshot ───────────────────────────────────────────────────────

    def _snapshot(self) -> Dict:
        cs   = self._cs
        ps   = cs["player"]
        es   = cs["enemy"]
        edef = cs["enemy_def"]
        return {
            "enemy":             edef,
            "enemy_current_hp":  es.get("hp", 0),
            "player_current_hp": ps.get("hp", 0),
            "player_max_hp":     ps.get("max_hp", 20),
            "player_dead":       cs["player_dead"],
            "log_text":          "\n".join(self._log),
            "equipped_weapon":   ps.get("equipped_weapon"),
            "equipped_armor":    ps.get("equipped_armor"),
        }
