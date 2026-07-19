"""
NPCs of the Grid.

Citizens react to arrivals by exposure tier — the world reading your record
back to you (principle 3's telegraph, worn by people instead of numbers).
Watch patrols are the telegraph with teeth: they keep to watched streets,
their density tracks the district alert level, and crossing one while hot
means detainment.
"""

import random

from evennia.objects.objects import DefaultCharacter

from world import tuning

from .objects import ObjectParent


class Citizen(ObjectParent, DefaultCharacter):
    """
    A resident of the Grid. Subclasses (or prototypes) set reaction strings;
    the room calls `at_watched_arrival` for each arriving character.
    """

    def at_object_creation(self):
        super().at_object_creation()
        # (cold, noticed, calm) reaction poses, formatted with {name}.
        self.db.react_calm = "{npc} glances up, then back to their work."
        self.db.react_noticed = "{npc} looks at {name} a moment too long."
        self.db.react_hot = (
            "{npc} steps carefully away from {name}, suddenly busy elsewhere."
        )

    def at_watched_arrival(self, char):
        exposure = char.db.exposure or 0
        if exposure >= tuning.HOT_EXPOSURE:
            template = self.db.react_hot
        elif exposure >= tuning.NOTICE_EXPOSURE:
            template = self.db.react_noticed
        else:
            template = self.db.react_calm
        if template and self.location:
            self.location.msg_contents(
                template.format(npc=self.get_display_name(char), name=char.key),
                exclude=(self,),
            )


class Informant(Citizen):
    """
    A citizen who hears things, and can be persuaded to pass them on.

    `db.loyalty` is the hidden truth: "street" informants genuinely serve
    the cell that recruits them (they tip the cell when a member is taken);
    "ministry" plants serve the Watch, and being recruited is their whole
    assignment — they file on the cell, slowly, from the inside.

    Nothing in the game states loyalty outright below a practiced
    observation skill: `db.demeanor` is the only tell most citizens will
    ever get, and it is written to be true without being conclusive.
    """

    def at_object_creation(self):
        super().at_object_creation()
        self.db.loyalty = "street"
        self.db.recruited_by = None
        self.db.last_report = 0
        self.db.demeanor = "They give away exactly nothing, professionally."


class WatchPatrol(Citizen):
    """
    An officer of the Watch on foot patrol. Wanders rooms at or above
    PATROL_MIN_VISIBILITY; reads everyone who crosses their path; detains
    anyone at or past the detain threshold.
    """

    def at_object_creation(self):
        super().at_object_creation()
        self.db.desc = (
            "Grey uniform, mirrored visor, unhurried step. The Watch does not "
            "patrol to find anything; it patrols so that you know it could."
        )
        self.db.react_calm = ""  # patrols ignore nobodies
        self.db.react_noticed = (
            "{npc}'s visor tracks {name} for three slow steps before moving on."
        )
        self.db.react_hot = ""  # the hot case detains instead; no pose needed

    def at_watched_arrival(self, char):
        if (char.db.exposure or 0) >= tuning.DETAIN_THRESHOLD:
            from world import watch

            watch.detain(char, reason="flagged on sight by a street patrol")
            return
        super().at_watched_arrival(char)

    def patrol_step(self):
        """Take one wander step; called by the patrol script."""
        location = self.location
        if not location:
            return
        # Detain-on-sight also applies to whoever is already here.
        for obj in location.contents:
            if obj.has_account and (obj.db.exposure or 0) >= tuning.DETAIN_THRESHOLD:
                from world import watch

                watch.detain(obj, reason="flagged on sight by a street patrol")
        exits = [
            ex
            for ex in location.contents
            if ex.destination
            and (ex.destination.db.visibility or 0) >= tuning.PATROL_MIN_VISIBILITY
        ]
        if not exits:
            return
        exit_obj = random.choice(exits)
        old_room = location
        self.move_to(exit_obj.destination, quiet=True, move_type="patrol")
        old_room.msg_contents(f"{self.key} sweeps out, unhurried, toward the {exit_obj.key}.")
        self.location.msg_contents(
            f"{self.key} walks through in measured steps, visor turning as it goes.",
            exclude=(self,),
        )
        # Arriving patrols read the room like anyone arriving would be read.
        for obj in self.location.contents:
            if obj.has_account:
                self.at_watched_arrival(obj)
