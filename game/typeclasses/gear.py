"""
Gear (v0.10): the implant catalog, adapted for an analog dystopia.

3M sells skills as implants with memory slots — the lesson we took
(field research §3) is that a *slot-limited loadout of trade-offs* is what
made that system sing, not the surgery. Airstrip One is a place of coats,
cuffs and laminated cards, so 2084 wears its implants: one item per slot,
every item a trade, no straight upgrades (principle 9 gets a corollary
here: no magic items either — each piece does exactly what a thing of
cloth, foil, or lamination could plausibly do).

The economics carry the theme: the state issues what helps it watch you
(the badge identifies, the cuff reports), the black market sells what
interferes (the coat muffles, the pocket lies) — and each side's gear is
priced in that side's ledger.

Effects are dispatched by `db.gear_kind` at the existing hook sites
(room entry, work pay, decay tick, contraband seizure); this module holds
only the object and its wearing logic.
"""

from .objects import Object


class Gear(Object):
    """A wearable. One per slot; effects keyed by db.gear_kind."""

    def at_object_creation(self):
        super().at_object_creation()
        self.db.slot = "coat"
        self.db.gear_kind = None
        self.db.worn = False

    def at_drop(self, dropper, **kwargs):
        super().at_drop(dropper, **kwargs)
        self.db.worn = False


def worn_gear(char):
    """Everything this character is wearing."""
    return [
        obj for obj in char.contents if isinstance(obj, Gear) and obj.db.worn
    ]


def worn_kind(char, kind):
    """The worn gear of a given kind, or None."""
    for obj in worn_gear(char):
        if obj.db.gear_kind == kind:
            return obj
    return None


def room_exposure_delta(char, room):
    """Worn-gear adjustment to a room's entry exposure (can be negative)."""
    from world import tuning

    delta = 0
    if (
        worn_kind(char, "badge")
        and getattr(room, "visibility", 0) >= tuning.BADGE_VIS_THRESHOLD
    ):
        delta += tuning.BADGE_ROOM_EXPOSURE
    if worn_kind(char, "dampener"):
        delta -= tuning.DAMPENER_ROOM_RELIEF
    return delta
