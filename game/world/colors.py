"""
Shared color mappings for stats that appear in more than one place (the
prompt, the map) so the two can't quietly drift apart.
"""

from world import tuning

# Visibility digit (0-5): dark places green, watched places hot.
VIS_COLORS = {0: "|g", 1: "|w", 2: "|w", 3: "|y", 4: "|y", 5: "|r"}


def exposure_color(value):
    """Exposure band color, keyed to the sweep/detainment thresholds."""
    if value >= tuning.DETAIN_THRESHOLD:
        return "|r"
    if value >= tuning.SWEEP_MIN_EXPOSURE:
        return "|y"
    return "|g"
