"""
The underground verbs (v0.5, principle 6): circles, signals, and informants.

None of these are taught by the Orientation Wing. The chalk in Tunnel B
teaches them, which is the correct classroom: every one of these verbs
either requires a dead zone or gets safer in one, and every one of them
creates something a confession could later spend.

(v0.7 renames, from the first human playtest: player "cells" are now
"circles" — the holding cell had the word first — and `sound` is now
`judge`, which says what it does.)
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


def _citizen_here(caller, name):
    from typeclasses.characters import Character

    target = caller.search(name, quiet=True)
    target = target[0] if target else None
    if not target or target is caller or not isinstance(target, Character):
        return None
    return target


class CmdCircle(Command):
    """
    Your circle: the people who know your name and shouldn't.

    Usage:
      circle                   - who you are in this with
      circle form <name>       - found a circle (only where nothing watches)
      circle invite <citizen>  - invite someone present (same condition)
      circle join              - accept an invitation (same condition)
      circle leave             - walk away (what you already share stays shared)

    A circle is not a guild. There is no roster the Grid can read, no hall,
    no banner. There are only people who trusted each other somewhere dark,
    and everything the Ministry ever learns about a circle, it learns from
    one of them.
    """

    key = "circle"
    locks = "cmd:all()"
    help_category = "the underground"

    def func(self):
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
            caller.msg(
                "Usage: circle [form <name> | invite <citizen> | join | leave]"
            )

    def show_status(self):
        from world import circles

        caller = self.caller
        slug = circles.circle_of(caller)
        if not slug:
            invite = caller.db.circle_invite
            if invite:
                caller.msg(
                    "You carry an invitation nobody wrote down: "
                    f"|w{circles.circle_name(invite)}|n. Accept it "
                    "(|ccircle join|n) somewhere nothing watches, or let it "
                    "stay a thing that never happened."
                )
            else:
                caller.msg(
                    "You are in this alone, which the Ministry would call "
                    "correct citizenship."
                )
            return
        members = circles.members_of(slug)
        lines = [
            f"|wCircle: {circles.circle_name(slug)}|n "
            "(a name that appears in no registry the Grid admits to)"
        ]
        for member in sorted(members, key=lambda m: m.key):
            here = "|gon the Grid|n" if member.sessions.count() else "|=melsewhere|n"
            you = " (you)" if member is self.caller else ""
            lines.append(f" - {member.key}{you}: {here}")
        lines.append(
            "|=mEach name on this list can end every other name on it. "
            "That is what a circle is.|n"
        )
        caller.msg("\n".join(lines))

    def do_form(self, name):
        from world import circles

        caller = self.caller
        if not _dead_zone(caller.location):
            caller.msg(
                "Not here. A circle is drawn where nothing watches, or it "
                "is drawn in a file."
            )
            return
        slug, err = circles.form(caller, name)
        if err:
            caller.msg(err)
            return
        caller.msg(
            f"In the dark, with no witnesses worth the word, "
            f"|w{circles.circle_name(slug)}|n begins to exist. It has one "
            "member and no evidence. Keep it that way as long as you can.\n"
            "|=mInvite others here with |ccircle invite <citizen>|n|=m, "
            "they must be standing where you are standing: nowhere.|n"
        )

    def do_invite(self, name):
        from world import circles

        caller = self.caller
        slug = circles.circle_of(caller)
        if not slug:
            caller.msg("You have no circle to invite anyone into.")
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
        if circles.circle_of(target):
            caller.msg(f"{target.key} already belongs to somebody's risk.")
            return
        target.db.circle_invite = slug
        caller.msg(
            f"You put it to {target.key} in the fewest words it has ever "
            "been put in."
        )
        target.msg(
            f"|c{caller.key} leans close|n and offers you a name: "
            f"|w{circles.circle_name(slug)}|n. No paper changes hands; that "
            "is the entire attraction. |=mAccept with |ccircle join|n|=m, "
            "here or in any place this dark. Or don't, and this never "
            "happened.|n"
        )

    def do_join(self):
        from world import circles

        caller = self.caller
        slug = caller.db.circle_invite
        if not slug:
            caller.msg("Nobody has offered you a name to join.")
            return
        if not _dead_zone(caller.location):
            caller.msg("Not here. Accept it where nothing watches, or not at all.")
            return
        err = circles.join(caller, slug)
        caller.db.circle_invite = None
        if err:
            caller.msg(err)
            return
        others = [m.key for m in circles.members_of(slug) if m is not caller]
        caller.msg(
            f"You are now part of |w{circles.circle_name(slug)}|n, alongside "
            f"{', '.join(sorted(others)) if others else 'no one, anymore'}. "
            "\n|=mPass word with |csignal <message>|n|=m, safe from quiet "
            "places, less so from watched ones. And understand the "
            "arithmetic: everything the circle does, every member can "
            "eventually be made to sign for.|n"
        )

    def do_leave(self):
        from world import circles

        caller = self.caller
        slug = circles.leave(caller)
        if not slug:
            caller.msg("You are not in a circle.")
            return
        caller.msg(
            f"You stop being part of {circles.circle_name(slug)}. The others "
            "will notice the way one notices weather. What you already "
            "know, you still know, and so does anyone who ever signs a "
            "form about it."
        )


class CmdSignal(Command):
    """
    Pass word to your circle.

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
    help_category = "the underground"

    def func(self):
        from world import circles

        caller = self.caller
        message = (self.args or "").strip()
        if not circles.circle_of(caller):
            caller.msg("You have no one to signal. A circle comes first.")
            return
        if not message:
            caller.msg("Usage: signal <message>")
            return
        circles.send_signal(caller, message)


class CmdRecruit(Command):
    """
    Bring an informant into the circle's confidence.

    Usage:
      recruit <someone>

    Some citizens hear things: menders, vendors, people whose work keeps
    them on corners. Recruited, they pass word to your circle: who was
    taken, when the street goes quiet. It is done in quiet places, and it
    is a bet: you are trusting that the person who listens for you does
    not also listen for someone else. |cjudge|n them first, if you can
    judge at all.
    """

    key = "recruit"
    locks = "cmd:all()"
    help_category = "the underground"

    def func(self):
        from world import circles

        caller = self.caller
        slug = circles.circle_of(caller)
        if not slug:
            caller.msg("Recruit them into what? A circle comes first.")
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
            "|=mThey will pass word to your circle, if word is what they "
            "actually deal in.|n"
        )


class CmdJudge(Command):
    """
    Take the measure of an informant, or a fellow citizen.

    Usage:
      judge <someone>

    Loyalty is not written on a face, but faces leak. What you get depends
    entirely on how well you have learned to look (the |cobserve|n skill).
    Against an informant: most citizens get nothing; a practiced eye reads
    demeanor; a trained one reads the truth. Against a fellow citizen the
    bar is higher: you are not reading a demeanor, you are reading whether
    their file remembers a Section C, and files remember for a long time
    (ADR 0010).
    """

    key = "judge"
    aliases = ["sound"]  # the old name, kept as a courtesy
    locks = "cmd:all()"
    help_category = "the underground"

    def func(self):
        caller = self.caller
        target = _informant_here(caller, self.args)
        if target:
            self._judge_informant(caller, target)
            return
        target = _citizen_here(caller, self.args)
        if not target:
            caller.msg("They are exactly what they appear to be, or you can't tell.")
            return
        self._judge_citizen(caller, target)

    @staticmethod
    def _judge_informant(caller, target):
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

    @staticmethod
    def _judge_citizen(caller, target):
        # ADR 0010: reading a citizen's actual file is a bigger claim than
        # reading an informant's demeanor, so the bar sits above the
        # informant tiers entirely rather than reusing OBSERVE_TIER_STATUS.
        if caller.skill("observation") < tuning.OBSERVE_TIER_REPUTATION:
            caller.msg(
                f"You watch {target.key} for as long as you dare. They are "
                "a person, standing there. You have learned nothing, "
                "including how much there was to learn."
            )
            caller.improve_skill("observation")
            return
        from world import records

        incidents = records.records_for(target, kind="incident", include_redacted=False)
        verdict = None
        for rec in reversed(incidents):  # most recent first
            if rec.tags.get("section_c_complete", category=records.BETRAYAL_TAG_CATEGORY):
                verdict = "complete"
                break
            if rec.tags.get("section_c_clean", category=records.BETRAYAL_TAG_CATEGORY):
                verdict = "clean"
                break
        if verdict == "complete":
            caller.msg(
                f"You assemble {target.key} slowly, and the pieces don't "
                "agree with each other.\n"
                "|rSection C, completed. Whatever they signed, someone "
                "else walked free on it.|n"
            )
        elif verdict == "clean":
            caller.msg(
                f"You assemble {target.key} slowly, and the pieces agree "
                "with each other.\n"
                "|gThey've been asked before, and kept faith.|n"
            )
        else:
            caller.msg(
                f"You watch {target.key} the way you have learned to "
                "watch people. Whatever their file holds, it isn't in "
                "their face."
            )
        caller.improve_skill("observation")


class CmdFlip(Command):
    """
    Buy an informant out of the Ministry's service.

    Usage:
      flip <someone>

    A plant can be turned: everyone in the listening trade has a price,
    and the Ministry's stipend is famously late. It costs standing with the
    Ministry of Commerce (ration chits are the only currency that never
    asks questions), and it requires knowing *for certain* what you are
    buying: flip someone you have misread and you have just introduced
    yourself to the Watch.
    """

    key = "flip"
    locks = "cmd:all()"
    help_category = "the underground"

    def func(self):
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
            "stays reported: files do not un-happen.|n"
        )


class CmdStash(Command):
    """
    The circle's cache: what you keep where nothing watches.

    Usage:
      stash                - where the cache is, and what's in it
      stash <item>         - put something in (establishes the cache if
                             the circle has none, only in a dead zone)
      stash take <item>    - take something out (at the cache)

    A loose brick, a hollow pipe: one hiding place per circle, invisible
    to anyone who doesn't already know, which is the only lock that has
    ever worked. Knowing where it is *is* the membership, and Section C
    has an address line. A confessed circle's stash belongs to the
    Ministry before the confessor's coat is returned.
    """

    key = "stash"
    locks = "cmd:all()"
    help_category = "the underground"

    def func(self):
        from world import circles

        caller = self.caller
        slug = circles.circle_of(caller)
        if not slug:
            caller.msg(
                "You have no circle, so you have no brick. Property is "
                "the second thing trust buys."
            )
            return
        args = (self.args or "").strip()
        cache = circles.cache_of(slug)

        if not args:
            self.show(cache)
            return
        if args.lower().startswith("take "):
            self.do_take(cache, args[5:].strip())
            return
        self.do_put(cache, args)

    def show(self, cache):
        caller = self.caller
        if not cache:
            caller.msg(
                "The circle keeps nothing yet. |cStash <item>|n somewhere "
                "truly unwatched, and it will start."
            )
            return
        where = cache.location.key if cache.location else "nowhere"
        items = [obj.key for obj in cache.contents]
        caller.msg(
            f"The circle's cache is at |w{where}|n. "
            + (
                f"In it: {', '.join(items)}."
                if items
                else "It is currently empty, which is also safe."
            )
        )

    def do_put(self, cache, item_name):
        from world import circles

        caller = self.caller
        item = caller.search(item_name, candidates=caller.contents)
        if not item:
            return
        room = caller.location
        if cache is None:
            if not _dead_zone(room):
                caller.msg(
                    "Not here. A cache begins somewhere nothing watches "
                    "at all."
                )
                return
            cache = circles.establish_cache(caller, room)
            caller.msg(
                "You find it almost without looking: a loose brick, a "
                "gap behind a pipe: a place you'd have to know. "
                "|=mThe circle has a cache now. Its members will know "
                "where by knowing you.|n"
            )
        if cache.location != room:
            caller.msg(
                f"The circle's brick is at {cache.location.key}, not here. "
                "One hiding place; that's what makes it one."
            )
            return
        item.move_to(cache, quiet=True, move_type="stashed")
        caller.msg(
            f"{item.key} goes where things go to not exist for a while."
        )

    def do_take(self, cache, item_name):
        caller = self.caller
        if not cache:
            caller.msg("The circle keeps nothing yet.")
            return
        if cache.location != caller.location:
            caller.msg(
                f"The brick is at {cache.location.key}. Things come out "
                "of it the way they went in: in person."
            )
            return
        item = caller.search(item_name, candidates=cache.contents)
        if not item:
            return
        item.move_to(caller, quiet=True, move_type="unstashed")
        caller.msg(f"{item.key} exists again, and is yours.")
