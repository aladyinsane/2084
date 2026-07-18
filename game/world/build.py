"""
Builds the starting district of the Grid: Sector 9.

The world is code (docs/engineering/contributing.md rule 8): this module is the
source of truth for the starting district, run once by the initial-setup hook.

Grid-consistency (ADR 0007): every room sits on the 2D plan below; all exits
are compass directions with true reciprocals. Sketch first, then code.

    z=0                            z=-1

            [CHECKPOINT]  Vis 5
                 |
    [ANNEX]---[PLAZA]     Vis 4
                 |
    [QUEUE]---[HALL]      Vis 3   <- start (repurposed Limbo)
                 |
              [ALLEY]     Vis 2
                 |
              [TENEMENT]  Vis 1 --(down)-- [TUNNEL]  Vis 0

    (off-plan: [HOLDING CELL] — no exits; reached only by being detained)
"""

from evennia import create_object, search_object
from evennia.utils import logger

# Reciprocal compass pairs and their standard aliases.
OPPOSITE = {
    "north": "south",
    "south": "north",
    "east": "west",
    "west": "east",
    "up": "down",
    "down": "up",
}
ALIASES = {
    "north": ["n"],
    "south": ["s"],
    "east": ["e"],
    "west": ["w"],
    "up": ["u"],
    "down": ["d"],
}

ROOMS = {
    "hall": (
        "Assignment Hall",
        3,
        "A long municipal room the color of weak tea. Citizens queue between "
        "rope barriers toward a counter where a clerk of the Ministry of Order "
        "stamps work assignments without looking up. A watchscreen high on the "
        "wall cycles the day's directives; its lens does not cycle. The air "
        "smells of wet wool and pencil shavings.",
    ),
    "plaza": (
        "Unity Plaza",
        4,
        "The open heart of Sector 9, paved in regulation grey. Loudspeakers on "
        "every lamppost murmur production figures like a lullaby. The crowds "
        "here move briskly and look at nothing, which is a skill. North, the "
        "Central Spire checkpoint scans the worthy through; the Spire itself "
        "rises beyond it until the smog decides otherwise.",
    ),
    "checkpoint": (
        "Central Spire Checkpoint",
        5,
        "Steel gates, white light, no shadows anywhere — the architecture of "
        "being seen. Officers of the Watch stand behind glass, faces lit from "
        "below by scanner readouts. A sign in Ministry typeface reads: "
        "TRANSPARENCY IS SAFETY. YOURS. The queue is silent, and everyone in "
        "it is rehearsing.",
    ),
    "annex": (
        "Archive Annex",
        4,
        "A reading room of the Ministry of Records: rows of public terminals "
        "bolted to desks, each screen slightly cloudy, as if breathed on for "
        "decades. Here a citizen may consult the record, which is accurate, "
        "and has always been accurate. An archivist watches from a raised "
        "desk, logging who reads what.",
    ),
    "queue": (
        "Ration Queue",
        3,
        "A covered walkway along the distribution windows of the Ministry of "
        "Commerce. The queue exists whether or not anything is being "
        "distributed; standing in it is the nearest thing Sector 9 has to a "
        "public square. Gossip travels down the line faster than the line "
        "itself, and more reliably than the newsfeeds.",
    ),
    "alley": (
        "Neon Alley",
        2,
        "A crooked seam between tenement blocks where half the lamps are "
        "burned out and nobody files the maintenance form. Vendors sell tea, "
        "batteries, and things kept under the tea. The one watchscreen here "
        "was installed in the spring; it has been broken since the spring.",
    ),
    "tenement": (
        "Tenement Row",
        1,
        "Housing block K-fifty-something — the stencilled number has flaked "
        "past reading. Laundry lines web the airshaft, a radio plays a song "
        "older than the regime, and someone is arguing about a kettle. The "
        "Grid barely watches here. Nobody worth watching, says the Grid. The "
        "residents work hard to keep it thinking so.",
    ),
    "tunnel": (
        "Tunnel B",
        0,
        "A dead service tunnel under Tenement Row, lit by whatever you brought "
        "with you. Cables sag from the ceiling like jungle vines; water ticks "
        "somewhere in the dark. No sensors reach down here. The chalk marks on "
        "the wall are recent, and they are not the Ministry's.",
    ),
    # Off-plan by design: you are *taken* here, never walked (documented
    # exception under ADR 0007 — no exits, so nothing to map).
    "cell": (
        "Holding Cell, Ministry of Order",
        5,
        "Four white walls, a bench, a light that has no switch, and a door "
        "with no handle on this side. A grille at eye level lets the corridor "
        "look in; it does not particularly let you look out. Someone has "
        "scratched four thin lines into the bench. There is a fifth line, "
        "fainter, abandoned halfway.",
    ),
}

# (room, sensor key, sensor desc, sensitivity, active)
# Every device a room description promises must exist as an object, or
# `observe` calls the description a liar (principle 9, learned in-game).
SENSORS = [
    (
        "hall",
        "a watchscreen",
        "High on the wall, cycling the day's directives in Ministry typeface. "
        "The lens beneath the screen does not cycle. It is aimed at the "
        "queue, which is to say, at everyone who has ever stood in it.",
        1,
        True,
    ),
    (
        "checkpoint",
        "a scanner array",
        "Black glass domes track in smooth, silent arcs — plural, overlapping, "
        "leaving no angle unaccounted for. A status row of green diodes "
        "confirms that everything is working, which you already knew.",
        2,
        True,
    ),
    (
        "plaza",
        "a watchscreen",
        "A public screen two stories tall, cycling production figures over "
        "the Ministry crest. The lens above it is small, unblinking, and "
        "aimed at the crowd rather than the screen.",
        1,
        True,
    ),
    (
        "annex",
        "a reading-desk monitor",
        "A slim camera on an articulated arm, positioned to see not the "
        "terminals but the faces at them. A brass plate reads: FOR YOUR "
        "SECURITY AND CONVENIENCE.",
        1,
        True,
    ),
    (
        "alley",
        "a broken watchscreen",
        "Installed in the spring, dead since the spring. The lens is crazed "
        "with a spiderweb crack radiating from something thrown precisely "
        "once. Nobody has filed the maintenance form, and nobody is going to.",
        1,
        False,
    ),
]

# (from, to, direction, exposure_modifier on that one-way exit)
LINKS = [
    ("hall", "plaza", "north", 0),
    ("plaza", "checkpoint", "north", 2),  # scanner gate: costs extra to enter
    ("plaza", "annex", "west", 0),
    ("hall", "queue", "west", 0),
    ("hall", "alley", "south", 0),
    ("alley", "tenement", "south", 0),
    ("tenement", "tunnel", "down", 0),
]


def _link(source, dest, direction, modifier=0):
    """Create a two-way, reciprocal compass link (ADR 0007)."""
    back = OPPOSITE[direction]
    out = create_object(
        "typeclasses.exits.Exit",
        key=direction,
        aliases=ALIASES[direction],
        location=source,
        destination=dest,
    )
    if modifier:
        out.db.exposure_modifier = modifier
    create_object(
        "typeclasses.exits.Exit",
        key=back,
        aliases=ALIASES[back],
        location=dest,
        destination=source,
    )
    return out


def build():
    """Build Sector 9. Run once, at initial setup."""
    rooms = {}

    # Limbo (#2, the default start location) becomes the Assignment Hall, so
    # settings.START_LOCATION needs no dbref guesswork.
    limbo = search_object("Limbo")
    if limbo:
        hall = limbo[0]
        hall.key = ROOMS["hall"][0]
        hall.aliases.clear()
    else:
        hall = create_object("typeclasses.rooms.Room", key=ROOMS["hall"][0])
    hall.db.desc = ROOMS["hall"][2]
    hall.db.visibility = ROOMS["hall"][1]
    rooms["hall"] = hall

    for tag, (name, visibility, desc) in ROOMS.items():
        if tag == "hall":
            continue
        room = create_object("typeclasses.rooms.Room", key=name)
        room.db.desc = desc
        room.db.visibility = visibility
        rooms[tag] = room

    for source, dest, direction, modifier in LINKS:
        _link(rooms[source], rooms[dest], direction, modifier)

    # Functional tags: where the Watch takes you, releases you, and musters —
    # and where citizens work, and where the queue talks.
    rooms["cell"].tags.add("holding_cell", category="grid")
    rooms["hall"].tags.add("release_point", category="grid")
    rooms["plaza"].tags.add("patrol_spawn", category="grid")
    rooms["hall"].tags.add("workplace", category="grid")
    rooms["queue"].tags.add("gossip_spot", category="grid")

    # The surveillance apparatus, in the world where it can be seen.
    for room_tag, key, desc, sensitivity, active in SENSORS:
        sensor = create_object(
            "typeclasses.objects.Sensor", key=key, location=rooms[room_tag]
        )
        sensor.db.desc = desc
        sensor.db.sensitivity = sensitivity
        sensor.db.active = active

    # The ration clerk: the first NPC who reads your record off your face.
    clerk = create_object(
        "typeclasses.npcs.Citizen",
        key="the ration clerk",
        location=rooms["queue"],
    )
    clerk.db.desc = (
        "Grey-aproned, quick-handed, older than the queue and more patient "
        "than the Ministry. Their eyes do a small arithmetic on everyone who "
        "approaches the window."
    )
    clerk.db.react_calm = (
        "{npc} slides a ration chit across the counter without looking up."
    )
    clerk.db.react_noticed = (
        "{npc} pauses mid-count as {name} arrives, then resumes, one beat late."
    )
    clerk.db.react_hot = (
        "{npc} finds urgent business in the back room the moment {name} "
        "approaches."
    )

    # The archivist: the sanctioned route to a different past (ADR 0005).
    archivist = create_object(
        "typeclasses.npcs.Citizen",
        key="the archivist",
        location=rooms["annex"],
    )
    archivist.tags.add("records_service", category="grid")
    archivist.db.desc = (
        "Dust-colored cardigan, cotton gloves, and the serenity of someone "
        "who decides what happened. The archivist amends and redacts citizen "
        "files for a consideration in standing — petition them, and the past "
        "improves. The service is real, the ledger is balanced, and the "
        "request goes in a file of its own."
    )
    archivist.db.react_calm = (
        "{npc} continues re-shelving the past, one folder at a time."
    )
    archivist.db.react_noticed = (
        "{npc} looks at {name} the way one checks a citation."
    )
    archivist.db.react_hot = (
        "{npc} slides a drawer shut as {name} enters, unhurried, precise."
    )

    logger.log_info(f"2084: built Sector 9 ({len(rooms)} rooms).")
    return rooms
