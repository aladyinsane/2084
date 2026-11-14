"""
Escalating circle projects (v0.21, ADR 0013): a joint pot that only pays
out whole, to a circle that finishes what it started.

Casing and the Run are solo-completable, one stage at a time, by any
member acting alone -- the circle's shared tally, not a personal one.
The Split is the one moment that demands two members in the same dead
zone at once, the same idiom errands.py's "Four Hands" joint_visit
already established. A completed Section C confession (circles.betray)
wipes an active project the same way it already wipes the stash: no
partial credit, no salvage.

State lives in the ServerConfig registry, keyed by circle slug, same
shape circles.py itself uses -- a project is circle property, not
character property, so it survives any single member logging off.
"""

import time

from evennia.server.models import ServerConfig
from evennia.utils import logger

from world import tuning

REGISTRY_KEY = "sector9_circle_projects"

_STAGES = [
    {
        "key": "casing",
        "title": "Casing",
        "event": "sabotage",
        "threshold": tuning.PROJECT_CASING_THRESHOLD,
        "advance": (
            "|w[{circle}: Casing complete.]|n Dead screens between you, and "
            "nobody's file says whose hands. The Run is next: courier work, "
            "however many of you it takes."
        ),
    },
    {
        "key": "run",
        "title": "The Run",
        "event": "deliver",
        "threshold": tuning.PROJECT_RUN_THRESHOLD,
        "advance": (
            "|w[{circle}: The Run complete.]|n The legs are done. What's "
            "left needs two of you in the same dark place at the same "
            "time: the Split."
        ),
    },
    {
        "key": "split",
        "title": "The Split",
        "event": "arrival",
        "threshold": None,
        "advance": None,
    },
]


def _registry():
    return ServerConfig.objects.conf(REGISTRY_KEY, default={}) or {}


def _save_registry(reg):
    ServerConfig.objects.conf(REGISTRY_KEY, value=reg)


def project_of(slug):
    """The active project state for a circle, or None."""
    return _registry().get(slug)


def start(char):
    """
    Begin a project for the caller's circle. Returns an error string, or
    None on success. One project at a time, same idiom as the stash and
    char.db.errand.
    """
    from world import circles

    slug = circles.circle_of(char)
    if not slug:
        return "A project needs a circle first."
    reg = _registry()
    if slug in reg:
        return "This circle already has a project running. Finish it, or lose it."
    reg[slug] = {"stage": 0, "progress": 0, "started": time.time()}
    _save_registry(reg)
    logger.log_info(
        f"watchlog: (unknown to the Watch) circle project started: {slug}"
    )
    return None


def abandon(slug):
    """Wipe a circle's active project outright (Section C's forfeiture)."""
    reg = _registry()
    if slug in reg:
        del reg[slug]
        _save_registry(reg)
        logger.log_info(f"watchlog: circle project forfeited: {slug}")


def status_lines(slug):
    """Human-readable status for `circle project`, or None if there's none running."""
    proj = project_of(slug)
    if not proj:
        return None
    stage = _STAGES[proj["stage"]]
    if stage["key"] == "split":
        return [
            f"|wProject: {stage['title']}|n -- casing and the run are both "
            "done. What's left: two of you, the same dead zone, the same "
            "moment."
        ]
    return [
        f"|wProject: {stage['title']}|n -- {proj['progress']} of "
        f"{stage['threshold']}, the circle's tally, not just yours."
    ]


def _advance(slug, reg):
    proj = reg[slug]
    stage = _STAGES[proj["stage"]]
    proj["stage"] += 1
    proj["progress"] = 0
    reg[slug] = proj
    _save_registry(reg)
    from world import circles

    if stage["advance"]:
        message = stage["advance"].format(circle=circles.circle_name(slug))
        for member in circles.online_members(slug):
            member.msg(message)


def _complete(slug):
    from world import circles

    members = circles.members_of(slug)
    reg = _registry()
    reg.pop(slug, None)
    _save_registry(reg)
    if not members:
        return
    share = tuning.PROJECT_PAYOUT // len(members)
    if share <= 0:
        return
    name = circles.circle_name(slug)
    for member in members:
        member.gain_standing_and_credits(tuning.UNDERGROUND, share)
    for member in circles.online_members(slug):
        member.msg(
            f"|g[{name}: The Split.]|n Whatever it was, it's done, and "
            f"it's yours now: {share} standing with {tuning.UNDERGROUND} "
            f"and {share} credits apiece, no ledger anywhere that says so."
        )
    logger.log_info(
        f"watchlog: (unknown to the Watch) circle project completed: "
        f"{slug}, {share} each to {len(members)} member(s)"
    )


def check(char, event):
    """
    The single dispatch point for Casing and the Run: verbs report events
    here, the same idiom errands.check already uses. Cheap no-op for a
    citizen without a circle, a circle with no running project, or a
    project not currently waiting on this event.
    """
    from world import circles

    slug = circles.circle_of(char)
    if not slug:
        return
    reg = _registry()
    proj = reg.get(slug)
    if not proj:
        return
    stage = _STAGES[proj["stage"]]
    if stage["event"] != event:
        return
    proj["progress"] += 1
    # ADR 0015: the room of whoever most recently moved the tally, kept for
    # informant reports to reference -- an act, not an actor, since the
    # tally itself is already shared across the whole circle.
    if char.location:
        proj["last_event_room"] = char.location.key
    reg[slug] = proj
    _save_registry(reg)
    if proj["progress"] >= stage["threshold"]:
        _advance(slug, reg)
    else:
        char.msg(
            f"|=m[{stage['title']}: {proj['progress']} of "
            f"{stage['threshold']} -- the circle's tally, not just "
            "yours.]|n"
        )


def check_arrival(char, room):
    """
    The Split: two circle members in the same dead zone at once. Called
    from the room's own at_object_receive (rooms.py), on every arrival --
    symmetric by construction, since a project is circle state, not
    per-character state: whichever member arrives second completes it for
    everyone, so there's no need to also re-check whoever was already
    standing there (unlike errands.py's per-character joint_visit, which
    needs that second check because each character tracks its own errand
    completion separately).
    """
    from world import circles

    slug = circles.circle_of(char)
    if not slug or not room:
        return
    proj = project_of(slug)
    if not proj or _STAGES[proj["stage"]]["key"] != "split":
        return
    if not getattr(room, "is_dead_zone", lambda: False)():
        return
    mates_here = [
        obj
        for obj in room.contents
        if obj is not char and circles.circle_of(obj) == slug
    ]
    if mates_here:
        _complete(slug)
