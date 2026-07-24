"""
File-based help entries (v0.7): the two core stats and the game's shape,
written in the world's voice. Read via settings.FILE_HELP_ENTRY_MODULES.
The first human playtest found that the game's two most important numbers
had no helpfiles at all.
"""

# The category used to be "the grid" — identical to this module's own
# "the grid" entry key. Evennia's CmdHelp resolves an exact category name
# before an exact topic key, so `help the grid` (the thing nomatch.py and
# half the Wing's placards tell citizens to type) silently returned a
# command-category listing instead of the entry, for everyone, always
# (round-two playtest finding 1). Renamed so the entry itself is reachable.
_CATEGORY = "sector 9"

# (The "grade" entry moved into CmdGrade's docstring in v0.13 — a command
# named `grade` shadows a file entry of the same key, so the explanation
# lives with the verb now.)
HELP_ENTRY_DICTS = [
    {
        "key": "exposure",
        "aliases": ["exp", "heat"],
        "category": _CATEGORY,
        "text": """
            The number in your prompt where |wdown is good|n.

            Exposure (0-100) is how interesting you currently are to the
            state. It is not experience points. There are no experience
            points. There is only how much of you the Grid has recently
            seen.

            |wIt rises|n when you move through watched places (see |chelp
            visibility|n), pass scanners, speak on the public channel, and
            generally exist where the apparatus can notice you existing.

            |wIt falls|n slowly with time; faster through visible
            usefulness (|cwork|n), through being stopped, checked and
            cleared, and through attending assemblies when convened.

            |wWhat it costs you:|n above 20 or so, the Watch's sweeps may
            select you: a papers check if you are middling, detainment at
            50 and up. Patrols detain the hot on sight. Citizens read your
            heat off your face and act accordingly.

            Below 20 you are, in the Grid's own idiom, nobody. Being
            nobody is a strategy. Some say it is the only one.
        """,
    },
    {
        "key": "sweep",
        "aliases": ["watch", "the watch"],
        "category": _CATEGORY,
        "text": """
            The Watch does not see everyone at once. It samples.

            On an interval, the Grid rolls each connected citizen above a
            floor of Exposure (|chelp exposure|n) for its attention. The
            chance of being picked rises with how interesting you currently
            are: nobody, at the bottom, is never sampled at all; the
            hottest citizens are caught most tries, not every try. A sweep
            that selects you means a papers check if you are middling,
            detainment if you are hot enough. Patrols work the same
            arithmetic in the street, in real time, on sight.

            It is never certain and never omniscient: the Grid is
            probability, not a scripted trap. What *is* certain: the trend.
            Exposure that keeps climbing keeps the odds climbing with it,
            and the prompt tells you which way it is moving before
            anything does.
        """,
    },
    {
        "key": "visibility",
        "aliases": ["vis"],
        "category": _CATEGORY,
        "text": """
            The other number in your prompt: how watched |wthis place|n is,
            from 0 to 5.

            0 means nothing watches here at all: no fixtures, no ambient
            coverage. 5 is the checkpoint: white light, no shadows,
            architecture designed to be seen in. Entering a place accrues
            Exposure in proportion to its visibility, plus whatever live
            devices hang there (|cobserve|n counts them; attention is a
            skill).

            Visibility belongs to the room, not to you, and it does not
            change on its own, though devices can break, and broken
            devices watch nothing.

            A place showing Vis 0 with nothing live in it is a |wdead
            zone|n: sweeps cannot select you there, and certain things
            become possible that are possible nowhere else. Whether a
            place that *looks* like a dead zone actually is one is a
            separate question, and the careful have ways of checking.
        """,
    },
    {
        "key": "the grid",
        # "sector 9" used to be an alias here too, until it became this
        # module's shared category name — keeping both would only move
        # finding 1's bug one alias sideways instead of fixing it.
        "aliases": ["2084", "basics"],
        "category": _CATEGORY,
        "text": """
            2084 is not a game about killing things; there is nothing to
            kill and no experience points for killing it. It is a game
            about being |wseen|n, being |wwritten down|n, and what you are
            willing to do about the file that results.

            The short version of everything:

            - Your prompt shows |wGrade|n (the Grid's one-number opinion of
              you; |chelp grade|n), |wVisibility|n (how watched this place
              is; |chelp visibility|n), and |wExposure|n (how interesting
              you are; |chelp exposure|n).
            - Your |cdossier|n (or |cscore|n) is what the state says you
              are. It is not necessarily what happened. That distinction
              is most of the game.
            - Sanctioned life: |creport|n for a function, |cwork|n your
              post, earn |cstanding|n, |cpetition|n corrections,
              |capply|n for clearance, attend assemblies when the
              loudspeakers say so.
            - The rest of life is taught elsewhere. Rooms explain
              themselves; read them. The Orientation Wing (east of the
              Assignment Hall) is the sanctioned classroom. Sector 9 has
              at least one other, for those who look down as well as up.
        """,
    },
    {
        "key": "standing",
        "aliases": ["influence"],
        "category": _CATEGORY,
        "text": """
            The other ledger, separate from |wExposure|n (|chelp
            exposure|n) and separate from your |wgrade|n (|chelp grade|n).
            Standing is kept per institution: the Ministry of Records, the
            Ministry of Commerce, whichever office last had a use for you.

            |wHow it's earned:|n |cwork|n your assigned post, complete an
            institution's errands (|cerrands|n), or |creport|n and take a
            function in the first place. Each pays standing with the
            institution that asked.

            |wHow it's spent:|n |cpetition|n (amend your file),
            |cforge|n's sanctioned cousin; |capply|n for clearance; the
            Annex's other services. Spending standing never lowers your
            grade: merit is separate and lifetime (|chelp grade|n).

            |wWhere to see it:|n |cdossier|n lists "Standing with
            institutions" once you've earned any. Nothing is owed you
            before then; a citizen with no standing has simply not yet
            been useful to anyone in particular.
        """,
    },
    {
        "key": "gridwide",
        "aliases": ["grid", "pub"],
        "category": _CATEGORY,
        "text": """
            The one public channel: |cgridwide <message>|n, heard sector-
            wide by anyone listening. Monitored, of course: speaking on
            it costs exposure, same as speaking into a microphone the
            state also owns. Cheap for a whisper, not for a habit.
        """,
    },
]
