
from typing import Dict, Tuple, Union
from utils.metrics import METRIC_ALIASES, ALIAS_LOOKUP, REF_RANGES

FlaggedMetric = Tuple[str, str]  # (value‑string, colour)

def flag_metrics(values: Dict[str, Union[float, None]]) -> Dict[str, FlaggedMetric]:
    flagged: Dict[str, FlaggedMetric] = {}
    for metric, val in values.items():
        if val is None:
            flagged[metric] = ("❌ Missing", "red")
            continue
        if metric not in REF_RANGES:
            flagged[metric] = (f"{val} (no ref)", "gray")
            continue
        lo, hi = REF_RANGES[metric]
        colour = "green" if lo <= val <= hi else "orange"
        suffix = " ⚠️" if colour == "orange" else ""
        flagged[metric] = (f"{val}{suffix}", colour)
    return flagged
