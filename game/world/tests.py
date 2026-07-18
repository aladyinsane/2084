"""
v0.1 spine tests: the exposure loop and the dossier stub.

Mechanics are unit-tested; tone is playtested (docs/engineering/architecture.md).
Run from game/ with:  evennia test --settings settings.py .
"""

from evennia.utils import create
from evennia.utils.test_resources import EvenniaCommandTest, EvenniaTest

from commands.dossier import CmdDossier
from world import tuning


class TestExposureLoop(EvenniaTest):
    def test_entering_watched_room_gains_exposure(self):
        self.room2.db.visibility = 4
        self.char1.db.exposure = 0
        self.char1.move_to(self.room2)
        self.assertEqual(
            self.char1.db.exposure, tuning.VISIBILITY_EXPOSURE[4]
        )

    def test_shallow_end_costs_nothing(self):
        # Vis 0-1 must be free (principle 10's protected shallow end).
        self.room2.db.visibility = 1
        self.char1.db.exposure = 0
        self.char1.move_to(self.room2)
        self.assertEqual(self.char1.db.exposure, 0)

    def test_exit_modifier_adds_exposure(self):
        self.room2.db.visibility = 0
        self.exit.db.exposure_modifier = 2
        self.char1.db.exposure = 0
        self.char1.execute_cmd(self.exit.key)
        self.assertEqual(self.char1.db.exposure, 2)

    def test_exposure_clamps_at_max_and_floor(self):
        self.char1.gain_exposure(tuning.EXPOSURE_MAX + 50)
        self.assertEqual(self.char1.db.exposure, tuning.EXPOSURE_MAX)
        self.char1.gain_exposure(-(tuning.EXPOSURE_MAX + 50))
        self.assertEqual(self.char1.db.exposure, 0)

    def test_decay_tick_reduces_but_not_below_zero(self):
        script = create.create_script("typeclasses.scripts.ExposureDecayScript")
        self.char1.db.exposure = 1
        script.at_repeat()
        self.assertEqual(self.char1.db.exposure, max(0, 1 - tuning.EXPOSURE_DECAY_AMOUNT))
        script.at_repeat()
        self.assertEqual(self.char1.db.exposure, 0)
        script.stop()

    def test_no_class_no_race_anywhere(self):
        # ADR 0002's review rule, automated: a character must not carry
        # race/class-shaped attributes.
        for forbidden in ("race", "class", "charclass", "archetype"):
            self.assertIsNone(self.char1.attributes.get(forbidden))


class TestDossier(EvenniaCommandTest):
    def test_dossier_shows_citizen_file(self):
        output = self.call(CmdDossier(), "")
        self.assertIn("CITIZEN FILE", output)
        self.assertIn("Exposure", output)
