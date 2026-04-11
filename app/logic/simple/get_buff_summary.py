"""
get_buff_summary — return a human-readable string of active buffs.

One job: format the buffs list for display. Returns empty string when
no buffs are active. Does not know what entity this is.
"""
from typing import Dict


def get_buff_summary(state: Dict) -> str:
    buffs = state.get("buffs", [])
    if not buffs:
        return ""
    parts = []
    for b in buffs:
        label = b.get("label", b.get("id", "?"))
        dur   = b.get("duration", "")
        if dur == "turns":
            parts.append(f"{label} ({b.get('duration_remaining', '?')} turns)")
        elif dur == "one_run":
            parts.append(f"{label} (until exit)")
        else:
            parts.append(label)
    return ", ".join(parts)
