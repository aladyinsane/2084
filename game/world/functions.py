"""
Functions: the regime's answer to "what are you?" (ADR 0002).

A function is not a class. It is a stamp in your dossier — assigned by the
Ministry after reading your recorded aptitudes, revoked as easily, suspended
the moment you're detained. The stamp decides where your labor counts and
which ministry's ledger it feeds.

Also here: the Form C-1 adjudication, as a pure function so the paperwork's
logic is testable apart from its ceremony (the EvMenu in world/form_c1.py).
"""

from world import tuning

# function key -> (dossier title, paying faction, workplace description,
#                  workplace test(room) -> bool)
FUNCTIONS = {
    "records_clerk": {
        "title": "Clerk, Records Section",
        "faction": "Ministry of Records",
        "workplace_desc": "the Assignment Hall counter",
        "skill": "clerking",
        "works_here": lambda room: bool(
            room and room.tags.get("workplace", category="grid")
        ),
        "shifts": [
            "You stamp, sort, and cross-reference until the names stop being "
            "names. Your initials go in boxes sized exactly for initials.",
            "You reconcile two contradictory ledgers by producing a third.",
        ],
    },
    "auditor": {
        "title": "Auditor, Order Section",
        "faction": "Ministry of Order",
        "workplace_desc": "any room with a fixed device in it",
        "skill": "observation",
        "works_here": lambda room: bool(
            room
            and any(
                hasattr(obj, "sensitivity") and not obj.destination
                for obj in room.contents
            )
        ),
        "shifts": [
            "You log each device's serial, angle, and appetite, and initial "
            "the margin. One lens follows you as you check it. You note that.",
            "You test a lens with a cloth and a form. Both come away clean.",
        ],
    },
    "steward": {
        "title": "Steward, Commerce Section",
        "faction": "Ministry of Commerce",
        "workplace_desc": "the Ration Queue",
        "skill": "clerking",
        "works_here": lambda room: bool(
            room and room.tags.get("gossip_spot", category="grid")
        ),
        "shifts": [
            "You square the queue's edges and re-hang the rope that is always "
            "falling. The queue tolerates you the way weather is tolerated.",
            "You count heads, then count them again for the evening figure. "
            "The two numbers disagree. You submit the calmer one.",
        ],
    },
}


def assign_function(char):
    """
    The Ministry reads your file and decides what you are. Recorded aptitude
    drives the stamp: clerking types you as a clerk, observation as an
    auditor; the unremarkable become stewards. (Your skills are your record;
    your record is your function — ADR 0002 and 0005 shaking hands.)
    """
    skills = char.db.skills or {}
    clerking = skills.get("clerking", 0)
    observation = skills.get("observation", 0)
    if clerking or observation:
        key = "records_clerk" if clerking >= observation else "auditor"
    else:
        key = "steward"
    spec = FUNCTIONS[key]
    standing = char.db.standing or {}
    standing["function"] = spec["title"]
    standing["function_key"] = key
    char.db.standing = standing
    from world import grades

    grades.check_reclassification(char)
    return key, spec


def current_function(char):
    key = (char.db.standing or {}).get("function_key")
    return (key, FUNCTIONS[key]) if key in FUNCTIONS else (None, None)


def suspend_function(char):
    standing = char.db.standing or {}
    if standing.get("function_key"):
        standing["function"] = "|=msuspended pending review|n"
        standing.pop("function_key", None)
        char.db.standing = standing
        from world import grades

        grades.check_reclassification(char)
        return True
    return False


def clearance_level(char):
    """Numeric clearance: 'C-2' -> 2; anything else -> 0."""
    value = (char.db.standing or {}).get("clearance", "")
    if isinstance(value, str) and value.startswith("C-"):
        try:
            return int(value.split("-", 1)[1])
        except ValueError:
            return 0
    return 0


def adjudicate_c1(char):
    """
    Form C-1's decision logic, free of ceremony. Returns (approved, reason).
    The Ministry reads the *record layer* only — a laundered file is, per
    ADR 0005, indistinguishable from a clean one at this counter.
    """
    from world import records

    if clearance_level(char) >= 1:
        return False, "applicant already holds the clearance applied for"
    key, _spec = current_function(char)
    if not key:
        return False, "Form 77 (Employment Verification) absent from file"
    visible_incidents = [
        rec
        for rec in records.records_for(char, kind="incident")
        if not rec.db.redacted
    ]
    # ADR 0014: a character reference on file (someone currently vouching
    # for this citizen) tolerates one extra incident -- flat, regardless of
    # how many citizens are backing them, so stacking vouches for a bigger
    # offset is deliberately not a thing.
    from world import vouching

    threshold = tuning.CLEARANCE_MAX_INCIDENTS
    if vouching.has_backers(char):
        threshold += 1
    if len(visible_incidents) > threshold:
        return False, "character references insufficient at this time"
    return True, "application conforms to schedule"


def grant_c1(char):
    standing = char.db.standing or {}
    standing["clearance"] = "C-1"
    char.db.standing = standing
    char.gain_exposure(tuning.CLEARANCE_GRANT_EXPOSURE)
    from world import grades

    grades.check_reclassification(char)


def adjudicate_c2(char):
    """
    Form C-2's decision logic (ADR 0021), mirroring adjudicate_c1 with a
    tighter bar -- the record layer is still all that's read (ADR 0005),
    the same promise C-1 made.
    """
    from world import records

    if clearance_level(char) < 1:
        return False, "Grade C-1 must be held before C-2 may be sought"
    if clearance_level(char) >= 2:
        return False, "applicant already holds the clearance applied for"
    key, _spec = current_function(char)
    if not key:
        return False, "Form 77 (Employment Verification) absent from file"
    visible_incidents = [
        rec
        for rec in records.records_for(char, kind="incident")
        if not rec.db.redacted
    ]
    from world import vouching

    threshold = tuning.CLEARANCE_C2_MAX_INCIDENTS
    if vouching.has_backers(char):
        threshold += 1
    if len(visible_incidents) > threshold:
        return False, "character references insufficient at this time"
    return True, "application conforms to schedule"


def grant_c2(char):
    standing = char.db.standing or {}
    standing["clearance"] = "C-2"
    char.db.standing = standing
    char.gain_exposure(tuning.CLEARANCE_C2_GRANT_EXPOSURE)
    from world import grades

    grades.check_reclassification(char)
