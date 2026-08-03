"""
FORM C-2: APPLICATION FOR FURTHER ELEVATION (an EvMenu).

Filed the same place Form C-1 was -- the archivist keeps every tier's
paperwork -- but read more closely: `functions.adjudicate_c2`'s bar is
tighter than `adjudicate_c1`'s, per ADR 0021.
"""

from world import forms, functions, records, tuning

_HEADER = (
    forms.form_box(
        "|wMINISTRY OF RECORDS - FORM C-2|n",
        "|wAPPLICATION FOR FURTHER ELEVATION (GRADE C-2)|n",
    )
    + "\n"
)


def node_start(caller):
    text = (
        _HEADER
        + "The archivist produces a second form, thinner than the first, "
        "from a drawer one down. \"Those who come back for this one "
        "usually already know what it costs.\"\n\n"
        f"Filing fee: |w{tuning.CLEARANCE_FEE}|n standing with the Ministry "
        "of Records, payable on submission whatever the outcome. Grade C-2 "
        "admits the holder past the Spire lobby, to the floor where the "
        "lobby's promises are kept, revised, or quietly forgotten."
    )
    options = (
        {"desc": "Take up the pen", "goto": "node_purpose"},
        {"desc": "Leave the form where it is", "goto": "node_withdraw"},
    )
    return text, options


def node_purpose(caller):
    text = (
        _HEADER
        + "SECTION 2: STATED PURPOSE OF FURTHER ELEVATION\n"
        "(The Ministry notes that this section is read more closely the "
        "second time.)"
    )
    options = (
        {
            "desc": "To better serve the Grid, at greater altitude",
            "goto": ("node_declaration", {"purpose": "service"}),
        },
        {
            "desc": "To pursue advancement within my function",
            "goto": ("node_declaration", {"purpose": "advancement"}),
        },
        {
            "desc": "Personal reasons, enumerated on attachment (no attachment)",
            "goto": ("node_declaration", {"purpose": "personal"}),
        },
    )
    return text, options


def node_declaration(caller, raw_string, **kwargs):
    text = (
        _HEADER
        + "SECTION 4: DECLARATION\n"
        '"I affirm that the contents of my citizen file are accurate, that '
        "they have always been accurate, and that this affirmation is not "
        'noticeably different from the last one I signed."'
    )
    options = (
        {"desc": "Affirm and submit", "goto": "node_adjudicate"},
        {"desc": "Decline to affirm", "goto": "node_decline"},
    )
    return text, options


def node_decline(caller):
    text = (
        "The archivist retrieves the form without visible reaction and "
        "returns it to its drawer.\n\n\"Fewer citizens decline the second "
        "time,\" they say, to the drawer. \"Most have already decided by "
        "the elevator.\""
    )
    return text, None


def node_withdraw(caller):
    text = (
        "You leave the form where it is. The archivist adds nothing, "
        "which, at this tier, is itself a kind of note."
    )
    return text, None


def node_adjudicate(caller):
    if not caller.spend_influence("Ministry of Records", tuning.CLEARANCE_FEE):
        text = (
            "The archivist doesn't need to check the ledger twice this "
            "time.\n\n"
            f'"The filing fee is {tuning.CLEARANCE_FEE} standing with the '
            "Ministry of Records. Unchanged from the last form. The "
            'Ministry\'s generosity has limits, and you have found one."\n\n'
            "The form goes back in the drawer, unsubmitted."
        )
        return text, None

    approved, reason = functions.adjudicate_c2(caller)
    if approved:
        functions.grant_c2(caller)
        records.add_record(
            caller,
            "Form C-2 submitted; APPROVED. Clearance C-2 issued",
            author="Ministry of Records",
            kind="observation",
        )
        text = (
            "The archivist reads your file forward, backward, and once "
            "more at an angle you don't recognize. The stamp that comes "
            "out this time has no color at all -- an impression, not an "
            "ink.\n\n"
            "|wAPPLICATION APPROVED. CLEARANCE GRADE C-2 ISSUED.|n\n\n"
            "\"The elevator will know,\" the archivist says. \"It "
            "generally does.\"\n\n"
            "|=mElevation and scrutiny are the same purchase, again (your "
            "exposure reflects your new altitude).|n"
        )
    else:
        records.add_record(
            caller,
            f"Form C-2 submitted; REJECTED: {reason}",
            author="Ministry of Records",
            kind="observation",
        )
        text = (
            "The archivist reads your file with the specific patience of "
            "someone who expected this.\n\n"
            f"|rAPPLICATION REJECTED:|n {reason}.\n\n"
            "\"The fee is retained,\" the archivist adds, \"as before. "
            "Return when your circumstances have improved. They tend to, "
            "at this tier, or they tend not to. There is rarely a middle "
            "case.\""
        )
    caller.send_prompt()
    return text, None
