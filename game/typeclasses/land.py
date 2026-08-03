"""
Land and water parcels (ADR 0022): the same records-are-objects promise
(ADR 0005) pointed at a place instead of a person.

world/records.py's add_record()/records_for() already take a generic
`subject` — nothing there requires a Character. A Parcel is that generic
subject, non-spatial exactly like typeclasses/records.py's Record, so a
land survey or water allotment can be falsified and petitioned the same
way a citizen's incident can, through the same API, with one real
difference: the standing that governs petition/forge on a parcel's record
belongs to whoever holds `db.owner`, not to the citizen the record happens
to be filed about (there is no such citizen -- a parcel's record is about
the land).
"""

from evennia.objects.objects import DefaultObject


class Parcel(DefaultObject):
    """
    A tracked plot of land or water allotment. Never walked into; exists
    only to be a record subject and to answer "whose is this."
    """

    def at_object_creation(self):
        super().at_object_creation()
        self.db.owner = None  # the citizen whose standing governs this parcel's records
        self.db.parcel_kind = None  # "survey" | "allotment"
        self.locks.add("get:false();view:perm(Builder)")
