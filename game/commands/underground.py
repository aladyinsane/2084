"""
The grind verbs (v0.6, ADR 0008): sabotage and couriering.

Neither is taught by the Orientation Wing — the chalk in Tunnel B carries
the curriculum, as it does for every verb the Ministry would rather you not
have. Both pay the underground, whose ledger nobody can subpoena.
"""

from evennia import Command

from world import tuning


def _broker_here(room):
    if not room:
        return None
    for obj in room.contents:
        if obj.tags.get("courier_broker", category="grid"):
            return obj
    return None


class CmdSabotage(Command):
    """
    Put a watching device out of its misery.

    Usage:
      sabotage <device>

    A skill like any other: the first attempts go badly for most, and a
    failed attempt is exactly the kind of thing that ends up in a file.
    Done well, the device dies quietly, the underground hears who did it,
    and a street gets a little darker, until the maintenance crew works
    its way down the backlog, because the Ministry repairs what citizens
    report broken, and the Ministry reports these itself.
    """

    key = "sabotage"
    locks = "cmd:all()"
    help_category = "the underground"

    def func(self):
        from world import underground

        caller = self.caller
        room = caller.location
        if not room:
            return
        target_name = (self.args or "").strip()
        if not target_name:
            caller.msg("Usage: sabotage <device>")
            return
        targets = underground.sabotage_targets(room, caller)
        target = caller.search(
            target_name, candidates=targets, quiet=True
        )
        target = target[0] if target else None
        if not target:
            caller.msg(
                "Nothing here answers to that, nothing live you can find, "
                "anyway. Dead screens don't need your help."
            )
            return

        success, room_dark, pay = underground.do_sabotage(caller, target)
        if not success:
            caller.msg(
                "|rThe housing gives, then bites back|n: a contact you "
                "didn't see closes a circuit you didn't know was there. The "
                "device is fine. Somewhere, a fault report files itself, "
                "with a timestamp, from this room."
            )
            caller.send_prompt()
            return
        caller.msg(
            f"A shim, a twist, a held breath. {target.key} dies without "
            "drama: the diode just stops pretending to be a star."
        )
        if room_dark:
            caller.msg(
                "|gAnd the room changes.|n Nothing you could point to; the "
                "sum of it. Nothing here is watching now."
            )
        caller.msg(
            f"|=mSabotage {caller.skill('sabotage')}. The underground "
            f"credits you {pay}: standing with {tuning.UNDERGROUND} "
            f"{(caller.db.influence or {}).get(tuning.UNDERGROUND, 0)}.|n"
        )
        from world import circle_projects, propaganda

        circle_projects.check(caller, "sabotage")
        propaganda.record("sabotage")


class CmdCarry(Command):
    """
    Carry a parcel for the queue.

    Usage:
      carry          - hear what runs are going
      carry <tier>   - take one (quiet / street / bright / gate)

    The broker in the ration queue always has something that needs to be
    somewhere, and never says what. Pay scales with how watched the drop
    is. Being papers-checked, detained, or scanned at a gate while carrying
    ends the run the way you'd expect: the parcel becomes evidence, and
    the fact of it becomes an entry.
    """

    key = "carry"
    locks = "cmd:all()"
    help_category = "the underground"

    def func(self):
        from world import underground

        caller = self.caller
        broker = _broker_here(caller.location)
        if not broker:
            caller.msg(
                "Nobody here has anything that needs carrying. The ration "
                "queue is where errands find their legs."
            )
            return
        if underground.current_job(caller):
            tier = underground.current_job(caller)
            dest, _, drop = tuning.COURIER_JOBS[tier]
            caller.msg(
                f"You are already carrying. The drop is at {dest}: {drop}. "
                "One parcel at a time; you are not a cart."
            )
            return

        tier = (self.args or "").strip().lower()
        if tier not in tuning.COURIER_JOBS:
            lines = [
                f"{broker.key} looks through you while reciting, to no one:"
            ]
            for key, (dest, pay, _) in tuning.COURIER_JOBS.items():
                lines.append(
                    f" - |c{key}|n: something to {dest}. "
                    f"Worth {pay} to the right people."
                )
            lines.append(
                "|=mTake one with |ccarry <tier>|n|=m. Deliver with "
                "|cdeliver|n|=m at the drop. Don't get checked.|n"
            )
            standing = (caller.db.influence or {}).get(tuning.UNDERGROUND, 0)
            lines.append(
                f"|=mThe right people put you at {standing}. No ledger "
                "says so, which is the point.|n"
            )
            caller.msg("\n".join(lines))
            return

        dest, pay, drop = underground.accept_job(caller, tier)
        caller.msg(
            f"{broker.key} hands you a paper-wrapped parcel in the course "
            "of apparently adjusting their coat.\n"
            f"|=mThe drop: {dest}, {drop}. Worth {pay}. You were never "
            "here, which is true of everyone in this queue.|n"
        )


class CmdDeliver(Command):
    """
    Make the drop.

    Usage:
      deliver

    Only works at the destination, only with the parcel still on you.
    Sometimes what you carried turns out to have been worth considerably
    more than the quote; the underground shares when that happens, which
    is more than the Ministry has ever done.
    """

    key = "deliver"
    locks = "cmd:all()"
    help_category = "the underground"

    def func(self):
        from world import underground

        caller = self.caller
        result = underground.deliver(caller)
        if isinstance(result, str):
            caller.msg(result)
            return
        total, jackpot = result
        caller.msg(
            "The handoff takes four seconds and looks like two strangers "
            "failing to apologize to each other. The parcel is gone from "
            "your hands and, more importantly, from your story."
        )
        if jackpot:
            caller.msg(
                "|gLater, word reaches you: whatever that was, somebody "
                "needed it badly.|n The underground shares."
            )
        caller.msg(
            f"|=mCouriering {caller.skill('couriering')}. Standing with "
            f"{tuning.UNDERGROUND} "
            f"{(caller.db.influence or {}).get(tuning.UNDERGROUND, 0)} "
            f"(+{total}).|n"
        )


class CmdWord(Command):
    """
    Ask around about your own reputation.

    Usage:
      word

    No ledger holds this: the underground doesn't write things down. Ask
    somewhere it's safe to ask, and word finds its way to you the same
    way it finds its way anywhere: mouth to ear, corner to corner.
    """

    key = "word"
    aliases = ["rumor", "reputation"]
    locks = "cmd:all()"
    help_category = "the underground"

    def func(self):
        from world import underground

        caller = self.caller
        vis = getattr(caller.location, "visibility", 0)
        if vis > tuning.SHADOW_LADDER_MAX_VISIBILITY:
            caller.msg(
                "Not here. Not where anyone's watching you ask."
            )
            return
        standing, tier, next_tier, threshold = underground.shadow_standing(caller)
        if next_tier:
            caller.msg(
                f"Word on the street: you're {tier}. "
                f"A little more, and you're {next_tier}."
            )
        else:
            caller.msg(
                f"Word on the street: you're {tier}. Nobody says what "
                "comes after that, out loud."
            )


class CmdPapers(Command):
    """
    Buy clean papers.

    Usage:
      papers

    The underground's other trade: for those who have run enough errands,
    a fresh set of papers that make you, briefly, a much less interesting
    person. Bought from the broker, priced in the standing you earned.
    """

    key = "papers"
    locks = "cmd:all()"
    help_category = "the underground"

    def func(self):
        from world import underground

        caller = self.caller
        broker = _broker_here(caller.location)
        if not broker:
            caller.msg(
                "Papers change hands where the queue stands. Find the broker."
            )
            return
        err = underground.buy_papers(caller)
        if err:
            caller.msg(err)
            return
        caller.msg(
            f"{broker.key} palms you a documents wallet still warm from "
            "somewhere. Inside: you, but duller. A citizen nobody would "
            "look at twice.\n"
            "|=mThe heat comes off you like a coat coming off.|n"
        )
        caller.send_prompt()
