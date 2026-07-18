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

# --- v0.2: the Watch -------------------------------------------------------

# The sweep samples connected citizens on this interval (ADR 0004: sampled,
# never triggered; likely and soon at high exposure, never a scripted
# certainty).
WATCH_SWEEP_INTERVAL = 90  # seconds

# The shallow end (principle 10): below this exposure the Watch does not
# sample you at all. Nobodies are not worth watching.
SWEEP_MIN_EXPOSURE = 20

# At or above this exposure, being swept (or crossing a patrol) means
# detainment; below it, a papers check.
DETAIN_THRESHOLD = 50

# Sweep selection probability ramps linearly from 0 at SWEEP_MIN_EXPOSURE to
# SWEEP_MAX_CHANCE at EXPOSURE_MAX.
SWEEP_MAX_CHANCE = 0.6

# Being checked and cleared is a sanctioned interaction: it lowers exposure.
PAPERS_CHECK_RELIEF = 8

# Exposure you leave detainment with (they know exactly where you are — for
# the moment, you are the least interesting person in the Grid).
RELEASE_EXPOSURE = 5

# `wait` this many times in the holding cell and they lose interest.
WAIT_RELEASE_TURNS = 5

# Patrol NPCs keep to streets at or above this visibility (the tunnels are
# unpatrolled — that's what makes them the tunnels).
PATROL_MIN_VISIBILITY = 2
PATROL_MOVE_INTERVAL = 45  # seconds

# District alert: rises on detainment, decays on quiet sweep ticks. Patrol
# density = 1 + alert, capped.
ALERT_MAX = 2
PATROL_BASELINE = 1

# NPC reaction tiers (read by clerks, patrols): below WARM you're nobody,
# WARM..HOT gets you noticed, at HOT+ people edge away.
NOTICE_EXPOSURE = 25
HOT_EXPOSURE = 50
