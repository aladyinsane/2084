"""
Hands-on orientation (v0.15): the Wing teaches by making a citizen do the
verb, not just by describing it. The mechanic is deliberately placeless —
the first time a citizen ever runs one of the core verbs, wherever they
happen to be, the Grid reacts once. The Wing simply arranges to be the
likeliest place that first time happens; nobody who skips it is worse
taught for having found the verbs on their own (ten-persona playtest:
the min-maxer who skipped orientation still did fine).
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
}


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
