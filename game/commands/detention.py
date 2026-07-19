"""
Detainment: the cmdset swap that IS the game state (ADR 0001's argument,
ADR 0006's ladder). While detained you cannot move, fight, or leave; you can
look, speak, read your own file, and choose between confessing, waiting, and
demanding — and the interrogation room is a scene, not a death screen.
"""

from evennia import CmdSet, Command, default_cmds

from world import tuning


class CmdConfess(Command):
    """
    Confess.

    Usage:
      confess
      confess names   - complete Section C (Associates)
      confess alone   - strike Section C and sign only for yourself

    To what? That has never mattered. A confession is a formality the file
    requires; the file is patient, and so are the officers. Citizens who
    have associates will find the form already knows how many lines
    Section C needs — only the confirmation is theirs to give, or refuse.
    """

    key = "confess"
    locks = "cmd:all()"
    help_category = "detention"

    def func(self):
        from world import circles, watch

        caller = self.caller
        slug = circles.circle_of(caller)
        mode = (self.args or "").strip().lower()

        if not slug:
            # No associates: the v0.2 confession, unchanged.
            caller.msg(
                "You confess. The words arrange themselves surprisingly "
                "easily — the form on the table is mostly pre-printed, and "
                "your part is small.\n\nThe officer countersigns without "
                "reading it."
            )
            watch.release(
                caller,
                note="Confession recorded (contents unspecified). Released.",
                farewell=(
                    "Processing is brisk. A stamp, a second stamp, the "
                    "return of your bootlaces. The door opens."
                ),
            )
            return

        blanks = len(circles.members_of(slug)) - 1
        if mode not in ("names", "alone"):
            caller.msg(
                "The officer slides the form across. Your part is small and "
                "mostly pre-printed — except |wSection C: Associates|n, "
                f"which has been ruled with |r{blanks}|n blank line"
                f"{'s' if blanks != 1 else ''}. Not a guess. A count.\n\n"
                "The officer waits. |cconfess names|n completes Section C. "
                "|cconfess alone|n strikes it out and signs only for "
                "yourself, which the Ministry will remember you chose."
            )
            return

        if mode == "names":
            named = circles.betray(caller)
            caller.msg(
                "You fill Section C in the neat hand of a person being "
                f"cooperative. {named} name{'s' if named != 1 else ''}, "
                "block capitals, no crossings-out.\n\nThe officer "
                "countersigns, and for one professional instant looks at "
                "you the way you will now always suspect people of "
                "looking at you."
            )
            watch.release(
                caller,
                note="Confession recorded; Section C complete. Released "
                "with the Ministry's appreciation.",
                farewell=(
                    "Processing is immediate. Both stamps land together. "
                    "Someone has already brought your coat."
                ),
            )
        else:
            watch.add_record_note(
                caller, "Declined to complete Section C of confession."
            )
            caller.msg(
                "You draw one line through Section C and sign your own "
                "part only.\n\nThe officer looks at the strike-through "
                "longer than they looked at you, initials the margin, and "
                "files the form somewhere that sounds further away than "
                "the drawer it goes into."
            )
            watch.release(
                caller,
                note="Confession recorded; Section C returned blank. "
                "Released under continued observation.",
                farewell=(
                    "Processing is unhurried in a way that is doing it on "
                    "purpose. Eventually: a stamp, your bootlaces, the door."
                ),
                exposure=tuning.RELEASE_EXPOSURE_UNCOOPERATIVE,
            )


class CmdWait(Command):
    """
    Wait.

    Usage:
      wait

    The Ministry of Order has more detainees than officers, and the Grid's
    attention is a finite resource. Patience is not innocence, but it is
    sometimes indistinguishable from it in the paperwork.
    """

    key = "wait"
    locks = "cmd:all()"
    help_category = "detention"

    WAITS = [
        "You wait. The light does not change. Somewhere down the corridor, a "
        "door closes.",
        "You wait. Footsteps approach, slow at the door, and continue past.",
        "You wait. You become aware of the sound the light itself makes.",
        "You wait. Someone has scratched four thin lines into the bench. You "
        "decide not to add the fifth.",
        "You wait so long that the room stops being frightening, which is "
        "somehow worse.",
    ]

    def func(self):
        from world import watch

        caller = self.caller
        count = (caller.db.detained_wait or 0) + 1
        caller.db.detained_wait = count
        if count >= tuning.WAIT_RELEASE_TURNS:
            caller.msg(
                "A clerk appears at the grille — not an officer, a clerk. They "
                "check a list, check you against it, and frown at the "
                "discrepancy between how interesting you are and how much "
                "space you occupy."
            )
            watch.release(
                caller,
                note="Held pending review; released for lack of interest.",
            )
        else:
            caller.msg(self.WAITS[(count - 1) % len(self.WAITS)])


class CmdDemand(Command):
    """
    Demand.

    Usage:
      demand

    Demand release, a hearing, an explanation, anything. The Ministry has a
    procedure for demands. The procedure is a drawer.
    """

    key = "demand"
    locks = "cmd:all()"
    help_category = "detention"

    def func(self):
        from world import watch

        caller = self.caller
        # Demanding restarts the clock. It felt good, though.
        caller.db.detained_wait = 0
        watch.add_record_note(caller, "Was unruly in detention.")
        caller.msg(
            "You demand release, loudly and with several supporting arguments."
            "\n\nAn officer arrives, listens with genuine courtesy, writes "
            "|wone|n word on a form, and files the form in a drawer that you "
            "slowly realize is not connected to anything."
        )


class DetainedCmdSet(CmdSet):
    """
    Replaces the normal command surface while detained. Movement, channels,
    and every civic verb are gone; what remains is the room, your voice, your
    file, and three ways to spend time.
    """

    key = "detained"
    priority = 120
    mergetype = "Replace"
    no_exits = True

    def at_cmdset_creation(self):
        self.add(CmdConfess())
        self.add(CmdWait())
        self.add(CmdDemand())
        # The permitted remainder of a citizen's vocabulary. `help` is in it
        # — the first human playtest was detained with no idea what to do,
        # and a room you can't ask questions in is a bug, not a mood.
        self.add(default_cmds.CmdLook())
        self.add(default_cmds.CmdSay())
        self.add(default_cmds.CmdQuit())
        self.add(default_cmds.CmdHelp())
        from commands.dossier import CmdDossier

        self.add(CmdDossier())
