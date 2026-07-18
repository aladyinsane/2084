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


class TestWatch(EvenniaTest):
    """v0.2: sensors, sweep, detainment, release."""

    def _cell(self):
        cell = create.create_object(
            "typeclasses.rooms.Room", key="Holding Cell (test)"
        )
        cell.tags.add("holding_cell", category="grid")
        self.room1.tags.add("release_point", category="grid")
        return cell

    def test_active_sensor_adds_exposure_broken_does_not(self):
        self.room2.db.visibility = 0
        sensor = create.create_object(
            "typeclasses.objects.Sensor", key="a scanner", location=self.room2
        )
        sensor.db.sensitivity = 3
        self.char1.db.exposure = 0
        self.char1.move_to(self.room2)
        self.assertEqual(self.char1.db.exposure, 3)
        sensor.db.active = False
        self.char1.move_to(self.room1)
        self.char1.db.exposure = 0
        self.char1.move_to(self.room2)
        self.assertEqual(self.char1.db.exposure, 0)

    def test_detain_swaps_cmdset_and_release_restores(self):
        from world import tuning, watch

        cell = self._cell()
        self.char1.db.exposure = 60
        self.assertTrue(watch.detain(self.char1, reason="test sweep"))
        self.assertEqual(self.char1.location, cell)
        self.assertTrue(watch.is_detained(self.char1))
        # Movement vocabulary is gone; detention verbs exist.
        self.char1.execute_cmd("north")
        self.assertTrue(
            any("DETAINED" in n for n in self.char1.db.record_notes)
        )
        # Waiting out the clock releases you, changed.
        for _ in range(tuning.WAIT_RELEASE_TURNS):
            self.char1.execute_cmd("wait")
        self.assertFalse(watch.is_detained(self.char1))
        self.assertEqual(self.char1.location, self.room1)
        self.assertEqual(self.char1.db.exposure, tuning.RELEASE_EXPOSURE)
        self.assertTrue(
            any("lack of interest" in n for n in self.char1.db.record_notes)
        )

    def test_confess_releases_with_note(self):
        from world import watch

        self._cell()
        self.char1.db.exposure = 60
        watch.detain(self.char1)
        self.char1.execute_cmd("confess")
        self.assertFalse(watch.is_detained(self.char1))
        self.assertTrue(
            any("Confession" in n for n in self.char1.db.record_notes)
        )

    def test_demand_resets_wait_clock(self):
        from world import watch

        self._cell()
        self.char1.db.exposure = 60
        watch.detain(self.char1)
        self.char1.execute_cmd("wait")
        self.char1.execute_cmd("wait")
        self.char1.execute_cmd("demand")
        self.assertEqual(self.char1.db.detained_wait, 0)
        self.assertTrue(watch.is_detained(self.char1))

    def test_shallow_end_never_swept(self):
        from typeclasses.scripts import WatchSweepScript
        from world import tuning, watch

        self._cell()
        script = create.create_script(WatchSweepScript)
        self.char1.db.exposure = tuning.SWEEP_MIN_EXPOSURE - 1
        # Deterministic: below the floor, no roll happens at all — even a
        # hundred ticks never touch the character.
        for _ in range(100):
            script.at_repeat()
        self.assertFalse(watch.is_detained(self.char1))
        self.assertEqual(
            self.char1.db.exposure, tuning.SWEEP_MIN_EXPOSURE - 1
        )
        script.stop()

    def test_detainment_raises_alert(self):
        from world import watch

        self._cell()
        watch.set_alert(0)
        self.char1.db.exposure = 60
        watch.detain(self.char1)
        self.assertEqual(watch.get_alert(), 1)
        watch.set_alert(0)

    def test_citizen_reaction_tiers(self):
        from world import tuning

        clerk = create.create_object(
            "typeclasses.npcs.Citizen", key="the clerk", location=self.room1
        )
        # Tier selection is pure state; the delayed room-wiring is covered by
        # in-game verification (found the traverse-vs-move gap there once
        # already — see v0.2 notes).
        self.char1.db.exposure = 0
        clerk.at_watched_arrival(self.char1)  # calm: no exception, no detain
        self.char1.db.exposure = tuning.NOTICE_EXPOSURE
        clerk.at_watched_arrival(self.char1)
        self.char1.db.exposure = tuning.HOT_EXPOSURE
        clerk.at_watched_arrival(self.char1)
        self.assertFalse(self.char1.tags.get("detained", category="status"))

    def test_patrol_detains_hot_arrivals(self):
        from world import tuning, watch

        self._cell()
        patrol = create.create_object(
            "typeclasses.npcs.WatchPatrol", key="patrol", location=self.room1
        )
        self.char1.db.exposure = tuning.DETAIN_THRESHOLD
        patrol.at_watched_arrival(self.char1)
        self.assertTrue(watch.is_detained(self.char1))
        watch.release(self.char1)
