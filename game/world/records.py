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


def add_record(subject, content, author="Ministry of Order", kind="incident", tag=None):
    """Open a new entry in a citizen's file."""
    record = create_object(
        "typeclasses.records.Record",
        key=f"record:{subject.key}:{kind}",
    )
    record.db.subject = subject
    record.db.author = author
    record.db.kind = kind
    record.db.content = content
    record.tags.add(str(subject.id), category=SUBJECT_TAG_CATEGORY)
    if tag:
        record.tags.add(tag, category=BETRAYAL_TAG_CATEGORY)
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
    Incident entry `number` (1-based, numbered across the *full* incident
    list including redacted entries — which is why redaction leaves a
    visible gap in the file's numbering).
    """
    incidents = records_for(subject, kind="incident")
    if 1 <= number <= len(incidents):
        return incidents[number - 1]
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
