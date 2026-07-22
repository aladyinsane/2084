"""
The errand verb (v0.9): one command for the whole quest surface, per the
command-surface audit. Completion happens through verbs you already have.
"""

from evennia import Command


def _givers_here(room):
    if not room:
        return []
    return [
        obj
        for obj in room.contents
        if obj.tags.get("errand_giver", category="grid")
    ]


class CmdErrands(Command):
    """
    Errands: work that finds you, if you stand near the right people.

    Usage:
      errands              - your current errand, or what's offered here
      errands take <name>  - accept an errand from someone present
      errands drop         - abandon your current errand (it is noticed)

    Some citizens have uses for legs and eyes. Each offer names its risk;
    what it doesn't say, you should ask yourself. Errands complete through
    the things you'd do anyway — walking, working, watching, carrying —
    and one at a time is all anyone will trust you with.
    """

    key = "errands"
    # "quests" is what the rest of the genre calls these; the alias costs
    # nothing and answers the first thing a MUD veteran will type (v0.13).
    aliases = ["errand", "quests", "quest"]
    locks = "cmd:all()"
    help_category = "the grid"

    def func(self):
        from world import errands

        caller = self.caller
        args = (self.args or "").strip()
        action, _, rest = args.partition(" ")
        action = action.lower()

        if action == "take":
            self.do_take(rest.strip().lower())
        elif action == "drop":
            title = errands.drop(caller)
            if title:
                caller.msg(
                    f"You let \"{title}\" quietly stop being your problem. "
                    "Somewhere, someone recalibrates their opinion of your "
                    "legs."
                )
            else:
                caller.msg("You have no errand to drop.")
        else:
            self.show(rest or None)

    def show(self, _ignored=None):
        from world import errands

        caller = self.caller
        state = errands.current(caller)
        lines = []
        if state:
            spec = errands.ERRANDS[state["key"]]
            lines.append(
                f"|wYour errand: {spec['title']}|n (for {spec['giver']})"
            )
            lines.append(f"  {spec['brief']}")
            if spec["type"] == "visit":
                remaining = [
                    r for r in spec["rooms"] if r not in state["progress"]
                ]
                lines.append(
                    f"  |=mStill to walk: {', '.join(remaining) or 'nowhere — almost done'}.|n"
                )
            elif spec["type"] == "shifts":
                lines.append(
                    f"  |=mShifts: {len(state['progress'])} of {spec['count']}.|n"
                )
        else:
            lines.append("You are running no one's errand.")

        offered = False
        for giver in _givers_here(caller.location):
            for key, spec in errands.offers_for(giver.key, char=caller):
                if state and state["key"] == key:
                    continue
                offered = True
                lines.append(
                    f"\n|c{giver.get_display_name(caller)}|n offers "
                    f"|w{spec['title']}|n (|cerrands take {key}|n):"
                )
                lines.append(f"  {spec['brief']}")
                lines.append(f"  |=mRisk: {spec['risk']}|n")
        if not offered and not state:
            lines.append(
                "Nobody here has work for you. People with uses for legs "
                "and eyes tend to stand where legs pass and eyes linger."
            )
        caller.msg("\n".join(lines))

    def do_take(self, key):
        from world import errands

        caller = self.caller
        if not key:
            caller.msg("Take which? |cerrands|n lists what's offered here.")
            return
        spec = errands.ERRANDS.get(key)
        givers = [g.key for g in _givers_here(caller.location)]
        if not spec or spec["giver"] not in givers:
            caller.msg(
                "Nobody here is offering that. Offers are made in person; "
                "everything in Sector 9 is."
            )
            return
        err = errands.take(caller, key)
        if err:
            caller.msg(err)
            return
        caller.msg(
            f"|w[Errand accepted: {spec['title']}]|n\n{spec['brief']}\n"
            f"|=mRisk: {spec['risk']}|n"
        )
        from world.onboarding import acknowledge_first_use

        acknowledge_first_use(caller, "errands")
