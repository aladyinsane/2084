"""
Every gameplay number lives here, nowhere else.

ADR 0004 promises permanent tuning of the surveillance model; hunting magic
numbers across typeclasses is the failure mode this file prevents
(docs/engineering/architecture.md).
"""

# Exposure gained on entering a room, indexed by the room's visibility (0-5).
# Vis 0-1 is the "shallow end": nobodies in unwatched places accrue nothing.
VISIBILITY_EXPOSURE = {
    0: 0,
    1: 0,
    2: 1,
    3: 1,
    4: 2,
    5: 3,
}

# Exposure is clamped to [0, EXPOSURE_MAX].
EXPOSURE_MAX = 100

# Global decay tick: every interval, everyone's exposure drifts down by this
# amount. Slow on purpose — being seen should linger.
EXPOSURE_DECAY_INTERVAL = 300  # seconds
EXPOSURE_DECAY_AMOUNT = 1
