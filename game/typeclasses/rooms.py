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

    def at_object_receive(self, moved_obj, source_location, move_type="move", **kwargs):
        super().at_object_receive(
            moved_obj, source_location, move_type=move_type, **kwargs
        )
        gain = tuning.VISIBILITY_EXPOSURE.get(self.visibility, 0)
        if gain and hasattr(moved_obj, "gain_exposure"):
            moved_obj.gain_exposure(gain)
