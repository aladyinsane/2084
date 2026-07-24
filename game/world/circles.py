"""
Circles: the trust layer (principle 6 — betrayal outguns everything).

A circle is a small conspiracy of citizens: formed where nothing watches,
named only among its members, and held together by nothing the Grid can
confiscate. Membership is a Tag (category "circle"); the registry of circles
lives in ServerConfig. There is no circle object to seize — which is the
point, and also why the only way into a circle's business is a member's
mouth.

(Renamed from "cells" in v0.7: the first human playtest found the collision
with the Watch's holding cell genuinely confusing, and the holding cell had
the word first.)

Everything the Ministry learns about circles, it learns the way it learns
everything: from a form somebody signed (Section C, in detention), from an
intercepted signal, or from a source it planted early and waters patiently.
"""

import random
import time

from evennia.server.models import ServerConfig
from evennia.utils import logger
from evennia.utils.search import search_object_by_tag

from world import tuning

REGISTRY_KEY = "sector9_circles"
MEMBER_TAG_CATEGORY = "circle"


# --- registry and membership ------------------------------------------------


def _registry():
    return ServerConfig.objects.conf(REGISTRY_KEY, default={}) or {}


def _save_registry(reg):
    ServerConfig.objects.conf(REGISTRY_KEY, value=reg)


def slugify(name):
    return "-".join((name or "").strip().lower().split())


def circle_of(char):
    """The slug of the circle this character belongs to, or None."""
    tags = char.tags.get(category=MEMBER_TAG_CATEGORY, return_list=True)
    return tags[0] if tags else None


def circle_name(slug):
    return _registry().get(slug, {}).get("name", slug)


def members_of(slug):
    """All citizen characters in a circle (online or not)."""
    from typeclasses.characters import Character

    return [
        obj
        for obj in search_object_by_tag(slug, category=MEMBER_TAG_CATEGORY)
        if isinstance(obj, Character)
    ]


def online_members(slug):
    return [m for m in members_of(slug) if m.sessions.count()]


def form(char, name):
    """Found a new circle. Caller must be circle-less; the room must be dead."""
    slug = slugify(name)
    if not slug:
        return None, "A circle needs a name its members can whisper."
    if circle_of(char):
        return None, "You are already somebody's risk. One circle per citizen."
    reg = _registry()
    if slug in reg:
        return None, (
            "That name is already chalked somewhere. Choose one the "
            "walls haven't heard."
        )
    reg[slug] = {"name": name.strip(), "founded": time.time()}
    _save_registry(reg)
    char.tags.add(slug, category=MEMBER_TAG_CATEGORY)
    logger.log_info(f"watchlog: (unknown to the Watch) circle formed: {slug}")
    return slug, None


def join(char, slug):
    reg = _registry()
    if slug not in reg:
        return "Whatever you were invited to has stopped existing."
    if circle_of(char):
        return "You are already somebody's risk. One circle per citizen."
    char.tags.add(slug, category=MEMBER_TAG_CATEGORY)
    return None


def _dissolve_if_empty(slug):
    """Last member out: registry entry goes; the cache spills where it is."""
    if members_of(slug):
        return
    reg = _registry()
    reg.pop(slug, None)
    _save_registry(reg)
    cache = cache_of(slug)
    if cache:
        for item in list(cache.contents):
            item.move_to(cache.location, quiet=True, move_type="spilled")
        cache.delete()


def leave(char):
    """Leave a circle; dissolve the registry entry if it empties."""
    slug = circle_of(char)
    if not slug:
        return None
    char.tags.remove(slug, category=MEMBER_TAG_CATEGORY)
    _dissolve_if_empty(slug)
    return slug


# --- the stash (v0.11) ------------------------------------------------------

CACHE_TAG_CATEGORY = "circle_cache"


def cache_of(slug):
    """The circle's cache object, or None."""
    caches = search_object_by_tag(slug, category=CACHE_TAG_CATEGORY)
    return caches[0] if caches else None


def establish_cache(char, room):
    """
    First stash establishes the cache: a loose brick, a hollow pipe,
    a place you'd have to know. Invisible to everyone — members included;
    knowing where it is IS the membership. One cache per circle.
    """
    from evennia import create_object

    slug = circle_of(char)
    cache = create_object(
        "typeclasses.objects.Object",
        key="a place you'd have to know",
        location=room,
    )
    cache.tags.add(slug, category=CACHE_TAG_CATEGORY)
    cache.locks.add("view:false();get:false()")
    cache.db.desc = "A loose brick. A hollow pipe. You'd have to know."
    logger.log_info(
        f"watchlog: (unknown to the Watch) circle '{slug}' cached at {room.key}"
    )
    return cache


# --- signals ----------------------------------------------------------------


def send_signal(char, message):
    """
    Pass word to the circle: chalk shapes, folded papers, a cough with a
    rhythm. Reaches every member currently on the Grid. Safe from quiet
    places; from watched ones, the wall sometimes has a wire in it.
    Returns True if the signal was intercepted.
    """
    from world import records

    slug = circle_of(char)
    recipients = [m for m in online_members(slug) if m is not char]
    for member in recipients:
        member.msg(
            f'|cA mark left where you know to look:|n "{message}" '
            f"|=m(it is {char.key}'s hand)|n"
        )
    char.msg(
        f"You pass the word along the quiet routes"
        f"{' to no one currently reachable' if not recipients else ''}."
    )

    vis = getattr(char.location, "visibility", 0)
    excess = vis - tuning.SIGNAL_SAFE_VISIBILITY
    if excess > 0 and random.random() < excess * tuning.SIGNAL_INTERCEPT_PER_VIS:
        records.add_record(
            char,
            "Transmitted coded signals on a monitored band; "
            "content under analysis",
        )
        char.gain_exposure(tuning.SIGNAL_INTERCEPT_EXPOSURE)
        char.msg(
            "|rSomewhere between here and there, something copied it.|n "
            "You don't know what it made of the message. You know that it "
            "kept it."
        )
        char.send_prompt()
        logger.log_info(f"watchlog: signal intercepted from {char.key} (vis {vis})")
        return True
    return False


# --- betrayal (Section C) ---------------------------------------------------


def betray(confessor):
    """
    Section C, completed: every other member of the confessor's circle gains
    an incident and a hot file. The confessor's membership does not survive
    their signature. Returns the number of citizens named.
    """
    from world import records

    slug = circle_of(confessor)
    if not slug:
        return 0
    named = [m for m in members_of(slug) if m is not confessor]
    for member in named:
        records.add_record(
            member, "Named as an associate in a recorded confession"
        )
        member.gain_exposure(tuning.CELL_NAMED_EXPOSURE)
    # Section C has an address line (v0.11): the van goes to the brick
    # first. A confessed circle's stash is confiscated wholesale.
    cache = cache_of(slug)
    if cache:
        for item in list(cache.contents):
            item.delete()
        cache.delete()
        for member in online_members(slug):
            if member is not confessor:
                member.msg(
                    "|rWord comes the way bad word does: the brick is "
                    "empty.|n Everything the circle kept, the Ministry "
                    "keeps now."
                )
        logger.log_info(f"watchlog: circle '{slug}' cache confiscated")
    # ADR 0013: a running project doesn't survive a completed Section C
    # either -- the pot forfeits whole, same reasoning as the stash above.
    from world import circle_projects

    if circle_projects.project_of(slug):
        circle_projects.abandon(slug)
        for member in online_members(slug):
            if member is not confessor:
                member.msg(
                    "|rAnd whatever the circle was building toward: "
                    "gone with it.|n"
                )
    confessor.tags.remove(slug, category=MEMBER_TAG_CATEGORY)
    _dissolve_if_empty(slug)
    logger.log_info(
        f"watchlog: Section C complete — {confessor.key} named {len(named)} "
        f"member(s) of '{slug}'"
    )
    return len(named)


# --- informants -------------------------------------------------------------


def notify_detention(char):
    """
    Word travels: if the detained citizen's circle has a *street-loyal*
    informant, the informant tips the members still outside. A Ministry
    plant, naturally, reports nothing — silence is part of the service.
    """
    slug = circle_of(char)
    if not slug:
        return
    from typeclasses.npcs import Informant

    tippers = [
        npc
        for npc in Informant.objects.all()
        if npc.db.recruited_by == slug and npc.db.loyalty == "street"
    ]
    if not tippers:
        return
    tipper = tippers[0]
    for member in online_members(slug):
        if member is char:
            continue
        member.msg(
            f"|cWord finds you the way word does:|n they took {char.key}. "
            f"{tipper.key.capitalize()} saw the van. Decide what "
            f"{char.key} knows, and decide what you'd sign."
        )


def collect_informant_reports():
    """
    The sweep collects from its sources. Every recruited Ministry plant
    files on one member of the circle that trusted it, on a cooldown — a
    slow bleed a citizen only notices in their dossier, if they look.
    """
    from typeclasses.npcs import Informant
    from world import records

    now = time.time()
    for npc in Informant.objects.all():
        slug = npc.db.recruited_by
        if not slug or npc.db.loyalty != "ministry":
            continue
        if now - (npc.db.last_report or 0) < tuning.INFORMANT_REPORT_COOLDOWN:
            continue
        members = members_of(slug)
        if not members:
            continue
        npc.db.last_report = now
        target = random.choice(members)
        records.add_record(
            target,
            "Reported by a source: associates with an unregistered circle",
        )
        target.gain_exposure(tuning.INFORMANT_REPORT_EXPOSURE)
        logger.log_info(
            f"watchlog: informant {npc.key} filed on {target.key} "
            f"(circle '{slug}')"
        )
