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

# --- v0.3: records, services, skills ---------------------------------------

# Sensors log a movement record for anyone at/above this exposure — one entry
# per citizen per cooldown, not a flood (ADR 0005's growth concern).
SENSOR_LOG_MIN_EXPOSURE = 25
SENSOR_LOG_COOLDOWN = 300  # seconds

# Clerical work (the first sanctioned skill loop): pays standing with the
# Ministry of Records, teaches clerking, and being visibly useful lowers
# exposure a little.
WORK_COOLDOWN = 45  # seconds between shifts
WORK_INFLUENCE = 2  # a redaction = 4 shifts (~3 min of visible usefulness)
WORK_EXPOSURE_RELIEF = 2

# Records Annex services (the sanctioned route). Costs are influence with the
# Ministry of Records; using the service at all is itself noticed.
AMEND_COST = 4
REDACT_COST = 8
SERVICE_EXPOSURE = 10

# Forgery (the unsanctioned route): only possible somewhere truly unwatched
# (visibility 0). Success rewrites your file off the books; failure *is* an
# incident.
FORGE_BASE_CHANCE = 0.25
FORGE_SKILL_BONUS = 0.005  # per skill point: +0.5%/pt, +25% at cap
FORGE_FAIL_EXPOSURE = 15

# Observation: reading the apparatus back. Tier thresholds are skill values.
OBSERVE_TIER_STATUS = 15   # see which devices are live vs dead
OBSERVE_TIER_DETAIL = 35   # see how sharp each device is

# Skill-by-use: +1 per meaningful use, to a v0.3 soft cap.
SKILL_CAP = 50

# Queue gossip surfaces incidents this recent, about other citizens.
GOSSIP_WINDOW = 6 * 3600  # seconds
GOSSIP_LIMIT = 3

# --- v0.4: standing and paperwork ------------------------------------------

# Working your assigned function pays this much standing with the assigning
# ministry; casual (unassigned) hall labor still pays WORK_INFLUENCE.
FUNCTION_WORK_INFLUENCE = 3

# Form C-1 (Application for Elevated Clearance), heard at the Archive Annex.
CLEARANCE_FEE = 6                 # Ministry of Records standing, at submission
CLEARANCE_MAX_INCIDENTS = 1       # visible incidents beyond this = rejection
CLEARANCE_GRANT_EXPOSURE = 10     # elevation means scrutiny (M2)

# Speaking on the gridwide channel is speaking into a microphone.
CHANNEL_EXPOSURE = 2

# --- v0.5: trust -----------------------------------------------------------

# Signals between cell members are safe from rooms at or below this
# visibility; above it, each further visibility point adds interception risk.
SIGNAL_SAFE_VISIBILITY = 1
SIGNAL_INTERCEPT_PER_VIS = 0.2
SIGNAL_INTERCEPT_EXPOSURE = 12

# Being named in a comrade's confession (Section C).
CELL_NAMED_EXPOSURE = 25

# Declining to complete Section C gets you released — onto a shorter leash.
RELEASE_EXPOSURE_UNCOOPERATIVE = 20

# Informants are recruited where the Grid watches loosely, if at all.
RECRUIT_MAX_VISIBILITY = 2

# Flipping a Ministry plant is a Commerce transaction (ration chits change
# hands); reading them well enough to dare it is an observation problem.
FLIP_COST = 5

# A recruited Ministry plant files on one cell member per cooldown.
INFORMANT_REPORT_COOLDOWN = 600  # seconds
INFORMANT_REPORT_EXPOSURE = 5

# Concealed devices only show themselves to a truly practiced eye.
OBSERVE_TIER_CONCEALED = 45

# Civic assemblies: the script ticks at ASSEMBLY_TICK; after announcement,
# attendance is taken one tick later; then the Grid rests for REST_TICKS.
ASSEMBLY_TICK = 120  # seconds
ASSEMBLY_REST_TICKS = 8  # ~16 min between assemblies
ASSEMBLY_ATTEND_RELIEF = 5
ASSEMBLY_ABSENT_EXPOSURE = 10
