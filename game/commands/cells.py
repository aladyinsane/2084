"""
The underground verbs (v0.5, principle 6): cells, signals, and informants.

None of these are taught by the Orientation Wing. The chalk in Tunnel B
teaches them, which is the correct classroom: every one of these verbs
either requires a dead zone or gets safer in one, and every one of them
creates something a confession could later spend.
"""

from evennia import Command

from world import tuning


def _dead_zone(room):
    return bool(room) and getattr(room, "is_dead_zone", lambda: False)()


def _informant_here(caller, name):
    from typeclasses.npcs import Informant

    target = caller.search(name, quiet=True)
    target = target[0] if target else None
    if not target or not isinstance(target, Informant):
        return None
    return target


class CmdCell(Command):
    """
    Your cell: the people who know your name and shouldn't.

    Usage:
      cell                     - who you are in this with
      cell form <name>         - found a cell (only where nothing watches)
      cell invite <citizen>    - invite someone present (same condition)
      cell join                - accept an invitation (same condition)
      cell leave               - walk away (the file you already share stays shared)

    A cell is not a guild. There is no roster the Grid can read, no hall,
    no banner. There are only people who trusted each other somewhere dark —
    and everything the Ministry ever learns about a cell, it learns from
    one of them.
    """

    key = "cell"
    locks = "cmd:all()"
    help_category = "the grid"

    def func(self):
        from world import cells

        caller = self.caller
        args = (self.args or "").strip()
        action, _, rest = args.partition(" ")
        action = action.lower()

        if not action:
            self.show_status()
            return
        if action == "form":
            self.do_form(rest)
        elif action == "invite":
            self.do_invite(rest)
        elif action == "join":
            self.do_join()
        elif action == "leave":
            self.do_leave()
        else:
            caller.msg("Usage: cell [form <name> | invite <citizen> | join | leave]")

    def show_status(self):
        from world import cells

        caller = self.caller
        slug = cells.cell_of(caller)
        if not slug:
            invite = caller.db.cell_invite
            if invite:
                caller.msg(
                    "You carry an invitation nobody wrote down: "
                    f"|w{cells.cell_name(invite)}|n. Accept it (|ccell join|n) "
                    "somewhere nothing watches, or let it stay a thing that "
                    "never happened."
                )
            else:
                caller.msg(
                    "You are in this alone, which the Ministry would call "
                    "correct citizenship."
                )
            return
        members = cells.members_of(slug)
        lines = [
            f"|wCell: {cells.cell_name(slug)}|n "
            "(a name that appears in no registry the Grid admits to)"
        ]
        for member in sorted(members, key=lambda m: m.key):
            here = "|gon the Grid|n" if member.sessions.count() else "|=melsewhere|n"
            you = " (you)" if member is self.caller else ""
            lines.append(f" - {member.key}{you} — {here}")
        lines.append(
            "|=mEach name on this list can end every other name on it. "
            "That is what a cell is.|n"
        )
        caller.msg("\n".join(lines))

    def do_form(self, name):
        from world import cells

        caller = self.caller
        if not _dead_zone(caller.location):
            caller.msg(
                "Not here. A cell is founded where nothing watches, or it "
                "is founded in a file."
            )
            return
        slug, err = cells.form(caller, name)
        if err:
            caller.msg(err)
            return
        caller.msg(
            f"In the dark, with no witnesses worth the word, "
            f"|w{cells.cell_name(slug)}|n begins to exist. It has one member "
            "and no evidence. Keep it that way as long as you can.\n"
            "|=mInvite others here with |ccell invite <citizen>|n|=m — "
            "they must be standing where you are standing: nowhere.|n"
        )

    def do_invite(self, name):
        from world import cells

        caller = self.caller
        slug = cells.cell_of(caller)
        if not slug:
            caller.msg("You have no cell to invite anyone into.")
            return
        if not _dead_zone(caller.location):
            caller.msg("Not here. Invitations are made where nothing watches.")
            return
        target = caller.search(name)
        if not target:
            return
        from typeclasses.characters import Character

        if not isinstance(target, Character):
            caller.msg(
                f"{target.key} is not someone whose silence you can own. "
                "Citizens only."
            )
            return
        if cells.cell_of(target):
            caller.msg(f"{target.key} already belongs to somebody's risk.")
            return
        target.db.cell_invite = slug
        caller.msg(
            f"You put it to {target.key} in the fewest words it has ever "
            "been put in."
        )
        target.msg(
            f"|c{caller.key} leans close|n and offers you a name: "
            f"|w{cells.cell_name(slug)}|n. No paper changes hands; that is "
            "the entire attraction. |=mAccept with |ccell join|n|=m, here or "
            "in any place this dark. Or don't, and this never happened.|n"
        )

    def do_join(self):
        from world import cells

        caller = self.caller
        slug = caller.db.cell_invite
        if not slug:
            caller.msg("Nobody has offered you a name to join.")
            return
        if not _dead_zone(caller.location):
            caller.msg("Not here. Accept it where nothing watches, or not at all.")
            return
        err = cells.join(caller, slug)
        caller.db.cell_invite = None
        if err:
            caller.msg(err)
            return
        others = [m.key for m in cells.members_of(slug) if m is not caller]
        caller.msg(
            f"You are now part of |w{cells.cell_name(slug)}|n, alongside "
            f"{', '.join(sorted(others)) if others else 'no one, anymore'}. "
            "\n|=mPass word with |csignal <message>|n|=m — safe from quiet "
            "places, less so from watched ones. And understand the "
            "arithmetic: everything the cell does, every member can "
            "eventually be made to sign for.|n"
        )

    def do_leave(self):
        from world import cells

        caller = self.caller
        slug = cells.leave(caller)
        if not slug:
            caller.msg("You are not in a cell.")
            return
        caller.msg(
            f"You stop being part of {cells.cell_name(slug)}. The others "
            "will notice the way one notices weather. What you already "
            "know, you still know — and so does anyone who ever signs a "
            "form about it."
        )


class CmdSignal(Command):
    """
    Pass word to your cell.

    Usage:
      signal <message>

    Chalk shapes, folded papers, a cough with a rhythm to it. Reaches every
    member currently on the Grid, wherever they are. From quiet places
    (visibility 1 or less) the routes are safe; from watched ones, walls
    have wires in them sometimes, and an intercepted signal joins your file
    whether or not the Ministry ever decodes it.
    """

    key = "signal"
    locks = "cmd:all()"
    help_category = "the grid"

    def func(self):
        from world import cells

        caller = self.caller
        message = (self.args or "").strip()
        if not cells.cell_of(caller):
            caller.msg("You have no one to signal. A cell comes first.")
            return
        if not message:
            caller.msg("Usage: signal <message>")
            return
        cells.send_signal(caller, message)


class CmdRecruit(Command):
    """
    Bring an informant into the cell's confidence.

    Usage:
      recruit <someone>

    Some citizens hear things: menders, vendors, people whose work keeps
    them on corners. Recruited, they pass word to your cell — who was
    taken, when the street goes quiet. It is done in quiet places, and it
    is a bet: you are trusting that the person who listens for you does
    not also listen for someone else. Read them first (|csound|n), if you
    can read at all.
    """

    key = "recruit"
    locks = "cmd:all()"
    help_category = "the grid"

    def func(self):
        from world import cells

        caller = self.caller
        slug = cells.cell_of(caller)
        if not slug:
            caller.msg("Recruit them into what? A cell comes first.")
            return
        vis = getattr(caller.location, "visibility", 0)
        if vis > tuning.RECRUIT_MAX_VISIBILITY:
            caller.msg(
                "Not under this much light. Approaches are made on quiet "
                "corners."
            )
            return
        target = _informant_here(caller, self.args)
        if not target:
            caller.msg(
                "They hear you out, blink slowly, and develop a sudden "
                "excellent memory for your face. Not everyone is in the "
                "listening trade."
            )
            return
        if target.db.recruited_by == slug:
            caller.msg(f"{target.key} already listens for you. Allegedly.")
            return
        if target.db.recruited_by:
            caller.msg(
                f"{target.key} declines with an economy of words that "
                "suggests the position is filled."
            )
            return
        target.db.recruited_by = slug
        caller.msg(
            f"{target.key} listens, looks at the middle distance for a "
            "while, and names no price, which is either loyalty or the "
            "first installment of something.\n"
            "|=mThey will pass word to your cell — if word is what they "
            "actually deal in.|n"
        )


class CmdSound(Command):
    """
    Take the measure of an informant.

    Usage:
      sound <someone>

    Loyalty is not written on a face, but faces leak. What you get depends
    entirely on how well you have learned to look (the |cobserve|n skill):
    most citizens get nothing; a practiced eye reads demeanor; a trained
    one reads the truth.
    """

    key = "sound"
    locks = "cmd:all()"
    help_category = "the grid"

    def func(self):
        caller = self.caller
        target = _informant_here(caller, self.args)
        if not target:
            caller.msg("They are exactly what they appear to be, or you can't tell.")
            return
        skill = caller.skill("observation")
        if skill < tuning.OBSERVE_TIER_STATUS:
            caller.msg(
                f"You watch {target.key} for as long as you dare. They are "
                "a person, standing there. You have learned nothing, "
                "including how much there was to learn."
            )
        elif skill < tuning.OBSERVE_TIER_DETAIL:
            caller.msg(
                f"You watch {target.key} the way you have learned to watch "
                f"rooms.\n|=m{target.db.demeanor}|n\n"
                "That is all the face will give you at your level of craft."
            )
        else:
            if target.db.loyalty == "ministry":
                caller.msg(
                    f"You assemble {target.key} like a form with a field "
                    "out of place: the attention that never quite rests, "
                    "the questions shaped like small talk.\n"
                    "|rThey are the Ministry's. Whatever they hear, "
                    "someone else reads.|n"
                )
            else:
                caller.msg(
                    f"You assemble {target.key} slowly, and the pieces "
                    "agree with each other.\n"
                    "|gThey are what they seem: the street's, and "
                    "nobody's else.|n"
                )
        caller.improve_skill("observation")


class CmdFlip(Command):
    """
    Buy an informant out of the Ministry's service.

    Usage:
      flip <someone>

    A plant can be turned — everyone in the listening trade has a price,
    and the Ministry's stipend is famously late. It costs standing with the
    Ministry of Commerce (ration chits are the only currency that never
    asks questions), and it requires knowing *for certain* what you are
    buying: flip someone you have misread and you have just introduced
    yourself to the Watch.
    """

    key = "flip"
    locks = "cmd:all()"
    help_category = "the grid"

    def func(self):
        from world import cells, records

        caller = self.caller
        target = _informant_here(caller, self.args)
        if not target:
            caller.msg("There is nothing there to flip.")
            return
        if caller.skill("observation") < tuning.OBSERVE_TIER_DETAIL:
            caller.msg(
                "You do not know what they are, which means you do not "
                "know what you would be buying. Learn to look first."
            )
            return
        if target.db.loyalty != "ministry":
            caller.msg(
                f"{target.key} hears the offer out and looks almost "
                "offended. They were never anyone's but the street's. "
                "Save the chits."
            )
            return
        if not caller.spend_influence("Ministry of Commerce", tuning.FLIP_COST):
            caller.msg(
                f"The price is {tuning.FLIP_COST} standing with the "
                "Ministry of Commerce, and you do not have it. Loyalty is "
                "a commodity; commodities are prepaid."
            )
            return
        target.db.loyalty = "street"
        caller.msg(
            f"Chits change hands in a doorway. {target.key} weighs them, "
            "weighs something less countable, and nods once.\n"
            "|gWhat they hear is yours now. What they already reported "
            "stays reported — files do not un-happen.|n"
        )
