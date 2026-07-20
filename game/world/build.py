"""
Builds the starting district of the Grid: Sector 9.

The world is code (docs/engineering/contributing.md rule 8): this module is the
source of truth for the starting district, run once by the initial-setup hook.

Grid-consistency (ADR 0007): every room sits on the 2D plan below; all exits
are compass directions with true reciprocals. Sketch first, then code.

    z=0                            z=-1

            [SPIRE LOBBY] Vis 5   <- clearance C-1 gate
                 |
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
     (down) [BOLT-HOLE]---[TUNNEL]  (z=-1)  Vis 0 / "0"

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
        "it is rehearsing. North, past the gates, the Spire lobby glows — "
        "clearance grade C-1 and above.",
    ),
    "spire_lobby": (
        "Central Spire Lobby",
        5,
        "Marble the color of dead screens, and a ceiling too far away to be "
        "about anything but the distance. Cleared citizens cross the floor "
        "at the speed of people who belong, which is a speed you can "
        "practice. Elevator banks line the far wall, each door stencilled "
        "with a number and a floor and, in two cases, nothing at all. A "
        "reception pillar states, without being asked: THE SPIRE IS THE "
        "GRID. THE GRID IS YOURS. ASCENT BY APPOINTMENT.",
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
    # The honeypot (v0.5): reads as a dead zone, is not one. The tell is
    # mechanical, not narrated — forge refuses here, the entry exposure tick
    # is +1 at Vis 0, and a very practiced eye can find the seam.
    "bolthole": (
        "The Bolt-Hole",
        0,
        "An old valve room off Tunnel B, fitted out as a refuge: two cots "
        "with folded blankets, a shelf of tinned rations, a kettle that has "
        "been recently cleaned. The chalk mark on the door is the right "
        "shape for |wsafe|n. Someone keeps this place nice. The blankets are "
        "folded very precisely, for a place with no one in it.",
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
        "  watched a place is (0-5). Exposure is how interesting you have\n"
        "  made yourself. Low numbers are a virtue.\n"
        "  A citizen is expected to know their sector. Consult your own\n"
        "  recollection at any time: |cmap|w. The Ministry issues no maps\n"
        "  and is confident you will not need one.\n"
        "  Proceed NORTH when ready. Type |chelp|w at any difficulty.|n",
    ),
    "o_watched": (
        "Orientation: The Watched Life",
        2,
        "Diagrams of street corners cover the walls, each with sight-lines "
        "drawn in red. A placard reads:\n\n"
        "|w  The Watch protects you by knowing you. Moving through watched "
        "space raises your Exposure; time and good conduct lower it. Citizens "
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
        "|w  Usefulness is safety. At the Assignment Hall counter, |creport|w "
        "to be assigned your function - the Grid will read your file and "
        "decide what you are - then |cwork|w your post for standing with "
        "your ministry. Standing buys the Ministry's services, and in time, "
        "elevation: citizens of good record may |capply|w at the Archive "
        "Annex for Spire clearance. Between shifts, stand in the ration "
        "queue and |clisten|w - hearing is not yet a crime. Merit accrues "
        "to the visibly useful, and merit is graded: every citizen holds a "
        "CIVIC GRADE, 6 down to 1, revised as the record warrants. Your "
        "grade rides in your prompt; your |cdossier|w states the review "
        "threshold. The Grid does not hide the ladder. The ladder is the "
        "point. The |cgridwide|w "
        "channel carries the public voice of Sector 9; it is public in "
        "every direction. Citizens seeking direction may ask after "
        "|cerrands|w - your orientation clerk keeps a short list of "
        "constructive uses for a citizen's legs. Standing may be spent at "
        "the requisitions window in the Assignment Hall (|clist|w, "
        "|cbuy|w, |cwear|w): badges, monitors, the small apparatus of "
        "being legible.\n"
        "  When the loudspeakers convene a CIVIC ASSEMBLY, attend. "
        "Attendance is recorded with gratitude. Absence is also recorded.|n"
        "\n\n"
        "Continue SOUTH for the practical portion of your orientation.",
    ),
    "o_corridor": (
        "Orientation: Demonstration Corridor",
        5,
        "A short corridor lit like an operating theatre. Every surface is "
        "lens. A counter above the far door displays your exposure in "
        "figures a hand tall, updating as you walk. A placard reads:\n\n"
        "|w  This corridor is watched at the highest civic grade, so that "
        "you may feel the difference. Note the Exposure figure in your prompt "
        "as you entered. This sensation - of a number rising because you "
        "went somewhere - is the fundamental transaction of the Grid. "
        "Spend it wisely.\n"
        "  Your orientation is complete, and has been credited: note the "
        "revision of your civic grade. The ladder runs from Grade 6 to "
        "Grade 1, and you are now on it. Exit WEST, then SOUTH, then WEST "
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
        "fainter, abandoned halfway.\n\n"
        "A card is screwed to the wall at eye height, in Ministry typeface:\n"
        "|w  NOTICE OF REMAINING ENTITLEMENTS (FORM 12-D)\n"
        "  The detainee may: |cwait|w. The detainee may: |cconfess|w.\n"
        "  The detainee may: |cdemand|w (see reverse). The detainee\n"
        "  retains the rights of speech (|csay|w), of reviewing their\n"
        "  file (|cdossier|w), and of |chelp|w, within reason.|n\n"
        "There is no reverse. The card is screwed flat to the wall.",
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
    ("tunnel", "bolthole", "west", 0),
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

    # Walking the Demonstration Corridor completes orientation and credits
    # a citizen's first merit (v0.12) — the tag is what rooms.py reads.
    rooms["o_corridor"].tags.add("orients", category="grid")

    # The Spire gate: the first clearance-locked exit in the Grid (locks,
    # not plot flags). The way back out is never locked — the Spire has no
    # interest in keeping you.
    gate = _link(rooms["checkpoint"], rooms["spire_lobby"], "north", 1)
    gate.locks.add("traverse:clearance(1)")
    gate.db.err_traverse = (
        "An officer's palm arrives at your sternum with institutional "
        "gentleness. \"Grade C-1 and above.\" The palm withdraws. The gate "
        "does not."
    )

    # Ambient texture (v0.8.5): the rooms with the most life get their own
    # murmur lines; everywhere else falls back to the AmbienceScript's
    # visibility-based defaults.
    rooms["hall"].db.ambience = [
        "The clerk's stamp comes down three times, pauses, and comes down "
        "once more, harder, on the same form.",
        "The watchscreen cycles to a new directive. Nobody looks up, which "
        "is a way of reading it.",
        "Somewhere in the queue, someone practices saying a sentence "
        "under their breath until it sounds unrehearsed.",
    ]
    rooms["plaza"].db.ambience = [
        "The loudspeakers announce that production is up. The crowd's "
        "pace stays exactly the same, which is also a figure.",
        "A child points at the big screen. An adult gently repositions "
        "the arm to point at nothing.",
        "Two officers cross the plaza diagonally. The crowd re-forms "
        "around their path like water that has opinions.",
    ]
    rooms["queue"].db.ambience = [
        "The line advances one place. Nobody saw the front of it move. "
        "Nobody has ever seen the front of it move.",
        "Somewhere behind you: '—and I said, you can't redact what I '"
        "'never said, and he wrote that down—'",
        "The distribution window opens, dispenses one (1) of something, "
        "and closes with the finality of a stamp.",
    ]
    rooms["alley"].db.ambience = [
        "A vendor rearranges the tea tins. One of them sloshes. Tea "
        "tins don't slosh.",
        "The dead watchscreen reflects the alley back at itself, which "
        "is the most honest surveillance in Sector 9.",
        "Someone up a ladder mutters at a lamp that has been beyond "
        "muttering for years.",
    ]
    rooms["tenement"].db.ambience = [
        "The radio upstairs finds the end of the old song and starts it "
        "again. Nobody minds. It's older than the curfew.",
        "The kettle argument enters its third movement, allegro.",
        "Laundry shifts overhead: today's flags of every household that "
        "is keeping its head down successfully.",
    ]
    rooms["tunnel"].db.ambience = [
        "Water ticks in the dark, keeping its own census.",
        "Far off down the tunnel, something settles: masonry, or the "
        "past. Nothing comes of it.",
        "Your light finds a chalk mark you hadn't noticed, older than "
        "the others, worn to a ghost: just an arrow, pointing down.",
    ]

    # Functional tags: where the Watch takes you, releases you, and musters —
    # and where citizens work, and where the queue talks.
    rooms["cell"].tags.add("holding_cell", category="grid")
    rooms["hall"].tags.add("release_point", category="grid")
    rooms["plaza"].tags.add("patrol_spawn", category="grid")
    rooms["hall"].tags.add("workplace", category="grid")
    rooms["queue"].tags.add("gossip_spot", category="grid")
    rooms["plaza"].tags.add("assembly_point", category="grid")

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
    orienter.tags.add("errand_giver", category="grid")
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
        "    and be boring.|n\n"
        "  |w- alone you are a file. together you are a problem. draw a\n"
        "    |ccircle|w, down here, with people you'd go to the cells for.|n\n"
        "  |w- pass word with |csignal|w. from quiet places only. walls\n"
        "    have wires in them sometimes.|n\n"
        "  |w- people on corners hear things. |crecruit|w them if you must,\n"
        "    but |cjudge|w them first, and learn to look before you trust\n"
        "    the judging. not every ear is yours. some can be bought\n"
        "    back (|cflip|w). none can be returned.|n\n"
        "  |w- the bolt-hole west of here has cots and a kettle. somebody\n"
        "    keeps it nice. ask yourself who.|n\n"
        "  |w- every lens you |csabotage|w is a street that forgets you.\n"
        "    the crew fixes them oldest-first. so there is always work.|n\n"
        "  |w- the queue pays legs. |ccarry|w for the broker, |cdeliver|w,\n"
        "    don't get checked. earn enough and she sells clean |cpapers|w.|n\n"
        "  |w- the lamp-mender has |cerrands|w for careful people. do the\n"
        "    first one. the last one is worth more than it pays.|n\n"
        "  |w- the broker sells more than legs-work to people she knows.\n"
        "    a coat that muffles. a pocket that lies. |clist|w, when your\n"
        "    standing with the right people is more than nothing.|n\n"
        "  |w- what a circle keeps, it keeps in a brick (|cstash|w),\n"
        "    somewhere dark, once. choose the somewhere well, and\n"
        "    remember when you sign anything: section c has an\n"
        "    address line.|n"
        "\n\n"
        "Beneath, in different hands: initials, dates, and one line pressed "
        "hard enough to break the chalk: |wthey write it down. so can we.|n"
    )
    chalk.locks.add("get:false()")
    chalk.db.get_err_msg = "The wall declines to come along."

    # The honeypot's hidden device: not described in the room (a concealed
    # device is exactly the case principle 9's described-devices-exist rule
    # does not cover — the room isn't promising it; the Ministry is hiding
    # it). `observe` only surfaces it at a very practiced skill, `forge`
    # refuses to work near it, and the sweep can reach past the chalk mark
    # on the door.
    seam = create_object(
        "typeclasses.objects.Sensor",
        key="a hairline seam in the conduit",
        aliases=["seam", "conduit"],
        location=rooms["bolthole"],
    )
    seam.db.desc = (
        "Where the old valve conduit meets the ceiling, the cement has been "
        "re-pointed — neatly, recently, and only there. Behind the seam, "
        "something very small is very patient."
    )
    seam.db.sensitivity = 1
    seam.db.active = True
    seam.db.concealed = True
    seam.locks.add("get:false()")
    seam.db.get_err_msg = "The ceiling declines to be examined by touch."
    # Concealed means concealed: not in the room listing, not lookable.
    # `observe` at a practiced enough skill is the only in-fiction reveal
    # (it scans contents in code, which no view lock touches) — playtest
    # caught the seam standing in the open under "You see:".
    seam.locks.add("view:false()")

    # The listening trade (v0.5): two informants on the same crooked street.
    # One of them is what they seem. Their loyalties are set here, in code,
    # which is the only registry that will ever hold them.
    mender = create_object(
        "typeclasses.npcs.Informant",
        key="the lamp-mender",
        location=rooms["alley"],
    )
    mender.tags.add("errand_giver", category="grid")
    mender.db.loyalty = "street"
    mender.db.desc = (
        "A stooped figure with a satchel of parts, forever half-way up a "
        "ladder under one of the alley's dead lamps. The lamps stay dead. "
        "The lamp-mender stays informed."
    )
    mender.db.demeanor = (
        "Their hands are steady on the dead screen, and they have never "
        "once filed the maintenance form. Whatever they serve, it files "
        "nothing."
    )
    mender.db.react_calm = (
        "{npc} taps a dead lamp, listens to it, and seems satisfied."
    )
    mender.db.react_noticed = (
        "{npc} glances at {name} from the ladder, and the glance is an "
        "inventory."
    )
    mender.db.react_hot = (
        "{npc} begins packing the satchel, without hurry and without "
        "missing anything."
    )

    vendor = create_object(
        "typeclasses.npcs.Informant",
        key="the tea vendor",
        location=rooms["alley"],
    )
    vendor.db.loyalty = "ministry"
    vendor.db.desc = (
        "A folding table, a battered urn, small glasses in rows straighter "
        "than the alley deserves. The tea is good and the prices are kind, "
        "which in Sector 9 is its own kind of question."
    )
    vendor.db.demeanor = (
        "They remember every order. Every order, every face, every time. "
        "Kindness with a memory like that is being paid for by someone."
    )
    vendor.db.react_calm = (
        "{npc} pours a glass unasked and nudges it forward. On the house."
    )
    vendor.db.react_noticed = (
        "{npc} smiles at {name} with real warmth and remembers everything "
        "about the moment."
    )
    vendor.db.react_hot = (
        "{npc} polishes an already-clean glass, angled slightly toward "
        "{name}."
    )

    # The broker (v0.6, ADR 0008): the courier trade's one visible node.
    # She stands in the ration queue because the queue is the only place in
    # Sector 9 where standing still for hours is above suspicion.
    broker = create_object(
        "typeclasses.npcs.Citizen",
        key="the broker",
        aliases=["broker", "woman with the string bag"],
        location=rooms["queue"],
    )
    broker.tags.add("courier_broker", category="grid")
    broker.db.desc = (
        "A middle-aged woman with a string bag, holding a place in line she "
        "never advances. The bag has held the same three turnips for as "
        "long as anyone can remember. People drift near her, adjust a coat "
        "or a parcel, and drift away carrying slightly different weight. "
        "Ask her to |ccarry|n something, if your legs are honest."
    )
    broker.db.react_calm = (
        "{npc} recounts the queue ahead of her, arriving as always at a "
        "number that does not require her to move."
    )
    broker.db.react_noticed = (
        "{npc} adjusts her string bag so it hangs between herself and {name}."
    )
    broker.db.react_hot = (
        "{npc} becomes, with no visible transition, a tired woman holding "
        "turnips who has never met anyone in her life."
    )
    # The broker's second shelf (v0.10): black-market gear, shown only to
    # citizens the underground already knows.
    broker.tags.add("vendor", category="grid")
    broker.db.stock_underground = ["dampener", "pocket"]

    # The requisitions clerk (v0.10): state issue, logged with pleasure.
    requisitions = create_object(
        "typeclasses.npcs.Citizen",
        key="the requisitions clerk",
        location=rooms["hall"],
    )
    requisitions.tags.add("vendor", category="grid")
    requisitions.db.stock = ["badge", "cuff"]
    requisitions.db.desc = (
        "A side window of the Assignment Hall counter, and in it a clerk "
        "surrounded by grey boxes with excellent labels. State issue: "
        "badges, monitors, the small apparatus of being legible. |cList|n "
        "the stock; every issue is recorded, which is not a warning, "
        "citizen, it is a service."
    )
    requisitions.db.react_calm = (
        "{npc} aligns a grey box with the edge of the counter, restoring a "
        "symmetry only they had noticed was broken."
    )
    requisitions.db.react_noticed = (
        "{npc} looks from {name} to the requisition ledger, as if "
        "estimating a size."
    )
    requisitions.db.react_hot = (
        "{npc} slides the ledger two centimeters further from the window."
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
