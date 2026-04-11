"""
year_clock.py — tracks the action counter and fires year rollover.

One job: count actions, tell the engine when a year has passed.
Does not decide what happens on rollover — that is PlayerMgr's job.
"""

ACTIONS_PER_YEAR = 30


class YearClock:
    def __init__(self):
        self._count = 0

    def tick(self) -> bool:
        """Increment. Returns True when a year has just completed."""
        self._count += 1
        if self._count >= ACTIONS_PER_YEAR:
            self._count = 0
            return True
        return False

    def reset(self):
        self._count = 0

    def progress(self):
        return self._count, ACTIONS_PER_YEAR
