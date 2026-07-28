"""
Hands-on orientation (v0.15, extended v0.26 / ADR 0018): the Wing teaches by
making a citizen do the verb, not just by describing it. The mechanic is
deliberately placeless — the first time a citizen ever runs a tracked verb,
wherever they happen to be, the Grid reacts once. The Wing arranges to be the
likeliest place several of these first times happen (map/observe/dossier/
grade), but this set has grown well past the Wing's five rooms: the actual
answer to "does teaching reach the whole sector" is this dict's coverage, not
a bigger building. Nobody who skips the Wing is worse taught for having found
a verb on their own (ten-persona playtest: the min-maxer who skipped
orientation still did fine) — that principle is unchanged by ADR 0018, which
only changes what happens *inside* the Wing if a citizen chooses to walk it
(see rooms.py's `orients`-tag gate).
"""

_ACKNOWLEDGMENTS = {
    "map": (
        "|=mThe sector unfolds behind your eyes, dark and lit. Call it up "
        "again any time, |cmap|=m costs nothing, and the Ministry would "
        "rather you not get lost.|n"
    ),
    "observe": (
        "|=mThe skill of noticing the room noticing you. It sharpens with "
        "use, here and everywhere: you will never look at a room the "
        "same way again, which is the point.|n"
    ),
    "dossier": (
        "|=mYour file, on request, as promised. Ask for it whenever you "
        "want to know exactly what the Grid has decided about you.|n"
    ),
    "grade": (
        "|=mA number, standing in for a citizen. Ask again after anything "
        "that might have moved it: the Grid updates it whether you ask "
        "or not.|n"
    ),
    "errands": (
        "|=mWork found you, or you found it; the Grid does not distinguish. "
        "|cerrands|=m always shows what you're carrying and who else has "
        "uses for a citizen's legs.|n"
    ),
    "report": (
        "|=mThe first stamp. It will not be the last, and it will not be "
        "the strangest.|n"
    ),
    "work": (
        "|=mVisible usefulness, logged. Working takes a little heat off "
        "you every time, not just this one.|n"
    ),
    # v0.26 (ADR 0018): the acknowledgment set catches up to the verb
    # surface -- these all shipped after the original seven and never
    # got a first-use moment of their own until now.
    "listen": (
        "|=mThe queue says more than it means to. Nothing you hear here "
        "is official, which is exactly why it's worth hearing.|n"
    ),
    "petition": (
        "|=mThe sanctioned route: standing spent, a stamp applied, the "
        "past improved. The request itself joins the file, same as "
        "everything else.|n"
    ),
    "research": (
        "|=mMost of the archive is exactly as dull as it looks. Not all "
        "of it. |cresearch|=m again whenever you have standing to spend "
        "and patience to spare.|n"
    ),
    "apply": (
        "|=mThe Ministry will read your file, your function, and your "
        "ledger, in that order, and only the versions of them it has. "
        "|capply|=m again once your circumstances have improved.|n"
    ),
    "vouch": (
        "|=mA character reference, quietly filed. If they ever sign "
        "Section C, your name goes with theirs.|n"
    ),
    "unvouch": (
        "|=mYour name, taken back, standing returned in full. Nothing "
        "was ever written down.|n"
    ),
    "list": (
        "|=mWhat's for sale, and to whom. Not every counter shows every "
        "citizen the same shelf.|n"
    ),
    "buy": (
        "|=mThe want-ladder has a first rung. Every purchase is a trade, "
        "never a straight upgrade -- read the pitch before you spend.|n"
    ),
    "wear": (
        "|=mOne item per place it's worn. What you wear changes how the "
        "Grid reads you, in both directions.|n"
    ),
}


# ADR 0018: the Wing's own completion credit (rooms.py's `orients` tag) now
# requires having actually exercised these four, not just having walked the
# rooms that teach them. Kept separate from _ACKNOWLEDGMENTS's full key set
# on purpose -- growing the acknowledgment dict should never silently expand
# what orientation itself requires.
CORE_ORIENTATION_VERBS = {"map", "observe", "dossier", "grade"}


def has_completed_core_orientation(char):
    seen = char.db.first_use_verbs or set()
    return CORE_ORIENTATION_VERBS.issubset(seen)


def acknowledge_first_use(caller, verb):
    """
    Fire the one-time in-fiction reaction for a citizen's first-ever use of
    `verb`. Safe to call unconditionally from the end of a command's own
    func() — a no-op after the first time, or if `verb` isn't tracked.
    """
    seen = caller.db.first_use_verbs
    if seen is None:
        seen = set()
    if verb in seen:
        return
    seen.add(verb)
    caller.db.first_use_verbs = seen
    message = _ACKNOWLEDGMENTS.get(verb)
    if message:
        caller.msg(message)
