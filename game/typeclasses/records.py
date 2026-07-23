"""
Records: the state's memory of you, as first-class objects (ADR 0005).

A Record is non-spatial (location None) and carries two permanently distinct
layers:

- the **record layer** (`db.content`, `db.redacted`): what the file says.
  Mutable in play — clerks amend, petitions redact, forgers rewrite.
- the **truth layer** (`db.audit`): an append-only list of every state the
  record has ever been in and who changed it. Nothing removes from it, ever —
  including admins-in-fiction. All mutation goes through world/records.py,
  which maintains this discipline.
"""

import time

from evennia.objects.objects import DefaultObject

from .objects import ObjectParent


class Record(DefaultObject):
    """
    One entry in a citizen's file: an incident, an observation, a work
    evaluation, a denunciation. Fields per ADR 0005: origin, timestamp,
    author, subject, content.
    """

    def at_object_creation(self):
        super().at_object_creation()
        self.db.subject = None       # the citizen the record is about
        self.db.author = "unknown"   # what the file *claims* wrote it
        self.db.kind = "incident"    # incident | observation | evaluation
        self.db.content = ""
        self.db.created = time.time()
        self.db.redacted = False
        self.db.audit = []           # append-only truth layer
        # ADR 0011: incidents (kind="incident" only) get a stable number
        # assigned once at creation, from the subject's own counter — see
        # world/records.py:add_record. None for kinds that are never
        # individually numbered (observation, evaluation).
        self.db.number = None
        self.locks.add("get:false();view:perm(Builder)")
