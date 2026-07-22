"""
Room

Rooms are simple containers that has no location of their own.

"""

import re

from evennia.objects.objects import DefaultRoom
from evennia.typeclasses.attributes import AttributeProperty
from evennia.utils.utils import compress_whitespace

from world import tuning

from .objects import ObjectParent


class Room(ObjectParent, DefaultRoom):
    """
    A room in the Grid.

    `visibility` (0-5) is how watched this place is — static per room, set by
    the world build (ADR 0004). Entering a watched room is the event where
    exposure accrues; nothing polls.
    """

    visibility = AttributeProperty(0)

    # Same as DefaultObject.appearance_template, but with a marker between
    # the prose description and the Exits/Characters/You-see block. The
    # marker becomes a blank line in format_appearance below — a literal
    # blank line here wouldn't survive Evennia's whitespace compression,
    # which collapses runs of newlines down to one.
    appearance_template = """
{header}
|c{name}{extra_name_info}|n
{desc}
\x00
{exits}
{characters}
{things}
{footer}
    """

    def format_appearance(self, appearance, looker, **kwargs):
        """
        Give the room description its own paragraph, and Exits/Characters/
        You-see each theirs — a blank line between any two blocks that are
        actually present, so a room missing one (the holding cell has no
        exits) doesn't leave a stray gap where it would have been.
        """
        appearance = compress_whitespace(appearance).strip()
        appearance = appearance.replace("\x00\n", "\n")
        appearance = re.sub(r"\n(?=\|wCharacters:)", "\n\n", appearance)
        appearance = re.sub(r"\n(?=\|wYou see:)", "\n\n", appearance)
        appearance = re.sub(r"\n{3,}", "\n\n", appearance)
        return appearance.strip()

    def exposure_gain(self):
        """Base visibility cost plus every active sensor in the room."""
        gain = tuning.VISIBILITY_EXPOSURE.get(self.visibility, 0)
        gain += sum(
            obj.sensitivity
            for obj in self.contents
            if hasattr(obj, "sensitivity") and not obj.destination
        )
        return gain

    def is_dead_zone(self):
        """
        Truly unwatched: visibility 0 *and* nothing live in the room. The
        distinction matters because a room can look like a dead zone and not
        be one (v0.5's honeypot) — the sweep, `forge`, and the underground
        verbs all trust this method, not the label on the door.
        """
        return self.visibility == 0 and self.exposure_gain() == 0

    def at_object_receive(self, moved_obj, source_location, move_type="move", **kwargs):
        super().at_object_receive(
            moved_obj, source_location, move_type=move_type, **kwargs
        )
        if hasattr(moved_obj, "gain_exposure"):
            gain = self.exposure_gain()
            # Worn gear reads/misreads you (v0.10): the badge identifies,
            # the coat muffles. Gear can shave a positive gain to zero but
            # never mints relief out of walking.
            from typeclasses.gear import room_exposure_delta

            gain = max(0, gain + room_exposure_delta(moved_obj, self))
            if gain:
                moved_obj.gain_exposure(gain)
            self._maybe_log_movement(moved_obj)
        # Watched arrivals: citizens and patrols read whoever walks in.
        # Slightly deferred so reactions (including detainment) land after
        # the movement itself has fully resolved.
        # Completing the Wing's practical portion is a citizen's first
        # merit (v0.12, endowed progress): the corridor room carries the
        # `orients` tag and credits whoever walks it.
        if (
            not moved_obj.db.oriented
            and hasattr(moved_obj, "gain_exposure")
            and self.tags.get("orients", category="grid")
        ):
            moved_obj.db.oriented = True
            from world import grades

            grades.check_reclassification(moved_obj)
        if moved_obj.has_account and move_type in ("move", "traverse"):
            from evennia.utils import delay

            for obj in list(self.contents):
                if obj is not moved_obj and hasattr(obj, "at_watched_arrival"):
                    delay(0.3, obj.at_watched_arrival, moved_obj)
        # An arrival can complete someone ELSE's errand (v0.11's joint
        # work: the other pair of hands walking in counts) — checked for
        # any arrival, cheap for everyone without an active errand.
        if move_type in ("move", "traverse"):
            from world import errands

            for obj in list(self.contents):
                if obj is not moved_obj and obj.db.errand:
                    errands.check(obj, "visit", room=self)

    def _maybe_log_movement(self, moved_obj):
        """
        Live sensors open movement records on citizens hot enough to matter
        (ADR 0005) — rate-limited so the file records a trail, not a flood.
        """
        import time

        if not moved_obj.has_account:
            return
        threshold = tuning.SENSOR_LOG_MIN_EXPOSURE
        # A wellness monitor makes you easier to hear (v0.10).
        from typeclasses.gear import worn_kind

        if worn_kind(moved_obj, "cuff"):
            threshold //= tuning.CUFF_LOG_DIVISOR
        if (moved_obj.db.exposure or 0) < threshold:
            return
        live = [
            obj
            for obj in self.contents
            if hasattr(obj, "sensitivity") and not obj.destination and obj.sensitivity
        ]
        if not live:
            return
        now = time.time()
        if now - (moved_obj.db.last_sensor_log or 0) < tuning.SENSOR_LOG_COOLDOWN:
            return
        moved_obj.db.last_sensor_log = now
        from world import records

        records.add_record(
            moved_obj,
            f"Logged at {self.key}",
            author=live[0].key,
            kind="observation",
        )
