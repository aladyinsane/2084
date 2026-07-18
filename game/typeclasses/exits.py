"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""

from evennia.objects.objects import DefaultExit
from evennia.typeclasses.attributes import AttributeProperty

from .objects import ObjectParent


class Exit(ObjectParent, DefaultExit):
    """
    An exit in the Grid.

    `exposure_modifier` is extra exposure charged for using this particular
    passage — scanners, checkpoints, guarded doors — on top of whatever the
    destination room's visibility costs (ADR 0004).
    """

    exposure_modifier = AttributeProperty(0)

    def at_traverse(self, traversing_object, target_location, **kwargs):
        # Charged before the move so the arrival prompt already includes it —
        # and unconditionally: a scanner scans you whether or not you get
        # through the gate.
        if self.exposure_modifier and hasattr(traversing_object, "gain_exposure"):
            traversing_object.gain_exposure(self.exposure_modifier)
        super().at_traverse(traversing_object, target_location, **kwargs)
