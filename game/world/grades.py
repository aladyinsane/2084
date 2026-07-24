"""
Citizen Grades (v0.12): the familiar ladder.

The research (docs/research/the-first-hour.md) named the gap: 2084 has five
progression currencies and no single number that says "you are getting
somewhere." The grade is that number — the legibility of a level with no new
progression system underneath. It is *derived*, never granted: a pure view
over merit the citizen already earned.

Design rules:

- **Sanctioned only.** The Grid ranks what the Grid can see. The underground
  ledger and the errands it pays for do not exist, so they cannot count
  (the dossier-leak lesson, learned twice already).
- **Merit is lifetime, not balance.** Spending standing at the Annex must
  never demote you — levels that go down when you buy things are exactly
  the XP/gold confusion the ladder exists to prevent. `gain_influence`
  tracks lifetime earnings separately.
- **Civil-service shape.** Grades descend toward status: Grade 6
  (probationary) down to Grade 1. The *movement* is what's familiar, and
  the prompt makes it visible.
- **Display-only.** Grades gate nothing yet. If Form C-1 or function pay
  ever reference them, that is a separate decision with its own ADR.

The stored `db.citizen_grade` is a cache of the last computed grade, kept so
the prompt is cheap and so reclassification (the fanfare moment) can be
detected at the choke points that change merit.
"""

from evennia.utils import logger

from world import forms, tuning

GRADE_MIN = 6  # probationary: every citizen starts here, briefly


def merit(char):
    """
    Total sanctioned merit. Pure function of the character's earned record —
    nothing here mutates.
    """
    from world import errands, functions

    total = 0
    earned = char.db.influence_earned or {}
    total += sum(
        value
        for faction, value in earned.items()
        if faction not in tuning.UNSANCTIONED_FACTIONS
    )
    total += tuning.GRADE_MERIT_PER_ERRAND * sum(
        1
        for key in (char.db.errands_done or [])
        if errands.ERRANDS.get(key, {}).get("reward_faction")
        not in tuning.UNSANCTIONED_FACTIONS
    )
    if (char.db.standing or {}).get("function_key"):
        total += tuning.GRADE_MERIT_FUNCTION
    total += tuning.GRADE_MERIT_CLEARANCE * functions.clearance_level(char)
    if char.db.oriented:
        total += tuning.GRADE_MERIT_ORIENTATION
    return total


def grade_for_merit(points):
    """The best (lowest-numbered) grade this much merit reaches."""
    grade = GRADE_MIN
    for g in sorted(tuning.GRADE_THRESHOLDS, reverse=True):
        if points >= tuning.GRADE_THRESHOLDS[g]:
            grade = g
    return grade


def grade_of(char):
    """The stored grade (what the prompt shows). GRADE_MIN if never set."""
    return char.db.citizen_grade or GRADE_MIN


def next_review(char):
    """
    (current merit, next grade up, its threshold) — or (merit, None, None)
    at Grade 1, where no further elevation is contemplated.
    """
    points = merit(char)
    grade = grade_for_merit(points)
    if grade <= 1:
        return points, None, None
    nxt = grade - 1
    return points, nxt, tuning.GRADE_THRESHOLDS[nxt]


def check_reclassification(char):
    """
    Recompute the grade and, if it moved, stamp the change: fanfare to the
    citizen, an entry in the file (the file celebrates you, which is also a
    threat). Called from the choke points that change merit. Returns the
    current grade either way.
    """
    from world import records

    new = grade_for_merit(merit(char))
    old = grade_of(char)
    if new == old:
        return new
    char.db.citizen_grade = new
    if new < old:
        closing = "The Grid thanks you for your legibility."
    else:
        closing = "The Ministry does not discuss its arithmetic."
    char.msg(
        forms.form_box(
            "|wNOTICE OF RECLASSIFICATION (FORM 9-A)|n",
            "By review of the record, your civic grade",
            f"is revised: Grade {old} |w->|n |wGrade {new}|n.",
            closing,
        )
    )
    if hasattr(char, "send_prompt"):
        char.send_prompt()
    records.add_record(
        char,
        f"Reclassified: Citizen, Grade {new}",
        author="Ministry of Records",
        kind="observation",
    )
    logger.log_info(
        f"watchlog: reclassification — {char.key}: Grade {old} -> Grade {new}"
    )
    return new
