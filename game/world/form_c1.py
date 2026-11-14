"""
FORM C-1: APPLICATION FOR ELEVATED CLEARANCE (an EvMenu).

The ceremony lives here; the decision logic is `functions.adjudicate_c1`,
kept pure so the paperwork can be tested without the theatre. The form reads
only the record layer — a laundered file passes (ADR 0005), which is the
whole reason anyone launders one.
"""

from world import forms, functions, records, tuning

_HEADER = (
    forms.form_box(
        "|wMINISTRY OF RECORDS - FORM C-1|n",
        "|wAPPLICATION FOR ELEVATED CLEARANCE (GRADE C-1)|n",
    )
    + "\n"
)


def node_start(caller):
    text = (
        _HEADER
        + "The archivist produces the form from a drawer that unsticks with "
        "practice, and squares it on the counter.\n\n"
        f"Filing fee: |w{tuning.CLEARANCE_FEE}|n credits, payable on "
        "submission whatever the outcome. Grade C-1 "
        "admits the holder to the Central Spire lobby, and to such further "
        "opportunities as the Grid sees fit to see fit."
    )
    options = (
        {"desc": "Take up the pen", "goto": "node_purpose"},
        {"desc": "Leave the form where it is", "goto": "node_withdraw"},
    )
    return text, options


def node_purpose(caller):
    text = (
        _HEADER
        + "SECTION 2: STATED PURPOSE OF ELEVATION\n"
        "(Select one. The selections are not different.)"
    )
    options = (
        {
            "desc": "To better serve the Grid",
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
        "they have always been accurate, and that my consultation of them "
        'prior to this application was itself unnecessary."'
    )
    options = (
        {"desc": "Affirm and submit", "goto": "node_adjudicate"},
        {"desc": "Decline to affirm", "goto": "node_decline"},
    )
    return text, options


def node_decline(caller):
    text = (
        "The archivist retrieves the form, unhurried, and returns it to the "
        "drawer.\n\n\"A citizen unsure of their own file,\" they say, to the "
        "drawer, \"should perhaps review it. |cdossier|n is free of charge.\"\n\n"
        "Nothing has been submitted. Almost nothing has been noticed."
    )
    return text, None


def node_withdraw(caller):
    text = (
        "You leave the form where it is. The archivist neither approves nor "
        "disapproves, which is the most unsettling thing available to them."
    )
    return text, None


def node_adjudicate(caller):
    if not caller.spend_credits(tuning.CLEARANCE_FEE):
        text = (
            "The archivist reads your ledger upside down without effort.\n\n"
            f'"The filing fee is {tuning.CLEARANCE_FEE} credits. The '
            "Ministry does not extend credit; credit implies a future, "
            'which is not the Ministry\'s to give."\n\n'
            "The form goes back in the drawer, unsubmitted."
        )
        return text, None

    approved, reason = functions.adjudicate_c1(caller)
    if approved:
        functions.grant_c1(caller)
        records.add_record(
            caller,
            "Form C-1 submitted; APPROVED. Clearance C-1 issued",
            author="Ministry of Records",
            kind="observation",
        )
        text = (
            "The archivist reads your file once forward and, apparently for "
            "pleasure, once backward. Then the good stamp comes out: the "
            "brass one.\n\n"
            "|wAPPLICATION APPROVED. CLEARANCE GRADE C-1 ISSUED.|n\n\n"
            "\"The Spire lobby will admit you now,\" the archivist says. "
            "\"Congratulations. You are henceforth of |winterest|n.\"\n\n"
            "|=mElevation and scrutiny are the same purchase (your exposure "
            "reflects your new altitude).|n"
        )
    else:
        records.add_record(
            caller,
            f"Form C-1 submitted; REJECTED: {reason}",
            author="Ministry of Records",
            kind="observation",
        )
        text = (
            "The archivist reads your file, aligns a rejection stamp with "
            "care approaching tenderness, and brings it down.\n\n"
            f"|rAPPLICATION REJECTED:|n {reason}.\n\n"
            "\"The fee is retained,\" the archivist adds, \"as a record of "
            "your ambition. You may reapply when your circumstances have "
            "improved. Circumstances do improve.\" A pause. \"They can be "
            "|wmade|n to."
        )
    caller.send_prompt()
    return text, None
