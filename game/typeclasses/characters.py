"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.objects.objects import DefaultCharacter
from evennia.typeclasses.attributes import AttributeProperty

from world import tuning

from .objects import ObjectParent


class Character(ObjectParent, DefaultCharacter):
    """
    A citizen of the Grid.

    There is no race and no class, by decision (ADR 0002): a character is
    skills (rise by use), standing (granted and revoked by institutions),
    influence (a per-faction spendable ledger) and exposure (how visible you
    currently are to the state — the number where down is good, ADR 0003).
    """

    exposure = AttributeProperty(0)

    def at_object_creation(self):
        super().at_object_creation()
        self.db.skills = {}
        self.db.influence = {}
        self.db.standing = {}

    def gain_exposure(self, amount):
        """Adjust exposure (negative allowed), clamped to [0, EXPOSURE_MAX]."""
        self.exposure = max(0, min(tuning.EXPOSURE_MAX, self.exposure + amount))
        return self.exposure

    def improve_skill(self, name, cap=None):
        """Skill-by-use (ADR 0002/0003): +1 per meaningful use, soft-capped."""
        cap = tuning.SKILL_CAP if cap is None else cap
        skills = self.db.skills or {}
        value = skills.get(name, 0)
        if value < cap:
            skills[name] = value + 1
            self.db.skills = skills
        return skills.get(name, 0)

    def skill(self, name):
        return (self.db.skills or {}).get(name, 0)

    def gain_influence(self, faction, amount):
        influence = self.db.influence or {}
        influence[faction] = influence.get(faction, 0) + amount
        self.db.influence = influence
        return influence[faction]

    def spend_influence(self, faction, amount):
        """Spend standing; returns False (untouched) if there isn't enough."""
        influence = self.db.influence or {}
        if influence.get(faction, 0) < amount:
            return False
        influence[faction] -= amount
        self.db.influence = influence
        return True

    def get_prompt(self):
        # The trend-telegraph promised by principle 3: the player always sees
        # how watched here is, and how hot they are.
        vis = getattr(self.location, "visibility", "-")
        return f"|=m[|nVis:{vis} Exp:{self.exposure}|=m]|n > "

    def send_prompt(self):
        self.msg(prompt=self.get_prompt())

    def at_post_move(self, source_location, move_type="move", **kwargs):
        super().at_post_move(source_location, move_type=move_type, **kwargs)
        if self.has_account:
            self.send_prompt()

    def at_post_puppet(self, **kwargs):
        super().at_post_puppet(**kwargs)
        self.send_prompt()
