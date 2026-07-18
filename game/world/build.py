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
    [QUEUE]---[HALL]------[O-ANTE]         Vis 3 / 2
                 |            |
              [ALLEY]     (orientation      Vis 2
                 |         lattice, x=1..2,
              [TENEMENT]   see below)       Vis 1
                 |
     (down) [TUNNEL]                        Vis 0

    Orientation Wing lattice (east of the Hall — 3M's tutorial-as-
    architecture pattern, docs/research/third-millennium-mud.md §5):

    (1,2) [O-FILE]------(2,2) [O-CIVIC]
    (1,1) [O-WATCHED]---(2,1) [O-CORRIDOR]  <- Vis 5 demo room
    (1,0) [O-ANTE]

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
        "smells of wet wool and pencil shavings. A stencilled arrow points "
        "east: |wCITIZEN ORIENTATION. ATTENDANCE IS VOLUNTARY. ATTENDANCE IS "
        "NOTED.|n",
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
    # --- The Orientation Wing: rooms whose descriptions are the manual -----
    # (3M's tutorial-as-architecture; the Ministry teaches only the
    # sanctioned verbs. The unsanctioned ones are taught in chalk, below.)
    "o_ante": (
        "Orientation Antechamber",
        2,
        "Folding chairs, a lectern nobody stands at, and paint the exact "
        "green of not being asked your opinion. A placard reads:\n\n"
        "|w  WELCOME, CITIZEN. THE GRID PROVIDES. THE GRID OBSERVES.\n"
        "  Read every room carefully; rooms are how the Grid explains\n"
        "  itself. The numbers in your prompt are yours: Vis is how\n"
        "  watched a place is (0-5). Exp is how interesting you have\n"
        "  made yourself. Low numbers are a virtue.\n"
        "  Proceed NORTH when ready. Type |chelp|w at any difficulty.|n",
    ),
    "o_watched": (
        "Orientation: The Watched Life",
        2,
        "Diagrams of street corners cover the walls, each with sight-lines "
        "drawn in red. A placard reads:\n\n"
        "|w  The Watch protects you by knowing you. Moving through watched "
        "space raises your Exp; time and good conduct lower it. Citizens "
        "of interest may be stopped and checked - cooperation clears you, "
        "and clearing is itself a credential. Citizens of |rgreat|w interest "
        "are detained for their protection.\n"
        "  You may study any room's devices yourself: type |cobserve|w. "
        "Attention is a skill. The Watch will not mind. The Watch does "
        "not mind anything.|n\n\n"
        "Continue NORTH.",
    ),
    "o_file": (
        "Orientation: Your File",
        2,
        "A wall-sized reproduction of a citizen file, annotated, with a "
        "child's handwriting exercise underneath: THE FILE IS MY FRIEND. "
        "A placard reads:\n\n"
        "|w  Everything of note about you is recorded at the Ministry of "
        "Records. Type |cdossier|w to review your file at any time. Your "
        "file is accurate. Incidents, once recorded, are part of you - "
        "though the Ministry, in its generosity, hears petitions: visit "
        "the archivist at the Archive Annex to |cpetition|w for corrections, "
        "priced in standing you have earned. The Ministry forgets nothing "
        "unless asked politely, in writing, for a consideration.|n\n\n"
        "Continue EAST.",
    ),
    "o_civic": (
        "Orientation: Civic Life",
        2,
        "Murals of citizens stamping forms, carrying sacks, and smiling in "
        "the approved manner. A placard reads:\n\n"
        "|w  Usefulness is safety. Report to the Assignment Hall counter and "
        "type |cwork|w: clerical shifts earn standing with the Ministry of "
        "Records and demonstrate the visible virtue that cools an "
        "interesting reputation. Between shifts, stand in the ration queue "
        "and |clisten|w - the queue is the beating heart of Sector 9, and "
        "hearing is not yet a crime.|n\n\n"
        "Continue SOUTH for the practical portion of your orientation.",
    ),
    "o_corridor": (
        "Orientation: Demonstration Corridor",
        5,
        "A short corridor lit like an operating theatre. Every surface is "
        "lens. A counter above the far door displays your exposure in "
        "figures a hand tall, updating as you walk. A placard reads:\n\n"
        "|w  This corridor is watched at the highest civic grade, so that "
        "you may feel the difference. Note the Exp figure in your prompt "
        "as you entered. This sensation - of a number rising because you "
        "went somewhere - is the fundamental transaction of the Grid. "
        "Spend it wisely.\n"
        "  Your orientation is complete. Exit WEST, then SOUTH, then WEST "
        "to the Assignment Hall. The Grid is waiting.|n",
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
        "o_corridor",
        "a demonstration lens array",
        "Rank upon rank of lenses, polished to a municipal shine, each one "
        "labelled with a small brass number as if to say: catalogued, like "
        "you. A plaque beneath reads: THE SENSATION YOU ARE EXPERIENCING "
        "IS SAFETY.",
        2,
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
    # The Orientation Wing lattice (see module docstring sketch).
    ("hall", "o_ante", "east", 0),
    ("o_ante", "o_watched", "north", 0),
    ("o_watched", "o_file", "north", 0),
    ("o_file", "o_civic", "east", 0),
    ("o_civic", "o_corridor", "south", 0),
    ("o_corridor", "o_watched", "west", 0),
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

    # The orientation clerk: the first face a citizen meets, if they take
    # the arrow's advice.
    orienter = create_object(
        "typeclasses.npcs.Citizen",
        key="the orientation clerk",
        location=rooms["o_ante"],
    )
    orienter.db.desc = (
        "Young, pressed, and reciting even when silent. Their lanyard "
        "photograph smiles slightly more than they do. They administer the "
        "orientation by standing near it."
    )
    orienter.db.react_calm = (
        "{npc} brightens by a regulation amount. \"Welcome, citizen! The "
        "rooms explain everything. Read them in order. Or don't! Attendance "
        "is voluntary.\" A pause. \"It's noted, but it's voluntary.\""
    )
    orienter.db.react_noticed = (
        "{npc} checks a clipboard as {name} enters, and their smile gains a "
        "structural quality."
    )
    orienter.db.react_hot = (
        "{npc} recalls, aloud and to no one, that orientation materials are "
        "also available in printed form, elsewhere, far away."
    )

    # The unsanctioned curriculum: what the Ministry doesn't teach, the
    # tunnels do. (Described chalk must exist — principle 9.)
    chalk = create_object(
        "typeclasses.objects.Object",
        key="the chalk marks",
        aliases=["chalk", "marks"],
        location=rooms["tunnel"],
    )
    chalk.db.desc = (
        "Fresh chalk over old chalk over older chalk, a curriculum in "
        "layers:\n\n"
        "  |w- sweeps can't reach where nothing watches. down here you are\n"
        "    a rumor.|n\n"
        "  |w- the file isn't you. a steady hand and a dead terminal can\n"
        "    |cforge|w it. first try goes badly for most. so did yours.|n\n"
        "  |w- the broken screen on the alley stays broken because nobody\n"
        "    files the form. remember what a form can do.|n\n"
        "  |w- heat fades. sit. breathe. count the water drips. then go up\n"
        "    and be boring.|n\n\n"
        "Beneath, in different hands: initials, dates, and one line pressed "
        "hard enough to break the chalk: |wthey write it down. so can we.|n"
    )
    chalk.locks.add("get:false()")
    chalk.db.get_err_msg = "The wall declines to come along."

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
