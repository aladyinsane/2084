"""
The First Hour (v0.13): sequencing the existing surface.

The research (docs/research/the-first-hour.md) named the second half of the
learning-curve problem: everything arrives at once. Nothing here locks
anything — MUD veterans skip ahead by right — but the opening minutes now
stage what they show:

- `help`, bare, shows an abridged card until orientation is complete
  (the full index stays one `help all` away, and is the default after).
- `next` reads the citizen's actual state and names one sensible thing
  to do, in the Ministry's voice.
- `grade` (aliases the muscle-memory set: level, rank, merit) answers
  "am I leveling?" in three lines.
"""

from evennia import Command, default_cmds

_WING_HINTS = {
    "wing_ante": (
        "you're in the Antechamber. Type |cmap|n to see the sector for "
        "yourself, or ask the clerk beside you after |cerrands|n — they "
        "have a use for a citizen's legs."
    ),
    "wing_watched": (
        "you're in the Watched Life room. Type |cobserve|n right here — "
        "see what the room is showing you before you're told."
    ),
    "wing_file": (
        "you're in the File room. Type |cdossier|n to see your file for "
        "the first time."
    ),
    "wing_civic": (
        "you're in the Civic Life room. Type |cgrade|n to see where you "
        "stand on the ladder before you continue."
    ),
}


def _wing_hint(room):
    """The Wing-specific nudge for the room a citizen is standing in, if
    any — None outside the Wing, so the generic advice takes over."""
    if not room:
        return None
    for tag, hint in _WING_HINTS.items():
        if room.tags.get(tag, category="grid"):
            return hint
    return None


_ABRIDGED = """\
|w  THE PERMITTED FORMS OF ASSISTANCE (ABRIDGED)|n
|=m  Issued to citizens not yet through orientation. The full index
  is available with |chelp all|=m; nothing is withheld, only sequenced.|n

  |cnext|n      — the Grid's one suggestion for what to do now
  |clook|n      — read where you are (rooms are how the Grid explains itself)
  |cmap|n       — your own recollection of the sector
  |cdossier|n   — your file, as the Ministry keeps it
  |cgrade|n     — your civic grade and the next review
  |cerrands|n   — constructive uses for a citizen's legs, offered in person
  |creport|n    — be assigned your function (Assignment Hall counter)
  |cwork|n      — visible usefulness; it pays, and it cools
  |chelp <topic>|n — e.g. |chelp exposure|n, |chelp visibility|n

|=m  Orientation waits EAST of the Assignment Hall. Completing it is
  the fastest thing the Grid will ever credit you for.|n"""


class CmdHelpStaged(default_cmds.CmdHelp):
    """
    The permitted forms of assistance.

    Usage:
      help
      help <topic>
      help all

    Before orientation is complete, bare |whelp|n shows an abridged card
    of first-hour commands; |whelp all|n is always the full index, and
    after orientation bare |whelp|n is too. Nothing is ever locked.
    """

    def func(self):
        if self.topic.strip().lower() == "all":
            self.topic = ""
            return super().func()
        if not self.topic and not self.caller.db.oriented:
            self.caller.msg(_ABRIDGED)
            return
        return super().func()


class CmdNext(Command):
    """
    Ask the Grid what a citizen in your position would sensibly do now.

    Usage:
      next

    One suggestion at a time, drawn from your actual circumstances. The
    Grid is pleased to advise. The Grid is always pleased to advise.
    """

    key = "next"
    aliases = ["hint", "whatnow"]
    locks = "cmd:all()"
    help_category = "sector 9"

    def func(self):
        from world import errands, tuning

        caller = self.caller
        advice = self._advice(caller, errands, tuning)
        caller.msg(f"|=mCITIZEN ADVISORY (FORM 2-B):|n {advice}")

    @staticmethod
    def _advice(caller, errands, tuning):
        standing = caller.db.standing or {}
        # An active errand is always the first answer: finish what you hold.
        state = errands.current(caller)
        if state:
            spec = errands.ERRANDS.get(state["key"])
            if spec:
                return (
                    f"you hold an errand — |c{spec['title']}|n. "
                    f"{spec['brief']}"
                )
        if not caller.db.oriented:
            hint = _wing_hint(caller.location)
            if hint:
                return hint
            return (
                "complete your orientation. It waits EAST of the "
                "Assignment Hall, it is five rooms long, and the Grid "
                "credits it toward your first reclassification."
            )
        if not standing.get("function_key"):
            return (
                "you are unassigned. |creport|n at the Assignment Hall "
                "counter and the Grid will read your file and decide "
                "what you are."
            )
        if (caller.db.exposure or 0) >= tuning.HOT_EXPOSURE:
            return (
                "you have made yourself extremely interesting. Be "
                "visibly useful (|cwork|n), attend anything the "
                "loudspeakers convene, and let the figure fall before "
                "the Watch reads it."
            )
        # Errandless: point at a giver, preferring one in the room.
        here = [
            obj
            for obj in (caller.location.contents if caller.location else [])
            if obj.tags.get("errand_giver", category="grid")
            and errands.offers_for(obj.key, caller)
        ]
        if here:
            return (
                f"{here[0].get_display_name(caller)} has a use for you. "
                "Ask after |cerrands|n."
            )
        # Catalog order on purpose: the clerk's safe chain leads it, so a
        # brand-new citizen is pointed at the shallow end first.
        for key, spec in errands.ERRANDS.items():
            if errands.available_to(caller, key):
                return (
                    f"word is {spec['giver']} has a use for a citizen's "
                    "legs. Find them and ask after |cerrands|n."
                )
        # Round-two playtest finding 3: every path through this method
        # eventually lands here, and until now it never named an
        # alternative to the sanctioned catalog — a citizen who'd cleared
        # it had no signal that circles or the underground exist as real
        # options, not just flavor text. Catalog-first stays the design
        # (a brand-new citizen still sees the clerk's chain before this);
        # this only fires once there's nothing sanctioned left to offer.
        return (
            "you've done what the Grid asks, for now. |cwork|n your post, "
            "|clisten|n where citizens queue, and walk your |cmap|n if "
            "you want more of the same. Not everyone in Sector 9 answers "
            "to the Grid, though: the underground trades in |cpapers|n "
            "and |ccarry|n runs, and a |ccircle|n of trusted citizens "
            "plays by its own rules entirely. |chelp the grid|n says more."
        )


class CmdGrade(Command):
    """
    Your civic grade: the Grid's one-number opinion of your usefulness.

    Usage:
      grade

    Grades run from 6 (probationary — everyone starts here) down to 1.
    If you are used to levels: this is that, upside down, because the
    civil service was ranking people before games were.

    Merit drives it — everything the Grid has watched you earn: standing
    paid by the ministries, errands seen through, a function held,
    clearance granted, orientation completed. Merit is lifetime; spending
    standing at the Annex does not lower your grade. Losing your function
    does. What the Grid cannot see earns no merit at all, which some
    citizens consider the fairest price in Sector 9.
    """

    key = "grade"
    aliases = ["level", "rank", "merit"]
    locks = "cmd:all()"
    help_category = "sector 9"

    def func(self):
        from world import grades

        caller = self.caller
        points, nxt, threshold = grades.next_review(caller)
        lines = [
            f"|wCitizen, Grade {grades.grade_of(caller)}.|n "
            f"Merit on record: {points}."
        ]
        if nxt:
            lines.append(
                f"Review threshold for Grade {nxt}: {threshold} "
                f"({threshold - points} to go)."
            )
        else:
            lines.append("No further elevation is contemplated.")
        caller.msg("\n".join(lines))

        from world.onboarding import acknowledge_first_use

        acknowledge_first_use(caller, "grade")


class CmdLook(default_cmds.CmdLook):
    """
    Look at your location or an object.

    Usage:
      look
      look <obj>

    Same muscle-memory reasoning as `score` for `dossier` (v0.7): `x` is
    the near-universal MUD shorthand for examine, and round-two's playtest
    found it landing on nomatch's fuzzy-suggester instead of doing
    anything (harmless, but not useful).
    """

    aliases = default_cmds.CmdLook.aliases + ["x"]
