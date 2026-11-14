"""
Records archaeology (v0.24, ADR 0016): the third grind loop, and the first
that never leaves sanctioned space.

`research` (commands/civic.py) is the verb; this module holds its data and
bookkeeping for two parallel tracks. A generic case is built from atomic
fragment sentences drawn without repetition within the case -- no
grammatical recombination, so nothing to get grammatically wrong -- and
pays a little Ministry of Records standing per fragment, underground
standing on completion. A rare draw instead surfaces a piece of one of a
small hand-authored set of named cases; completing one pays more and
prints a real reveal. Both tracks are pure per-citizen state (`char.db`),
by design: this loop has no group component, unlike circles.py's.
"""

import random

from world import tuning

CASE_NAMES = [
    "a printer's apprentice",
    "a third-shift auditor",
    "a woman who ran the eastern laundry",
    "a boy who swept the Assembly floor",
    "a filing clerk with a stutter",
    "a man who mended nets nobody used anymore",
    "a widow who read the meters",
    "a courier who never once got checked",
    "an usher at the old cinema",
    "a stock clerk with a memory for numbers",
    "a night porter at the Spire's service door",
    "a schoolteacher's assistant",
]

GENERIC_FRAGMENTS = [
    "A requisition form for a coat that was never collected.",
    "A transfer order to a district that appears on no current map.",
    "A ration card, cancelled, with no cancellation reason filed.",
    'A photograph with a shape cut out of it, catalogued under "damaged."',
    "A commendation half-written and never signed.",
    "A room assignment for a room that, per the current registry, does not exist.",
    "A medical exemption stamped the same week as a reclassification notice.",
    "A letter of introduction to a Ministry official who left no other trace.",
    "A payroll entry that continues three months past a listed transfer.",
    "A visitor's log with one line inked out so thoroughly the paper is thin there.",
    "A commendation revoked the same day it was granted, filed under a different name.",
    "A Form 77 for a function nobody in the current registry holds.",
    "An apology, addressed to no one, filed as if it were evidence.",
    "A census entry with a birth date and no death date, and no entries after it.",
    "A supply requisition for two, delivered, to a household later listed as one.",
    'A note in the margin of an old ledger: "ask again later," undated.',
    "A denied appeal, stamped, with the appeal itself missing from the file.",
    "A key ring logged as returned by someone the log otherwise never mentions.",
    "A single shift report with every other name redacted but this one.",
    "A commendation for observation skill, filed out of order with an incident from the same month.",
    "A form requesting a form that, per the index, was never printed.",
    "A ledger correction in a different hand, undated, unattributed.",
    "A queue assignment moved twice in one week, for reasons the file declines to give.",
    "A photograph of a room, empty, captioned only with a date.",
    "A note that the file continues in a volume the Annex does not hold.",
]

# Small, hand-authored, and deliberately not the whole story -- the reveal
# is what "assembling a story about an unperson" actually means; the ADR
# expects this table to grow the way errands.py's catalog did.
NAMED_CASES = {
    "the-signalman": {
        "title": "the signalman",
        "fragments": [
            "A maintenance log for a lamp that was fixed the same night its keeper was reassigned.",
            'A transfer order for "the signalman, Tenement Row," destination field left blank.',
            'A line in an old sweep report: "lamp restored; keeper\'s file closed; matter concluded."',
        ],
        "reveal": (
            "The lamp that used to flicker outside Tenement Row was fixed "
            "the same week its keeper stopped answering to his own name. "
            "The transfer order that should have sent him somewhere was "
            "never completed; the destination field is blank, and stays "
            'blank, in every copy the Annex holds. "Matter concluded," the '
            "sweep report says, three words doing the work of an "
            "explanation. The lamp has not flickered since."
        ),
    },
    "the-second-desk": {
        "title": "the second desk",
        "fragments": [
            "A staffing chart for the Assignment Hall with two names at one desk and one chair.",
            "A payroll entry paying a second clerk at that counter, for a citizen the current roster has no record of.",
            'A note clipped to an old chart: "desk reassigned; duplicate entry corrected."',
        ],
        "reveal": (
            "For eleven months, two names drew pay from one counter at the "
            "Assignment Hall, and the chart shows one chair. The Ministry's "
            "own correction calls it a duplicate entry -- an error in the "
            "ledger, the kind that gets fixed and forgotten. But the "
            "correction is dated a full year after the second name stops "
            "appearing anywhere else at all."
        ),
    },
    "the-uncounted-census": {
        "title": "the uncounted census",
        "fragments": [
            "A census page listing a household of three, and a ration allocation for two.",
            "A school attendance record with a child's name crossed through, re-entered, crossed through again.",
            'A closing note on the file: "household corrected; census stands."',
        ],
        "reveal": (
            "The census said three. The ration book said two, and had said "
            "two for longer than the census had said three. A child's name "
            "goes in and out of a school register like a held breath, and "
            "the file that finally closes the matter doesn't say which "
            'number was wrong -- only that the household is "corrected," '
            "and the census, whatever it once said, now stands."
        ),
    },
}


# --- generic cases (the infinite grind) --------------------------------


def _start_case(char):
    case = {"name": random.choice(CASE_NAMES), "found": []}
    char.db.archaeology_case = case
    return case


def _draw_generic_fragment(char):
    case = char.db.archaeology_case or _start_case(char)
    found = case["found"]
    remaining = [i for i in range(len(GENERIC_FRAGMENTS)) if i not in found]
    if not remaining:
        # Pool exhausted mid-case -- shouldn't happen at the default
        # CASE_FRAGMENTS_REQUIRED, but a shrunken pool shouldn't hang.
        case = _start_case(char)
        remaining = list(range(len(GENERIC_FRAGMENTS)))
    idx = random.choice(remaining)
    found.append(idx)
    char.db.archaeology_case = case
    char.msg(
        f"|=mSomewhere in the file of {case['name']}: "
        f"{GENERIC_FRAGMENTS[idx]}|n"
    )
    if len(found) >= tuning.CASE_FRAGMENTS_REQUIRED:
        _complete_generic(char, case)
    else:
        char.msg(
            f"|=m[{len(found)} of {tuning.CASE_FRAGMENTS_REQUIRED} pieces, "
            "assembling.]|n"
        )


def _complete_generic(char, case):
    lines = " ".join(GENERIC_FRAGMENTS[i] for i in case["found"])
    char.db.archaeology_case = None
    char.gain_standing_and_credits(tuning.UNDERGROUND, tuning.CASE_COMPLETION_PAYOUT)
    char.msg(
        f"|g[The shape completes itself: {case['name']}.]|n\n{lines}\n"
        "|=mWhoever they were, the file remembers less of them than you "
        f"just did. {tuning.CASE_COMPLETION_PAYOUT} standing with "
        f"{tuning.UNDERGROUND}, {tuning.CASE_COMPLETION_PAYOUT} credits, "
        "for the noticing.|n"
    )


# --- named cases (the jackpot) -------------------------------------------


def _next_named_draw(char):
    """
    Which named case a rare roll should feed, or None if this citizen has
    solved all of them. Prefers a case already in progress, so a rare
    streak finishes what it started before wandering to a new one.
    """
    solved = char.db.archaeology_solved or []
    available = [key for key in NAMED_CASES if key not in solved]
    if not available:
        return None
    progress = char.db.archaeology_named or {}
    in_progress = [key for key in available if progress.get(key)]
    return random.choice(in_progress or available)


def _draw_named_fragment(char, key):
    spec = NAMED_CASES[key]
    progress = char.db.archaeology_named or {}
    found = list(progress.get(key, []))
    remaining = [i for i in range(len(spec["fragments"])) if i not in found]
    if not remaining:
        return
    idx = random.choice(remaining)
    found.append(idx)
    progress[key] = found
    char.db.archaeology_named = progress
    char.msg(
        "|=mAmong the routine paperwork, one page doesn't belong: "
        f"{spec['fragments'][idx]}|n"
    )
    if len(found) >= len(spec["fragments"]):
        _complete_named(char, key)
    else:
        char.msg(
            f"|=m[{spec['title']}: {len(found)} of "
            f"{len(spec['fragments'])} pieces, assembling.]|n"
        )


def _complete_named(char, key):
    spec = NAMED_CASES[key]
    solved = char.db.archaeology_solved or []
    solved.append(key)
    char.db.archaeology_solved = solved
    progress = char.db.archaeology_named or {}
    progress.pop(key, None)
    char.db.archaeology_named = progress
    char.gain_standing_and_credits(tuning.UNDERGROUND, tuning.NAMED_CASE_PAYOUT)
    char.msg(
        f"|g[The shape completes itself: {spec['title']}.]|n\n"
        f"{spec['reveal']}\n"
        "|=mYou know something the file no longer says. "
        f"{tuning.NAMED_CASE_PAYOUT} standing with {tuning.UNDERGROUND}, "
        f"{tuning.NAMED_CASE_PAYOUT} credits, for knowing it.|n"
    )


# --- the verb's single entry point ---------------------------------------


def research(char):
    """
    One `research` action: pays, costs, and messages the caller directly,
    same idiom as circle_projects.check(). The command handles cooldown
    gating and the archivist's presence; this handles everything past that.
    """
    char.improve_skill("clerking")
    char.gain_standing_and_credits("Ministry of Records", tuning.RESEARCH_INFLUENCE)
    rare_chance = tuning.RESEARCH_RARE_BASE_CHANCE + (
        char.skill("clerking") * tuning.RESEARCH_RARE_SKILL_BONUS
    )
    named_key = _next_named_draw(char) if random.random() < rare_chance else None
    if named_key:
        char.gain_exposure(tuning.RESEARCH_RARE_EXPOSURE)
        _draw_named_fragment(char, named_key)
    else:
        char.gain_exposure(tuning.RESEARCH_EXPOSURE)
        _draw_generic_fragment(char)
    char.send_prompt()
