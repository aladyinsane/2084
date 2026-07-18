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

    To what? That has never mattered. A confession is a formality the file
    requires; the file is patient, and so are the officers.
    """

    key = "confess"
    locks = "cmd:all()"
    help_category = "detention"

    def func(self):
        from world import watch

        caller = self.caller
        caller.msg(
            "You confess. The words arrange themselves surprisingly easily — "
            "the form on the table is mostly pre-printed, and your part is "
            "small.\n\nThe officer countersigns without reading it."
        )
        watch.release(
            caller,
            note="Confession recorded (contents unspecified). Released.",
            farewell=(
                "Processing is brisk. A stamp, a second stamp, the return of "
                "your bootlaces. The door opens."
            ),
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
        # The permitted remainder of a citizen's vocabulary.
        self.add(default_cmds.CmdLook())
        self.add(default_cmds.CmdSay())
        self.add(default_cmds.CmdQuit())
        from commands.dossier import CmdDossier

        self.add(CmdDossier())
