"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia.objects.objects import DefaultRoom
from evennia.typeclasses.attributes import AttributeProperty

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

    def exposure_gain(self):
        """Base visibility cost plus every active sensor in the room."""
        gain = tuning.VISIBILITY_EXPOSURE.get(self.visibility, 0)
        gain += sum(
            obj.sensitivity
            for obj in self.contents
            if hasattr(obj, "sensitivity") and not obj.destination
        )
        return gain

    def at_object_receive(self, moved_obj, source_location, move_type="move", **kwargs):
        super().at_object_receive(
            moved_obj, source_location, move_type=move_type, **kwargs
        )
        if hasattr(moved_obj, "gain_exposure"):
            gain = self.exposure_gain()
            if gain:
                moved_obj.gain_exposure(gain)
        # Watched arrivals: citizens and patrols read whoever walks in.
        # Slightly deferred so reactions (including detainment) land after
        # the movement itself has fully resolved.
        if moved_obj.has_account and move_type in ("move", "traverse"):
            from evennia.utils import delay

            for obj in list(self.contents):
                if obj is not moved_obj and hasattr(obj, "at_watched_arrival"):
                    delay(0.3, obj.at_watched_arrival, moved_obj)
