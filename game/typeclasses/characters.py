"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.objects.objects import DefaultCharacter
from evennia.typeclasses.attributes import AttributeProperty

from world import forms, tuning

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
        if amount > 0:
            # Lifetime earnings feed the citizen grade (v0.12) — tracked
            # apart from the spendable balance so spending never demotes.
            earned = self.db.influence_earned or {}
            earned[faction] = earned.get(faction, 0) + amount
            self.db.influence_earned = earned
            from world import grades

            grades.check_reclassification(self)
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
        # how watched here is, and how hot they are. "Exposure" and
        # "Visibility" are spelled out because "Exp"/"Vis" read as
        # experience points and an ability score to every MUD veteran
        # (first-human-playtest finding #3). "Grade" is spelled out too,
        # same reasoning — "G5" reads as a stat abbreviation, not a name.
        from typeclasses.gear import room_exposure_delta
        from world import grades, tuning
        from world.colors import VIS_COLORS, exposure_color

        room = self.location
        vis = getattr(room, "visibility", None)
        if vis is None:
            vis_text = "-"
        else:
            vis_text = f"{VIS_COLORS.get(vis, '|w')}{vis}|n"
            # The static digit is what the room is built as; live sensors
            # and worn gear can pull the actual cost of entering it away
            # from that (rooms.py's exposure_gain()). Only say so when the
            # two disagree, so a room with nothing extra going on stays as
            # quiet on the prompt as it always was.
            live_gain = max(0, room.exposure_gain() + room_exposure_delta(self, room))
            base_gain = tuning.VISIBILITY_EXPOSURE.get(vis, 0)
            delta = live_gain - base_gain
            if delta:
                vis_text += f"|=m(|n{delta:+d}|=m)|n"

        exposure = self.exposure
        last = self.db.last_prompt_exposure
        trend = ""
        if last is not None and exposure != last:
            trend = "|r^|n" if exposure > last else "|gv|n"
        self.db.last_prompt_exposure = exposure

        return (
            f"|=m[|nGrade:{grades.grade_of(self)} "
            f"Visibility:{vis_text} "
            f"Exposure:{exposure_color(exposure)}{exposure}|n{trend}|=m]|n > "
        )

    def send_prompt(self):
        self.msg(prompt=self.get_prompt())

    def at_post_move(self, source_location, move_type="move", **kwargs):
        super().at_post_move(source_location, move_type=move_type, **kwargs)
        if self.has_account:
            self.send_prompt()
            # Errands listen to the verbs you already have (v0.9).
            if self.location and self.db.errand:
                from world import errands

                errands.check(self, "visit", room=self.location)

    def login_digest(self):
        """
        "Since you were last on the Grid:" — what accumulated in your file
        while you were away, plus who of your circle is out here now
        (v0.8.5, principle 8 pointed at the returning player). Returns
        None when there is nothing to tell.
        """
        import time

        from world import circles, records, tuning

        last_on = self.db.last_on
        if not last_on:
            return None
        lines = []
        new = [
            rec
            for rec in records.records_for(self)
            if (rec.db.audit and rec.db.audit[0]["at"] > last_on)
            and not rec.db.redacted
        ]
        if new:
            shown = new[-tuning.DIGEST_MAX_ENTRIES:]
            lines.append(
                f"Your file grew by {len(new)} "
                f"entr{'ies' if len(new) != 1 else 'y'} while you were "
                "elsewhere:"
            )
            lines.extend(f"  - {rec.db.content}" for rec in shown)
        slug = circles.circle_of(self)
        if slug:
            out = [m.key for m in circles.online_members(slug) if m is not self]
            if out:
                lines.append(
                    f"Of {circles.circle_name(slug)}: "
                    f"{', '.join(sorted(out))} — on the Grid right now."
                )
        if not lines:
            return None
        return (
            "|=mSince you were last on the Grid:|n\n" + "\n".join(lines)
        )

    def at_post_puppet(self, **kwargs):
        super().at_post_puppet(**kwargs)
        # The first minute of the first session (v0.13): one card, three
        # verbs, and a direction. Never shown again.
        if not self.db.welcomed:
            self.db.welcomed = True
            self.msg(
                forms.form_box(
                    "|wNOTICE OF ARRIVAL (FORM 1-A)|n",
                    "|=mYou are registered. You are expected. Orientation",
                    "waits EAST of the Assignment Hall; the Grid credits",
                    "completing it. When unsure, type |cnext|=m. For the",
                    "permitted forms of assistance, |chelp|=m. The Grid",
                    "provides.|n",
                )
            )
        digest = self.login_digest()
        if digest:
            self.msg(digest)
        self.send_prompt()

    def at_post_unpuppet(self, account=None, session=None, **kwargs):
        super().at_post_unpuppet(account=account, session=session, **kwargs)
        if not self.sessions.count():
            import time

            self.db.last_on = time.time()
