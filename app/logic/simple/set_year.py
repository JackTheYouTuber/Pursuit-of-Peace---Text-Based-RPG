"""set_year — advance the year counter and reset tax_paid."""
from typing import Dict

def set_year(state: Dict, new_year: int) -> Dict:
    s = dict(state)
    s["year"] = new_year
    s["tax_paid"] = False
    return s
