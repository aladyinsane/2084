"""
File-based help entries (v0.7): the two core stats and the game's shape,
written in the world's voice. Read via settings.FILE_HELP_ENTRY_MODULES.
The first human playtest found that the game's two most important numbers
had no helpfiles at all.
"""

# (The "grade" entry moved into CmdGrade's docstring in v0.13 — a command
# named `grade` shadows a file entry of the same key, so the explanation
# lives with the verb now.)
HELP_ENTRY_DICTS = [
    {
        "key": "exposure",
        "aliases": ["exp", "heat"],
        "category": "the grid",
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
            select you — a papers check if you are middling, detainment at
            50 and up. Patrols detain the hot on sight. Citizens read your
            heat off your face and act accordingly.

            Below 20 you are, in the Grid's own idiom, nobody. Being
            nobody is a strategy. Some say it is the only one.
        """,
    },
    {
        "key": "visibility",
        "aliases": ["vis"],
        "category": "the grid",
        "text": """
            The other number in your prompt: how watched |wthis place|n is,
            from 0 to 5.

            0 means nothing watches here at all — no fixtures, no ambient
            coverage. 5 is the checkpoint: white light, no shadows,
            architecture designed to be seen in. Entering a place accrues
            Exposure in proportion to its visibility, plus whatever live
            devices hang there (|cobserve|n counts them — attention is a
            skill).

            Visibility belongs to the room, not to you, and it does not
            change on its own — though devices can break, and broken
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
        "aliases": ["2084", "sector 9", "basics"],
        "category": "the grid",
        "text": """
            2084 is not a game about killing things; there is nothing to
            kill and no experience points for killing it. It is a game
            about being |wseen|n, being |wwritten down|n, and what you are
            willing to do about the file that results.

            The short version of everything:

            - Your prompt shows |wVis|n (how watched this place is; |chelp
              visibility|n) and |wExposure|n (how interesting you are;
              |chelp exposure|n).
            - Your |cdossier|n (or |cscore|n) is what the state says you
              are. It is not necessarily what happened. That distinction
              is most of the game.
            - Sanctioned life: |creport|n for a function, |cwork|n your
              post, earn standing, |cpetition|n corrections, |capply|n for
              clearance, attend assemblies when the loudspeakers say so.
            - The rest of life is taught elsewhere. Rooms explain
              themselves; read them. The Orientation Wing (east of the
              Assignment Hall) is the sanctioned classroom. Sector 9 has
              at least one other, for those who look down as well as up.
        """,
    },
]
