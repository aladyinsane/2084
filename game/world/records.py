"""
The records API: every read and write of a citizen's file goes through here.

This module enforces ADR 0005's two-layer promise: the record layer is freely
mutable *through these functions*, and every mutation appends what-was to the
audit trail first. The audit trail is the ground truth that makes forgery
gameplay honest — the game always knows what really happened, even when the
file lies.

The `actor` passed to mutators is recorded truthfully in the audit even when
the record layer is being made to lie (a forged amendment shows the forger in
the audit, whatever name the file now displays).
"""

import time

from evennia import create_object
from evennia.utils.search import search_object_by_tag

SUBJECT_TAG_CATEGORY = "record_subject"

# ADR 0010: a marker on the record object itself, set once at creation,
# untouched by amend()/redact() — so `judge` reads what actually happened
# instead of pattern-matching prose that's free to be rewritten later.
BETRAYAL_TAG_CATEGORY = "betrayal"


def add_record(
    subject,
    content,
    author="Ministry of Order",
    kind="incident",
    tag=None,
    type_key=None,
):
    """Open a new entry in a citizen's file."""
    record = create_object(
        "typeclasses.records.Record",
        key=f"record:{subject.key}:{kind}",
    )
    record.db.subject = subject
    record.db.author = author
    record.db.kind = kind
    record.db.content = content
    record.db.type_key = type_key
    record.tags.add(str(subject.id), category=SUBJECT_TAG_CATEGORY)
    if tag:
        record.tags.add(tag, category=BETRAYAL_TAG_CATEGORY)
    if kind == "incident":
        # ADR 0011 prerequisite: assigned once, here, rather than derived
        # later from list position (`enumerate` over a freshly-queried
        # list). Positional numbering was only ever stable because nothing
        # was ever deleted; assigning it at creation keeps it stable once
        # compaction starts removing individual records.
        subject.db.next_incident_number = (subject.db.next_incident_number or 0) + 1
        record.db.number = subject.db.next_incident_number
    record.db.audit.append(
        {"at": time.time(), "actor": author, "action": "created", "content": content}
    )
    return record


def records_for(subject, kind=None, include_redacted=True):
    """All records on a subject, oldest first."""
    found = search_object_by_tag(str(subject.id), category=SUBJECT_TAG_CATEGORY)
    found = [
        rec
        for rec in found
        if (kind is None or rec.db.kind == kind)
        and (include_redacted or not rec.db.redacted)
    ]
    return sorted(found, key=lambda rec: rec.db.created or 0)


def incident_by_number(subject, number):
    """
    Incident entry `number` (1-based, assigned once at creation and stored
    on the record — see ADR 0011 — so it survives redaction (which is why
    redaction leaves a visible gap). A number belonging to a since-compacted
    incident (ADR 0011 §2) resolves to None, same as any other unassigned
    number — compaction only ever touches routine types nobody references
    by number in practice.
    """
    for rec in records_for(subject, kind="incident"):
        if rec.db.number == number:
            return rec
    return None


def amend(record, new_content, actor, authorized=True):
    """Change what the file says. The audit keeps what it used to say."""
    record.db.audit.append(
        {
            "at": time.time(),
            "actor": getattr(actor, "key", str(actor)),
            "action": "amended" if authorized else "amended (unauthorized)",
            "content": record.db.content,
        }
    )
    record.db.content = new_content
    return record


def redact(record, actor, authorized=True):
    """Strike an entry from the visible file. The entry, and the striking,
    both persist beneath it."""
    record.db.audit.append(
        {
            "at": time.time(),
            "actor": getattr(actor, "key", str(actor)),
            "action": "redacted" if authorized else "redacted (unauthorized)",
            "content": record.db.content,
        }
    )
    record.db.redacted = True
    return record


def recent_incidents(exclude_subject=None, window=None, limit=3):
    """
    Fresh, unredacted incidents about *other* citizens — the raw material of
    queue gossip (principle 8's asynchronous traces).
    """
    from typeclasses.records import Record
    from world import tuning

    window = window if window is not None else tuning.GOSSIP_WINDOW
    cutoff = time.time() - window
    found = [
        rec
        for rec in Record.objects.all()
        if rec.db.kind == "incident"
        and not rec.db.redacted
        and (rec.db.created or 0) >= cutoff
        and rec.db.subject
        and rec.db.subject != exclude_subject
    ]
    found.sort(key=lambda rec: rec.db.created or 0, reverse=True)
    return found[:limit]


def compact_incidents(char):
    """
    ADR 0011: fold eligible old, routine, untouched incidents into the
    citizen's lifetime per-type summary (`char.db.incident_summaries`),
    then delete them. Eligible means: `type_key` is one of
    `tuning.COMPACTABLE_INCIDENT_TYPES` (milestone incidents default to
    `type_key=None` and are excluded automatically — no separate
    do-not-compact list needed); older than `tuning.RECORD_COMPACTION_AGE`;
    and untouched, meaning nothing but its own creation is in `db.audit`
    (`len(audit) == 1`) — the moment a player amends or redacts a specific
    entry, it's pinned as an individual object forever, same as a milestone.
    A pinned-but-redacted record therefore never contributes to a summary;
    its redaction work simply isn't lost, because the record itself isn't
    either.
    """
    from world import tuning

    cutoff = time.time() - tuning.RECORD_COMPACTION_AGE
    summaries = char.db.incident_summaries or {}
    changed = False
    for rec in records_for(char, kind="incident"):
        type_key = rec.db.type_key
        if type_key not in tuning.COMPACTABLE_INCIDENT_TYPES:
            continue
        if (rec.db.created or 0) >= cutoff:
            continue
        if len(rec.db.audit or []) > 1:
            continue
        bucket = summaries.setdefault(type_key, {"true": 0, "visible": 0})
        bucket["true"] += 1
        bucket["visible"] += 1
        rec.delete()
        changed = True
    if changed:
        char.db.incident_summaries = summaries


def prune_observations(char):
    """
    ADR 0011 §3: movement logs and assembly attendance have no
    petition/forge surface at all today (`incident_by_number` only ever
    queries `kind="incident"`), so past a retention cap the oldest are
    deleted outright — no summary needed, nothing was ever forgeable about
    them to begin with.
    """
    from world import tuning

    for type_key in tuning.PRUNABLE_OBSERVATION_TYPES:
        matches = [
            rec
            for rec in records_for(char, kind="observation")
            if rec.db.type_key == type_key
        ]
        excess = len(matches) - tuning.MOVEMENT_LOG_RETENTION
        for rec in matches[:excess]:  # oldest-first (records_for's sort)
            rec.delete()


def summary_for(char, type_key):
    """Current (true, visible) counts for a summarized incident type —
    (0, 0) if nothing of that type has folded in yet."""
    bucket = (char.db.incident_summaries or {}).get(type_key)
    return (bucket["true"], bucket["visible"]) if bucket else (0, 0)


def redact_summary(char, type_key):
    """Lower a summarized type's visible count by one. The true count, and
    the audit trail already folded into it, never changes. Returns False
    if there's nothing left to redact."""
    summaries = char.db.incident_summaries or {}
    bucket = summaries.get(type_key)
    if not bucket or bucket["visible"] <= 0:
        return False
    bucket["visible"] -= 1
    char.db.incident_summaries = summaries
    return True
