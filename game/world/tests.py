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

    @staticmethod
    def _file_contents(char):
        from world import records

        return [rec.db.content for rec in records.records_for(char)]

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
            any("DETAINED" in n for n in self._file_contents(self.char1))
        )
        # Waiting out the clock releases you, changed.
        for _ in range(tuning.WAIT_RELEASE_TURNS):
            self.char1.execute_cmd("wait")
        self.assertFalse(watch.is_detained(self.char1))
        self.assertEqual(self.char1.location, self.room1)
        self.assertEqual(self.char1.db.exposure, tuning.RELEASE_EXPOSURE)
        self.assertTrue(
            any("lack of interest" in n for n in self._file_contents(self.char1))
        )

    def test_confess_releases_with_note(self):
        from world import watch

        self._cell()
        self.char1.db.exposure = 60
        watch.detain(self.char1)
        self.char1.execute_cmd("confess")
        self.assertFalse(watch.is_detained(self.char1))
        self.assertTrue(
            any("Confession" in n for n in self._file_contents(self.char1))
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


class TestRecords(EvenniaTest):
    """v0.3: the record layer vs the truth layer."""

    def _incident(self, content="Jaywalked meaningfully"):
        from world import records

        return records.add_record(self.char1, content)

    def test_creation_seeds_audit(self):
        rec = self._incident()
        self.assertEqual(len(rec.db.audit), 1)
        self.assertEqual(rec.db.audit[0]["action"], "created")

    def test_amend_keeps_old_content_in_audit(self):
        from world import records

        rec = self._incident("Original truth")
        records.amend(rec, "Improved truth", actor=self.char1, authorized=False)
        self.assertEqual(rec.db.content, "Improved truth")
        self.assertEqual(rec.db.audit[-1]["content"], "Original truth")
        self.assertEqual(rec.db.audit[-1]["action"], "amended (unauthorized)")

    def test_redact_hides_but_preserves(self):
        from world import records

        rec = self._incident()
        records.redact(rec, actor=self.char1)
        self.assertTrue(rec.db.redacted)
        self.assertEqual(rec.db.audit[-1]["action"], "redacted")
        # Still queryable with include_redacted; gone without.
        self.assertIn(rec, records.records_for(self.char1))
        self.assertNotIn(
            rec, records.records_for(self.char1, include_redacted=False)
        )

    def test_numbering_gap_survives_redaction(self):
        from world import records

        self._incident("First")
        second = self._incident("Second")
        self._incident("Third")
        records.redact(second, actor=self.char1)
        # Entry 3 is still entry 3; entry 2 still *refers* to the redacted one.
        self.assertEqual(
            records.incident_by_number(self.char1, 3).db.content, "Third"
        )
        self.assertTrue(records.incident_by_number(self.char1, 2).db.redacted)


class TestCivic(EvenniaTest):
    """v0.3: work, observe, listen, petition, forge."""

    def setUp(self):
        super().setUp()
        self.room1.tags.add("workplace", category="grid")
        self.room1.tags.add("gossip_spot", category="grid")

    def _archivist(self):
        archivist = create.create_object(
            "typeclasses.npcs.Citizen", key="the archivist", location=self.room1
        )
        archivist.tags.add("records_service", category="grid")
        return archivist

    def test_work_pays_and_teaches_and_cools(self):
        from world import tuning

        self.char1.db.exposure = 10
        self.char1.execute_cmd("work")
        self.assertEqual(self.char1.skill("clerking"), 1)
        self.assertEqual(
            (self.char1.db.influence or {}).get("Ministry of Records"),
            tuning.WORK_INFLUENCE,
        )
        self.assertEqual(
            self.char1.db.exposure, 10 - tuning.WORK_EXPOSURE_RELIEF
        )
        # Cooldown: an immediate second shift changes nothing.
        self.char1.execute_cmd("work")
        self.assertEqual(self.char1.skill("clerking"), 1)

    def test_observe_improves_skill(self):
        self.char1.execute_cmd("observe")
        self.assertEqual(self.char1.skill("observation"), 1)

    def test_petition_amend_costs_and_amends(self):
        from world import records, tuning, watch

        self._archivist()
        watch.add_record_note(self.char1, "DETAINED: test")
        self.char1.db.influence = {"Ministry of Records": tuning.AMEND_COST}
        self.char1.db.exposure = 0
        self.char1.execute_cmd("petition amend 1 = Attended a records seminar")
        rec = records.incident_by_number(self.char1, 1)
        self.assertEqual(rec.db.content, "Attended a records seminar")
        self.assertEqual(rec.db.audit[-1]["content"], "DETAINED: test")
        self.assertEqual(
            (self.char1.db.influence or {}).get("Ministry of Records"), 0
        )
        self.assertEqual(self.char1.db.exposure, tuning.SERVICE_EXPOSURE)

    def test_petition_refused_without_standing(self):
        from world import records, watch

        self._archivist()
        watch.add_record_note(self.char1, "DETAINED: test")
        self.char1.db.influence = {}
        self.char1.execute_cmd("petition redact 1")
        self.assertFalse(records.incident_by_number(self.char1, 1).db.redacted)

    def test_forge_success_rewrites_off_the_books(self):
        from unittest.mock import patch

        from world import records, watch

        self.room1.db.visibility = 0
        watch.add_record_note(self.char1, "DETAINED: test")
        with patch("commands.civic.random.random", return_value=0.0):
            self.char1.execute_cmd("forge 1 = Commended for vigilance")
        rec = records.incident_by_number(self.char1, 1)
        self.assertEqual(rec.db.content, "Commended for vigilance")
        self.assertEqual(rec.db.audit[-1]["action"], "amended (unauthorized)")
        self.assertEqual(self.char1.skill("forgery"), 1)

    def test_forge_failure_is_an_incident(self):
        from unittest.mock import patch

        from world import records, tuning, watch

        self.room1.db.visibility = 0
        watch.add_record_note(self.char1, "DETAINED: test")
        self.char1.db.exposure = 0
        with patch("commands.civic.random.random", return_value=0.99):
            self.char1.execute_cmd("forge 1 = Commended for vigilance")
        contents = [r.db.content for r in records.records_for(self.char1)]
        self.assertTrue(any("tampering" in c for c in contents))
        self.assertEqual(self.char1.db.exposure, tuning.FORGE_FAIL_EXPOSURE)

    def test_forge_needs_a_dead_zone(self):
        from world import records, watch

        self.room1.db.visibility = 3
        watch.add_record_note(self.char1, "DETAINED: test")
        self.char1.execute_cmd("forge 1 = Commended for vigilance")
        self.assertEqual(
            records.incident_by_number(self.char1, 1).db.content,
            "DETAINED: test",
        )

    def test_listen_surfaces_others_not_self(self):
        from world import records

        records.add_record(self.char2, "Taken by the Watch at the plaza")
        records.add_record(self.char1, "My own embarrassment")
        old = self.char1.msg
        seen = []
        self.char1.msg = lambda text=None, **kw: seen.append(str(text))
        try:
            self.char1.execute_cmd("listen")
        finally:
            self.char1.msg = old
        blob = "\n".join(seen)
        self.assertIn("Char2", blob)
        self.assertNotIn("My own embarrassment", blob)

    def test_sensor_logs_movement_with_cooldown(self):
        from world import records, tuning

        self.room2.db.visibility = 0
        sensor = create.create_object(
            "typeclasses.objects.Sensor", key="a lens", location=self.room2
        )
        sensor.db.sensitivity = 1
        self.char1.db.exposure = tuning.SENSOR_LOG_MIN_EXPOSURE
        self.char1.move_to(self.room2)
        self.char1.move_to(self.room1)
        self.char1.db.exposure = tuning.SENSOR_LOG_MIN_EXPOSURE
        self.char1.move_to(self.room2)  # within cooldown: no second entry
        observations = records.records_for(self.char1, kind="observation")
        self.assertEqual(len(observations), 1)
        self.assertIn("Logged at", observations[0].db.content)

    def test_sweep_cannot_reach_dead_zones(self):
        from typeclasses.scripts import WatchSweepScript
        from world import watch

        cell = create.create_object(
            "typeclasses.rooms.Room", key="Holding Cell (test)"
        )
        cell.tags.add("holding_cell", category="grid")
        script = create.create_script(WatchSweepScript)
        self.room1.db.visibility = 0
        self.char1.db.exposure = 90
        for _ in range(50):
            script.at_repeat()
        self.assertFalse(watch.is_detained(self.char1))
        script.stop()
