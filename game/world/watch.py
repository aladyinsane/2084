"""
The Watch: detainment, release, and the district alert level.

Spans characters, rooms, and scripts, so it lives here rather than on a
typeclass (docs/engineering/architecture.md). Every consequence in this module
is non-lethal by decision (ADR 0006) and telegraphed by design (principle 3).

A dev-facing trace of every Watch action goes to the server log with the
prefix "watchlog:" — ADR 0004 promised us debuggability the fiction doesn't
have. The trace is not visible in-game and is not part of the game's truth.
"""

from evennia.server.models import ServerConfig
from evennia.utils import logger
from evennia.utils.search import search_object_by_tag

from commands.detention import DetainedCmdSet
from world import tuning

ALERT_KEY = "sector9_alert"


def holding_cell():
    rooms = search_object_by_tag("holding_cell", category="grid")
    return rooms[0] if rooms else None


def release_point():
    rooms = search_object_by_tag("release_point", category="grid")
    return rooms[0] if rooms else None


def get_alert():
    return ServerConfig.objects.conf(ALERT_KEY, default=0)


def set_alert(value):
    value = max(0, min(tuning.ALERT_MAX, value))
    ServerConfig.objects.conf(ALERT_KEY, value=value)
    return value


def add_record_note(char, note):
    """Open an incident in the citizen's file (the real ADR 0005 record layer
    replaced the v0.2 string-list stub here)."""
    from world import records

    records.add_record(char, note, author="Ministry of Order", kind="incident")


def is_detained(char):
    return bool(char.tags.get("detained", category="status"))


def detain(char, reason="routine sweep"):
    """Take a citizen into custody: cmdset swap + relocation (ADR 0006)."""
    cell = holding_cell()
    if not cell or is_detained(char) or not char.has_account:
        return False

    char.tags.add("detained", category="status")
    char.db.detained_wait = 0
    add_record_note(char, f"DETAINED: {reason}.")
    set_alert(get_alert() + 1)
    logger.log_info(
        f"watchlog: detain {char.key} (exposure {char.db.exposure}) — {reason}"
    )

    if char.location:
        char.location.msg_contents(
            f"Two officers of the Watch converge on {char.key} without breaking "
            "stride. There is no struggle. There is nowhere a struggle would go.",
            exclude=(char,),
        )
    char.msg(
        "|rA hand closes on your shoulder.|n\n"
        "Two officers of the Watch stand on either side of you. Neither is "
        "looking at you; they are looking at where you will be walking. "
        "The trip to the Ministry of Order is quiet and very short."
    )
    char.move_to(cell, quiet=True, move_type="detained")
    char.cmdset.add(DetainedCmdSet, persistent=True)
    char.execute_cmd("look")
    return True


def release(char, note="Released.", farewell=None):
    """Return a citizen to the street, changed."""
    char.cmdset.remove(DetainedCmdSet)
    char.tags.remove("detained", category="status")
    char.db.detained_wait = 0
    char.db.exposure = tuning.RELEASE_EXPOSURE
    add_record_note(char, note)
    logger.log_info(f"watchlog: release {char.key} — {note}")

    char.msg(
        farewell
        or "The door opens. Nobody tells you to leave; the open door is the "
        "entire communication."
    )
    destination = release_point()
    if destination:
        char.move_to(destination, quiet=True, move_type="released")
        char.msg(
            "|=mYou are returned to the Assignment Hall. The clerk does not "
            "look up. Your file is one incident longer, and for the moment, "
            "the Grid knows exactly where you are.|n"
        )
        char.execute_cmd("look")
    return True
