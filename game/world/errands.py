"""
Errands (v0.9): the quest system, generalized from the broker's pattern.

Design rules inherited from the command-surface audit and the fun research:

- **One verb** (`errands`) for browsing/taking/dropping. Completion happens
  through verbs the player already has — go somewhere, `work`, `observe`,
  `carry`/`deliver`, attend an assembly. The quest system *listens* to the
  game rather than adding quest-shaped actions to it.
- **Risk stated up front.** Every offer names its exposure shape the way
  the courier board names its tiers.
- **Chains end in something named**, not bare numbers — a commendation in
  your file, an introduction, a warning worth having.
- **The "nobody" questline exists**: the orientation clerk's chain is
  genuinely safe, so lying low is a campaign rather than an absence
  (fun-and-game-feel.md, dullness #1).

Data model: `char.db.errand = {"key": ..., "progress": [...]}` — one errand
at a time, like the courier board. Givers are NPCs tagged `errand_giver`
(category "grid"); the catalog maps giver key → offered errands. Event
hooks call `errands.check(char, event, **ctx)` from the relevant verbs.
"""

from evennia.utils import logger

from world import tuning

# The catalog. Rewards reference tuning sizes so the numbers stay in one
# place; prose is content and lives here.
#
# Types and their params / completion events:
#   visit:        rooms=[room keys]        <- check(char, "visit", room=...)
#   shifts:       count=N                  <- check(char, "shift")
#   observe_at:   room=key                 <- check(char, "observe", room=...)
#   deliver_tier: tier=key                 <- check(char, "deliver", tier=...)
#   attend:       (no params)              <- check(char, "attend")

ERRANDS = {
    # --- the orientation clerk: the "nobody" chain --------------------------
    "rounds": {
        "giver": "the orientation clerk",
        "title": "The Rounds",
        "brief": (
            "\"New citizens should know their sector. Present yourself at "
            "the Ration Queue, the Archive Annex, and Unity Plaza. You "
            "needn't do anything there. Being seen being ordinary is the "
            "whole exercise.\""
        ),
        "risk": "None to speak of. Walking is still legal.",
        "type": "visit",
        "rooms": ["Ration Queue", "Archive Annex", "Unity Plaza"],
        "reward_faction": "Ministry of Records",
        "reward_size": "small",
        "done": (
            "The clerk checks three boxes that were, you now see, already "
            "printed on a form about you."
        ),
        "next": "usefulness",
    },
    "usefulness": {
        "giver": "the orientation clerk",
        "title": "Visible Usefulness",
        "brief": (
            "\"Work suits a citizen. Three shifts, anywhere that will have "
            "you. The Grid finds the industrious restful to watch.\""
        ),
        "risk": "None. Work actively cools you.",
        "type": "shifts",
        "count": 3,
        "reward_faction": "Ministry of Records",
        "reward_size": "medium",
        "done": (
            "\"Three shifts,\" the clerk says, with the warmth of a "
            "stamped date. \"You are becoming legible.\""
        ),
        "next": "countable",
    },
    "countable": {
        "giver": "the orientation clerk",
        "title": "Countable",
        "brief": (
            "\"When the loudspeakers convene an assembly, be at the plaza "
            "when the roll completes. The Grid loves nothing the way it "
            "loves a countable citizen.\""
        ),
        "risk": "The plaza is watched (Vis 4), but attendance itself pays "
        "heat down.",
        "type": "attend",
        "reward_faction": "Ministry of Records",
        "reward_size": "medium",
        "commendation": "Commended: a model of civic reliability",
        "done": (
            "Later, the clerk finds you — or a form finds you, which is "
            "the same thing. A commendation has been entered in your "
            "file. It is the first thing in there you wanted."
        ),
    },
    # --- the lamp-mender: the careful people's chain ------------------------
    "look-closer": {
        "giver": "the lamp-mender",
        "title": "Look Closer",
        "brief": (
            "\"You want work? First learn to see. Stand in this alley and "
            "really |cobserve|n it. Tell me how many of these lamps are "
            "watching you back.\""
        ),
        "risk": "Low. Looking is not yet a crime either.",
        "type": "observe_at",
        "room": "Neon Alley",
        "reward_faction": tuning.UNDERGROUND,
        "reward_size": "small",
        "done": (
            "\"One,\" the lamp-mender says, before you speak. \"The dead "
            "one. Dead things make the best witnesses: everyone performs "
            "for them and nobody checks the tape.\" They seem satisfied "
            "with your eyes."
        ),
        "next": "legs",
    },
    "legs": {
        "giver": "the lamp-mender",
        "title": "Legs",
        "brief": (
            "\"The woman in the queue with the string bag. Take one of "
            "her street runs and see it through. She'll know I sent you. "
            "She won't say so. Neither will you.\""
        ),
        "risk": "A street run: watched ground, seizable cargo. Don't get "
        "checked.",
        "type": "deliver_tier",
        "tier": "street",
        "reward_faction": tuning.UNDERGROUND,
        "reward_size": "medium",
        "done": (
            "The lamp-mender doesn't look down from the ladder. \"Good "
            "legs.\" A pause, quieter: \"The bolt-hole under the "
            "tenements — you've seen the chalk. Look at who keeps it "
            "nice before you trust it. That's the whole lesson. That's "
            "everything I know.\""
        ),
        "next": "four-hands",
    },
    "four-hands": {
        "giver": "the lamp-mender",
        "title": "Four Hands",
        "brief": (
            "\"Some work needs four hands and zero witnesses. Be in "
            "Tunnel B with someone your circle trusts — both of you, at "
            "once, where the chalk is. What happens down there is the "
            "two of you knowing you both showed. That is the work.\""
        ),
        "risk": "The tunnel is dark; getting two people there quietly is "
        "the exercise. Requires a circle-mate present.",
        "type": "joint_visit",
        "room": "Tunnel B",
        "reward_faction": tuning.UNDERGROUND,
        "reward_size": "medium",
        "done": (
            "Nothing changes hands in Tunnel B; that was never the point. "
            "The point stands next to you, breathing the same dark. "
            "Later, the lamp-mender nods to you both, separately, on "
            "different days, so that it never happened all at once."
        ),
    },
}

_REWARD_SIZES = {
    "small": lambda: tuning.ERRAND_REWARD_SMALL,
    "medium": lambda: tuning.ERRAND_REWARD_MEDIUM,
}


# Chain bookkeeping: an errand that is another errand's "next" only opens
# once its prerequisite is done, and nothing repeats (a re-takeable
# commendation would be a farm, and the fiction agrees: the clerk's boxes
# are already ticked).
_PREREQ = {
    spec["next"]: key for key, spec in ERRANDS.items() if spec.get("next")
}


def done_list(char):
    return char.db.errands_done or []


def available_to(char, key):
    """Is this errand open to this character right now?"""
    if key not in ERRANDS or key in done_list(char):
        return False
    prereq = _PREREQ.get(key)
    return prereq is None or prereq in done_list(char)


def offers_for(giver_key, char=None):
    """Errands this giver offers (filtered to `char`'s progress if given)."""
    return [
        (key, spec)
        for key, spec in ERRANDS.items()
        if spec["giver"] == giver_key
        and (char is None or available_to(char, key))
    ]


def current(char):
    return char.db.errand or None


def take(char, key):
    """Accept an errand. One at a time. Returns an error string or None."""
    if char.db.errand:
        return (
            "You are already on an errand. Finish it or |cerrands drop|n "
            "it — half-done favors are remembered longer than refused ones."
        )
    if not available_to(char, key):
        return "Nobody is offering that. Not to you, not yet, or not again."
    char.db.errand = {"key": key, "progress": []}
    return None


def drop(char):
    state = char.db.errand
    char.db.errand = None
    return ERRANDS[state["key"]]["title"] if state else None


def _complete(char, spec):
    """Pay out, message, and offer the chain's next link."""
    from world import records

    amount = _REWARD_SIZES[spec["reward_size"]]()
    char.gain_influence(spec["reward_faction"], amount)
    char.db.errand = None
    key = next(k for k, s in ERRANDS.items() if s is spec)
    char.db.errands_done = done_list(char) + [key]
    char.msg(f"|w[Errand complete: {spec['title']}]|n\n{spec['done']}")
    char.msg(
        f"|=mStanding with {spec['reward_faction']}: "
        f"{(char.db.influence or {}).get(spec['reward_faction'], 0)} "
        f"(+{amount}).|n"
    )
    if spec.get("commendation"):
        records.add_record(
            char,
            spec["commendation"],
            author="Office of Orientation",
            kind="observation",
        )
    nxt = spec.get("next")
    if nxt and nxt in ERRANDS:
        nspec = ERRANDS[nxt]
        char.msg(
            f"|=m{nspec['giver'].capitalize()} has more for you, when "
            f"you're ready: |c{nspec['title']}|n|=m — find them and "
            "|cerrands|n|=m.|n"
        )
    logger.log_info(f"watchlog: (an errand ends) {char.key}: {spec['title']}")


def check(char, event, room=None, tier=None):
    """
    The single dispatch point: verbs report events here, and the active
    errand advances or completes. Cheap no-op for citizens without one.
    """
    state = char.db.errand
    if not state:
        return
    spec = ERRANDS.get(state["key"])
    if not spec:
        char.db.errand = None
        return
    etype = spec["type"]

    if etype == "visit" and event == "visit" and room is not None:
        if room.key in spec["rooms"] and room.key not in state["progress"]:
            state["progress"] = state["progress"] + [room.key]
            char.db.errand = state
            remaining = [r for r in spec["rooms"] if r not in state["progress"]]
            if remaining:
                char.msg(
                    f"|=m[{spec['title']}: {room.key} seen. Still to walk: "
                    f"{', '.join(remaining)}.]|n"
                )
            else:
                _complete(char, spec)
    elif etype == "shifts" and event == "shift":
        state["progress"] = state["progress"] + ["shift"]
        char.db.errand = state
        done, need = len(state["progress"]), spec["count"]
        if done >= need:
            _complete(char, spec)
        else:
            char.msg(f"|=m[{spec['title']}: shift {done} of {need}.]|n")
    elif etype == "observe_at" and event == "observe" and room is not None:
        if room.key == spec["room"]:
            _complete(char, spec)
    elif etype == "deliver_tier" and event == "deliver":
        if tier == spec["tier"]:
            _complete(char, spec)
    elif etype == "attend" and event == "attend":
        _complete(char, spec)
    elif etype == "joint_visit" and event == "visit" and room is not None:
        # Four hands (v0.11): completes only with a circle-mate standing
        # in the same room — cooperation as a completion condition.
        if room.key != spec["room"]:
            return
        from world import circles

        slug = circles.circle_of(char)
        if not slug:
            char.msg(
                "|=m[Four Hands: this needs a circle, and you are in "
                "this alone.]|n"
            )
            return
        mates_here = [
            obj
            for obj in room.contents
            if obj is not char and obj in circles.members_of(slug)
        ]
        if mates_here:
            _complete(char, spec)
        else:
            char.msg(
                f"|=m[{spec['title']}: right place. Now the other pair "
                "of hands.]|n"
            )
