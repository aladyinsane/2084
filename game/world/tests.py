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

    def test_border_matches_the_rest_of_the_bureaucratic_forms(self):
        """The dossier drifted to its own width before this fix (2026-07-28's
        presentation tidy-up); lock in the match with form_box()'s width."""
        from world.forms import FORM_WIDTH

        output = self.call(CmdDossier(), "")
        self.assertIn("=" * FORM_WIDTH, output)

    def test_standing_shown_as_none_recorded_at_zero(self):
        """Round-two playtest finding 2: the line vanished entirely at
        zero, so a new citizen had no way to learn "standing" existed."""
        output = self.call(CmdDossier(), "")
        self.assertIn("Standing with institutions:", output)
        self.assertIn("none recorded yet", output)

    def test_consecutive_repeats_collapse_with_a_count(self):
        """Round-two playtest finding 7: 35 duplicate absence incidents in
        a row. Consecutive repeats should roll up; non-consecutive ones
        (interrupted by a different incident) should not."""
        from world import records

        records.add_record(self.char1, "Absent from mandatory civic assembly")
        records.add_record(self.char1, "Absent from mandatory civic assembly")
        records.add_record(self.char1, "Absent from mandatory civic assembly")
        records.add_record(self.char1, "Papers checked in the street; cleared.")
        records.add_record(self.char1, "Absent from mandatory civic assembly")
        output = self.call(CmdDossier(), "")
        self.assertIn(
            "1-3. Absent from mandatory civic assembly (3)", output
        )
        self.assertIn("4. Papers checked in the street; cleared.", output)
        self.assertIn("5. Absent from mandatory civic assembly", output)
        self.assertNotIn("5. Absent from mandatory civic assembly (", output)


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

    def test_number_is_assigned_at_creation_not_derived_from_position(self):
        """ADR 0011 prerequisite: the number lives on the record itself
        (`db.number`), assigned from the subject's own counter, rather than
        being computed live from list position — the latter is only stable
        as long as nothing is ever deleted, which compaction will do."""
        from world import records

        first = self._incident("First")
        second = self._incident("Second")
        self.assertEqual(first.db.number, 1)
        self.assertEqual(second.db.number, 2)
        # Deleting the object a naive positional scheme would call "#1"
        # doesn't renumber what's left — #2 stays #2.
        first.delete()
        self.assertEqual(
            records.incident_by_number(self.char1, 2).db.content, "Second"
        )

    def test_numbering_is_per_subject(self):
        from world import records

        self._incident("char1's only incident")
        other = records.add_record(self.char2, "char2's first incident")
        self.assertEqual(other.db.number, 1)

    def test_only_incidents_are_numbered(self):
        from world import records

        rec = records.add_record(self.char1, "A movement log", kind="observation")
        self.assertIsNone(rec.db.number)


class TestCivic(EvenniaTest):
    """v0.3: work, observe, listen, petition, forge."""

    def setUp(self):
        super().setUp()
        self.room1.tags.add("workplace", category="grid")
        self.room1.tags.add("gossip_spot", category="grid")

    def _captured(self, char, command):
        old = char.msg
        seen = []
        char.msg = lambda text=None, **kw: seen.append(str(text))
        try:
            char.execute_cmd(command)
        finally:
            char.msg = old
        return "\n".join(seen)

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
            (self.char1.db.standing or {}).get("Ministry of Records"),
            tuning.WORK_INFLUENCE,
        )
        self.assertEqual(self.char1.db.credits, tuning.WORK_INFLUENCE)
        self.assertEqual(
            self.char1.db.exposure, 10 - tuning.WORK_EXPOSURE_RELIEF
        )
        # Cooldown: an immediate second shift changes nothing.
        self.char1.execute_cmd("work")
        self.assertEqual(self.char1.skill("clerking"), 1)

    def test_off_cooldown_texture_reflects_how_close_the_next_shift_is(self):
        # Playtest finding, picked up in the solo-fun pass: off-cooldown
        # gave no sense of when the next shift opens. Now it reads
        # differently depending on how much of the cooldown has elapsed.
        import time
        from commands.civic import CmdWork
        from world import tuning

        self.char1.db.last_work = time.time()
        blob = self._captured(self.char1, "work")
        self.assertIn(blob, CmdWork.OFF_COOLDOWN_FAR)

        self.char1.db.last_work = (
            time.time() - tuning.WORK_COOLDOWN * tuning.WORK_NEAR_COOLDOWN_FRACTION
        )
        blob = self._captured(self.char1, "work")
        self.assertIn(blob, CmdWork.OFF_COOLDOWN_NEAR)

    def test_observe_improves_skill(self):
        self.char1.execute_cmd("observe")
        self.assertEqual(self.char1.skill("observation"), 1)

    def test_petition_amend_costs_and_amends(self):
        from world import records, tuning, watch

        self._archivist()
        watch.add_record_note(self.char1, "DETAINED: test")
        self.char1.db.credits = tuning.AMEND_COST
        self.char1.db.exposure = 0
        self.char1.execute_cmd("petition amend 1 = Attended a records seminar")
        rec = records.incident_by_number(self.char1, 1)
        self.assertEqual(rec.db.content, "Attended a records seminar")
        self.assertEqual(rec.db.audit[-1]["content"], "DETAINED: test")
        self.assertEqual(self.char1.db.credits, 0)
        self.assertEqual(self.char1.db.exposure, tuning.SERVICE_EXPOSURE)

    def test_petition_refused_without_credits(self):
        from world import records, watch

        self._archivist()
        watch.add_record_note(self.char1, "DETAINED: test")
        self.char1.db.credits = 0
        self.char1.execute_cmd("petition redact 1")
        self.assertFalse(records.incident_by_number(self.char1, 1).db.redacted)

    def test_forge_success_rewrites_off_the_books(self):
        from unittest.mock import patch

        from world import records, watch

        self.room1.db.visibility = 0
        watch.add_record_note(self.char1, "DETAINED: test")
        with patch("world.checks.opposed_check", return_value=True):
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
        with patch("world.checks.opposed_check", return_value=False):
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


class TestWorldBuild(EvenniaTest):
    """The ADR 0007 lint: build Sector 9 and check the geometry's promises."""

    def test_build_is_grid_consistent(self):
        from world import build

        rooms = build.build()
        self.assertEqual(len(rooms), 16)  # 10 street + 5 orientation + cell
        for room in rooms.values():
            for ex in room.contents:
                if not ex.destination or ex.key not in build.OPPOSITE:
                    continue
                reciprocals = [
                    e
                    for e in ex.destination.contents
                    if e.destination == room and e.key == build.OPPOSITE[ex.key]
                ]
                self.assertTrue(
                    reciprocals,
                    f"{room.key} --{ex.key}--> {ex.destination.key} "
                    "has no true reciprocal",
                )
        # The holding cell is off-plan: no exits in, none out.
        self.assertFalse([e for e in rooms["cell"].contents if e.destination])

    def test_bolt_hole_props_are_examinable(self):
        """Round-two playtest finding 5, from round one's finding 3: the
        room describes blankets/cots/rations/kettle; the described tells
        must actually be lookable, or the honeypot's warning is a lie."""
        from world import build

        rooms = build.build()
        bolthole = rooms["bolthole"]
        for alias in ("blankets", "cots", "rations", "kettle"):
            found = [
                obj
                for obj in bolthole.contents
                if alias in [a.lower() for a in obj.aliases.all()] + [obj.key.lower()]
            ]
            self.assertTrue(found, f"the Bolt-Hole describes {alias} but none exist")
            self.assertTrue(found[0].db.desc, f"{alias} has no desc to look at")

    def test_built_npcs_have_a_deflection_line(self):
        """Extends the described-devices lint (principle 9) to cover being
        talked at: every citizen the build creates should have a brush-off
        written for it, not just nomatch's generic line (round-two
        playtest finding 6, from round one's finding 2)."""
        from typeclasses.npcs import Citizen
        from world import build

        rooms = build.build()
        npcs = [
            obj
            for room in rooms.values()
            for obj in room.contents
            if isinstance(obj, Citizen)
        ]
        self.assertTrue(npcs)
        for npc in npcs:
            self.assertTrue(npc.db.deflection, f"{npc.key} has no deflection line")

    def test_described_devices_exist(self):
        # Principle 9's in-world corollary, learned in v0.3 verification:
        # if a room description mentions a watchscreen/scanner/lens, a
        # Sensor object must exist there for `observe` to find.
        from world import build

        rooms = build.build()
        for tag, (_, _, desc) in build.ROOMS.items():
            promises = any(
                word in desc.lower()
                for word in ("watchscreen", "scanner", "lens array")
            )
            if not promises:
                continue
            sensors = [
                obj
                for obj in rooms[tag].contents
                if hasattr(obj, "sensitivity") and not obj.destination
            ]
            self.assertTrue(
                sensors, f"{rooms[tag].key} describes a device but has none"
            )


class TestStandingAndPaperwork(EvenniaTest):
    """v0.4: functions, clearance, Form C-1, monitored channel."""

    def setUp(self):
        super().setUp()
        self.room1.tags.add("workplace", category="grid")

    def test_report_assigns_by_recorded_aptitude(self):
        from world import functions

        self.char1.db.skills = {"observation": 5, "clerking": 2}
        self.char1.execute_cmd("report")
        key, spec = functions.current_function(self.char1)
        self.assertEqual(key, "auditor")
        self.assertEqual(
            (self.char1.db.civic_status or {}).get("function"),
            "Auditor, Order Section",
        )
        # The unremarkable become stewards.
        self.char1.db.skills = {}
        self.char1.execute_cmd("report")
        key, _ = functions.current_function(self.char1)
        self.assertEqual(key, "steward")

    def test_function_work_pays_own_ministry_at_own_post(self):
        from world import functions, tuning

        self.char1.db.skills = {"observation": 5}
        functions.assign_function(self.char1)
        # Auditor's post is any room with a device: room1 has none yet.
        self.char1.execute_cmd("work")
        self.assertFalse((self.char1.db.standing or {}).get("Ministry of Order"))
        create.create_object(
            "typeclasses.objects.Sensor", key="a lens", location=self.room1
        )
        self.char1.db.last_work = 0
        self.char1.execute_cmd("work")
        self.assertEqual(
            (self.char1.db.standing or {}).get("Ministry of Order"),
            tuning.FUNCTION_WORK_INFLUENCE,
        )

    def test_release_suspends_function(self):
        from world import functions, watch

        cell = create.create_object(
            "typeclasses.rooms.Room", key="Holding Cell (test)"
        )
        cell.tags.add("holding_cell", category="grid")
        self.room1.tags.add("release_point", category="grid")
        functions.assign_function(self.char1)
        self.char1.db.exposure = 60
        watch.detain(self.char1)
        watch.release(self.char1)
        key, _ = functions.current_function(self.char1)
        self.assertIsNone(key)
        self.assertIn(
            "suspended", (self.char1.db.civic_status or {}).get("function", "")
        )

    def test_clearance_lock_gates_exit(self):
        from evennia.utils.search import search_object

        self.exit.locks.add("traverse:clearance(1)")
        self.exit.db.err_traverse = "Turned away."
        self.char1.execute_cmd(self.exit.key)
        self.assertEqual(self.char1.location, self.room1)  # blocked
        self.char1.db.civic_status = {"clearance": "C-1"}
        self.char1.execute_cmd(self.exit.key)
        self.assertEqual(self.char1.location, self.room2)  # admitted

    def test_adjudicate_c1_paths(self):
        from world import functions, records, watch

        # No function: Form 77 absent.
        approved, reason = functions.adjudicate_c1(self.char1)
        self.assertFalse(approved)
        self.assertIn("Form 77", reason)
        # Function but dirty file: references insufficient.
        functions.assign_function(self.char1)
        watch.add_record_note(self.char1, "DETAINED: test")
        watch.add_record_note(self.char1, "Was unruly in detention.")
        approved, reason = functions.adjudicate_c1(self.char1)
        self.assertFalse(approved)
        self.assertIn("references", reason)
        # Launder the file (the v0.3 loop is the fix): redact one entry.
        records.redact(
            records.incident_by_number(self.char1, 1), actor=self.char1
        )
        approved, _ = functions.adjudicate_c1(self.char1)
        self.assertTrue(approved)
        # Grant sets clearance and exposure.
        self.char1.db.exposure = 0
        functions.grant_c1(self.char1)
        self.assertEqual(functions.clearance_level(self.char1), 1)
        self.assertGreater(self.char1.db.exposure, 0)
        # Already cleared: reapplication refused.
        approved, reason = functions.adjudicate_c1(self.char1)
        self.assertFalse(approved)
        self.assertIn("already holds", reason)

    def test_apply_menu_full_approval_flow(self):
        from world import functions, records, tuning

        archivist = create.create_object(
            "typeclasses.npcs.Citizen", key="the archivist", location=self.room1
        )
        archivist.tags.add("records_service", category="grid")
        functions.assign_function(self.char1)
        self.char1.db.credits = tuning.CLEARANCE_FEE
        self.char1.execute_cmd("apply")   # menu: start
        self.char1.execute_cmd("1")       # take up the pen
        self.char1.execute_cmd("1")       # purpose: to better serve
        self.char1.execute_cmd("1")       # affirm and submit
        self.assertEqual(functions.clearance_level(self.char1), 1)
        self.assertEqual(self.char1.db.credits, 0)
        outcomes = [
            r.db.content
            for r in records.records_for(self.char1, kind="observation")
        ]
        self.assertTrue(any("APPROVED" in c for c in outcomes))

    def test_monitored_channel_charges_speaker(self):
        from evennia.utils import create as ev_create

        from world import tuning

        # Not named "gridwide": on Windows, a running dev server holds the
        # real channel's log file open, and creating a same-key channel in
        # the test tries to rotate that file and dies on the lock. The
        # typeclass is what's under test, not the name.
        channel = ev_create.create_channel(
            "testband", typeclass="typeclasses.channels.MonitoredChannel"
        )
        channel.connect(self.char1)
        self.char1.db.exposure = 0
        channel.msg("test transmission", senders=self.char1)
        self.assertEqual(self.char1.db.exposure, tuning.CHANNEL_EXPOSURE)


class TestTrust(EvenniaTest):
    """v0.5: cells, Section C, informants, assemblies, and the honeypot."""

    def _file_contents(self, char):
        from world import records

        return [rec.db.content for rec in records.records_for(char)]

    def _holding_cell(self):
        room = create.create_object(
            "typeclasses.rooms.Room", key="Holding Cell (test)"
        )
        room.tags.add("holding_cell", category="grid")
        self.room1.tags.add("release_point", category="grid")
        return room

    def _circle_of_two(self, name="redbird"):
        """char1 founds a circle in room1 (a true dead zone) and char2 joins."""
        from world import circles

        slug, err = circles.form(self.char1, name)
        self.assertIsNone(err)
        self.char2.tags.add(slug, category="circle")
        return slug

    def _captured(self, char, command):
        old = char.msg
        seen = []
        char.msg = lambda text=None, **kw: seen.append(str(text))
        try:
            char.execute_cmd(command)
        finally:
            char.msg = old
        return "\n".join(seen)

    # --- cells --------------------------------------------------------------

    def test_circle_forms_only_in_dead_zones(self):
        from world import circles

        self.room1.db.visibility = 3
        self.char1.execute_cmd("circle form redbird")
        self.assertIsNone(circles.circle_of(self.char1))
        self.room1.db.visibility = 0
        self.char1.execute_cmd("circle form redbird")
        self.assertEqual(circles.circle_of(self.char1), "redbird")
        # One cell per citizen.
        _, err = circles.form(self.char1, "second-try")
        self.assertIsNotNone(err)

    def test_invite_and_join_flow(self):
        from world import circles

        self.char1.execute_cmd("circle form redbird")
        self.char1.execute_cmd("circle invite Char2")
        self.assertEqual(self.char2.db.circle_invite, "redbird")
        self.char2.execute_cmd("circle join")
        self.assertEqual(circles.circle_of(self.char2), "redbird")
        self.assertEqual(len(circles.members_of("redbird")), 2)
        # Leaving works, and the last member out dissolves the registry entry.
        self.char2.execute_cmd("circle leave")
        self.assertIsNone(circles.circle_of(self.char2))
        circles.leave(self.char1)
        slug, err = circles.form(self.char1, "redbird")  # name is free again
        self.assertIsNone(err)

    def test_signal_intercepted_only_above_safe_visibility(self):
        from unittest.mock import patch

        from world import circles, tuning

        self._circle_of_two()
        # From a dead zone: even a doomed roll cannot intercept.
        self.char1.db.exposure = 0
        with patch("world.circles.random.random", return_value=0.0):
            intercepted = circles.send_signal(self.char1, "lie low")
        self.assertFalse(intercepted)
        self.assertEqual(self.char1.db.exposure, 0)
        # From the plaza: the wall has a wire in it.
        self.room1.db.visibility = 4
        with patch("world.circles.random.random", return_value=0.0):
            intercepted = circles.send_signal(self.char1, "meet at the usual")
        self.assertTrue(intercepted)
        self.assertEqual(
            self.char1.db.exposure, tuning.SIGNAL_INTERCEPT_EXPOSURE
        )
        self.assertTrue(
            any("coded signals" in c for c in self._file_contents(self.char1))
        )

    # --- Section C ----------------------------------------------------------

    def test_confess_names_betrays_the_cell(self):
        from world import circles, tuning, watch

        self._holding_cell()
        slug = self._circle_of_two()
        self.char1.db.exposure = 60
        self.char2.db.exposure = 0
        watch.detain(self.char1)
        # Bare confess only shows the form; you are still detained.
        self.char1.execute_cmd("confess")
        self.assertTrue(watch.is_detained(self.char1))
        # Completing Section C releases you and burns everyone else.
        self.char1.execute_cmd("confess names")
        self.assertFalse(watch.is_detained(self.char1))
        self.assertIsNone(circles.circle_of(self.char1))
        self.assertEqual(self.char2.db.exposure, tuning.CELL_NAMED_EXPOSURE)
        self.assertTrue(
            any(
                "Named as an associate" in c
                for c in self._file_contents(self.char2)
            )
        )
        self.assertTrue(
            any("Section C complete" in c for c in self._file_contents(self.char1))
        )

    def test_confess_alone_costs_the_confessor_only(self):
        from world import circles, tuning, watch

        self._holding_cell()
        self._circle_of_two()
        self.char1.db.exposure = 60
        self.char2.db.exposure = 0
        watch.detain(self.char1)
        self.char1.execute_cmd("confess alone")
        self.assertFalse(watch.is_detained(self.char1))
        # Loyalty keeps the cell intact and the comrade's file clean...
        self.assertEqual(circles.circle_of(self.char1), "redbird")
        self.assertEqual(self.char2.db.exposure, 0)
        # ...and leaves *you* on a shorter leash.
        self.assertEqual(
            self.char1.db.exposure, tuning.RELEASE_EXPOSURE_UNCOOPERATIVE
        )
        self.assertTrue(
            any("Section C" in c for c in self._file_contents(self.char1))
        )

    # --- reputation (ADR 0010) ------------------------------------------------

    def test_judge_reads_a_citizens_completed_section_c_at_skill(self):
        from world import tuning, watch

        self._holding_cell()
        self._circle_of_two()
        self.char1.db.exposure = 60
        watch.detain(self.char1)
        self.char1.execute_cmd("confess names")

        self.char2.db.skills = {"observation": tuning.OBSERVE_TIER_REPUTATION - 1}
        blob = self._captured(self.char2, "judge Char")
        self.assertIn("learned nothing", blob)

        self.char2.db.skills = {"observation": tuning.OBSERVE_TIER_REPUTATION}
        blob = self._captured(self.char2, "judge Char")
        self.assertIn("Section C, completed", blob)

    def test_judge_reads_a_citizens_clean_section_c(self):
        from world import tuning, watch

        self._holding_cell()
        self._circle_of_two()
        self.char1.db.exposure = 60
        watch.detain(self.char1)
        self.char1.execute_cmd("confess alone")

        self.char2.db.skills = {"observation": tuning.OBSERVE_TIER_REPUTATION}
        blob = self._captured(self.char2, "judge Char")
        self.assertIn("kept faith", blob)

    def test_judge_cannot_distinguish_no_record_from_a_redacted_one(self):
        from world import tuning

        # Never confessed: unreadable, same as an unreadable informant --
        # the underground can't prove a negative any better than the
        # Ministry can.
        self.char1.db.skills = {"observation": tuning.OBSERVE_TIER_REPUTATION}
        blob = self._captured(self.char1, "judge Char2")
        self.assertIn("isn't in", blob)
        self.assertNotIn("Section C", blob)

    # --- informants ---------------------------------------------------------

    def _informant(self, loyalty):
        npc = create.create_object(
            "typeclasses.npcs.Informant",
            key="the tea vendor",
            location=self.room1,
        )
        npc.db.loyalty = loyalty
        return npc

    def test_recruit_needs_cell_and_quiet(self):
        from world import circles, tuning

        npc = self._informant("street")
        self.char1.execute_cmd("recruit tea vendor")
        self.assertIsNone(npc.db.recruited_by)  # no cell yet
        slug = self._circle_of_two()
        self.room1.db.visibility = tuning.RECRUIT_MAX_VISIBILITY + 1
        self.char1.execute_cmd("recruit tea vendor")
        self.assertIsNone(npc.db.recruited_by)  # too bright here
        self.room1.db.visibility = tuning.RECRUIT_MAX_VISIBILITY
        self.char1.execute_cmd("recruit tea vendor")
        self.assertEqual(npc.db.recruited_by, slug)

    def test_ministry_plant_files_on_the_cell(self):
        from world import circles, tuning

        slug = self._circle_of_two()
        npc = self._informant("ministry")
        npc.db.recruited_by = slug
        npc.db.last_report = 0
        circles.collect_informant_reports()
        reported = [
            c
            for member in (self.char1, self.char2)
            for c in self._file_contents(member)
            if "Reported by a source" in c
        ]
        self.assertEqual(len(reported), 1)
        # Cooldown: an immediate second collection files nothing new.
        circles.collect_informant_reports()
        reported = [
            c
            for member in (self.char1, self.char2)
            for c in self._file_contents(member)
            if "Reported by a source" in c
        ]
        self.assertEqual(len(reported), 1)

    def test_ministry_plant_report_names_the_project_room_not_a_member(self):
        # ADR 0015: an active project's last qualifying act gives the
        # report a room to reference -- an act, not an actor, so it can't
        # single out char1 or char2 by name.
        from world import circle_projects, circles

        slug = self._circle_of_two()
        circle_projects.start(self.char1)
        reg = circle_projects._registry()
        reg[slug]["last_event_room"] = "Tunnel B"
        circle_projects._save_registry(reg)
        npc = self._informant("ministry")
        npc.db.recruited_by = slug
        npc.db.last_report = 0
        circles.collect_informant_reports()
        reported = [
            c
            for member in (self.char1, self.char2)
            for c in self._file_contents(member)
            if "Reported by a source" in c
        ]
        self.assertEqual(len(reported), 1)
        self.assertIn("Tunnel B", reported[0])
        self.assertNotIn(self.char1.key, reported[0])
        self.assertNotIn(self.char2.key, reported[0])

    def test_ministry_plant_report_is_generic_without_a_project(self):
        from world import circles

        slug = self._circle_of_two()
        npc = self._informant("ministry")
        npc.db.recruited_by = slug
        npc.db.last_report = 0
        circles.collect_informant_reports()
        reported = [
            c
            for member in (self.char1, self.char2)
            for c in self._file_contents(member)
            if "Reported by a source" in c
        ]
        self.assertEqual(len(reported), 1)
        self.assertEqual(
            reported[0],
            "Reported by a source: associates with an unregistered circle",
        )

    def test_judge_reads_truth_only_at_skill(self):
        from world import tuning

        self._informant("ministry")
        self.char1.db.skills = {"observation": 0}
        blob = self._captured(self.char1, "judge tea vendor")
        self.assertIn("learned nothing", blob)
        self.char1.db.skills = {"observation": tuning.OBSERVE_TIER_DETAIL}
        blob = self._captured(self.char1, "judge tea vendor")
        self.assertIn("Ministry", blob)

    def test_flip_buys_a_plant_and_only_a_plant(self):
        from world import tuning

        npc = self._informant("ministry")
        self.char1.db.skills = {"observation": tuning.OBSERVE_TIER_DETAIL}
        self.char1.db.credits = 0
        self.char1.execute_cmd("flip tea vendor")
        self.assertEqual(npc.db.loyalty, "ministry")  # can't afford it
        self.char1.db.credits = tuning.FLIP_COST
        self.char1.execute_cmd("flip tea vendor")
        self.assertEqual(npc.db.loyalty, "street")
        self.assertEqual(self.char1.db.credits, 0)

    # --- assemblies ---------------------------------------------------------

    def _assembly(self):
        from typeclasses.scripts import AssemblyScript

        self.room2.tags.add("assembly_point", category="grid")
        script = create.create_script(AssemblyScript)
        return script

    def test_absence_is_data(self):
        from world import tuning

        script = self._assembly()
        script.db.announced = True  # skip straight to roll call
        self.char1.db.exposure = 0
        script.at_repeat()
        self.assertEqual(self.char1.db.exposure, tuning.ASSEMBLY_ABSENT_EXPOSURE)
        self.assertTrue(
            any(
                "Absent from mandatory civic assembly" in c
                for c in self._file_contents(self.char1)
            )
        )
        script.stop()

    def test_attendance_is_the_cheapest_virtue(self):
        from world import records, tuning

        script = self._assembly()
        script.db.announced = True
        self.char1.move_to(self.room2)
        start = self.char1.db.exposure or 0
        script.at_repeat()
        self.assertEqual(
            self.char1.db.exposure,
            max(0, start - tuning.ASSEMBLY_ATTEND_RELIEF),
        )
        observations = [
            r.db.content
            for r in records.records_for(self.char1, kind="observation")
        ]
        self.assertIn("Attended civic assembly", observations)
        script.stop()

    def test_detained_are_excused_from_assembly(self):
        from world import watch

        self._holding_cell()
        script = self._assembly()
        self.char1.db.exposure = 60
        watch.detain(self.char1)
        files_before = len(self._file_contents(self.char1))
        script.db.announced = True
        script.at_repeat()
        self.assertEqual(len(self._file_contents(self.char1)), files_before)
        script.stop()
        watch.release(self.char1)

    def test_absence_cap_stops_the_incident_flood(self):
        """The idler-farming fix (known risk since v0.12; round-two
        playtest found it still compounding — 35 duplicate incidents in
        one dossier). Consecutive unexcused absences stop generating
        incidents past the cap."""
        script = self._assembly()
        self.char1.db.exposure = 0
        for _ in range(tuning.ASSEMBLY_ABSENCE_CAP + 3):
            script.db.announced = True
            script.at_repeat()
        incidents = [
            c
            for c in self._file_contents(self.char1)
            if "Absent from mandatory civic assembly" in c
        ]
        self.assertEqual(len(incidents), tuning.ASSEMBLY_ABSENCE_CAP)
        script.stop()

    def test_inactive_session_is_excused_not_absent(self):
        """A citizen whose session has gone quiet longer than the active
        window can't be faulted for missing a roll it never really
        reached."""
        import time

        script = self._assembly()
        session = self.char1.sessions.all()[0]
        session.cmd_last = time.time() - tuning.ASSEMBLY_ACTIVE_WINDOW - 10
        script.db.announced = True
        script.at_repeat()
        self.assertFalse(
            any(
                "Absent from mandatory civic assembly" in c
                for c in self._file_contents(self.char1)
            )
        )
        script.stop()

    def test_registered_after_announcement_is_excused(self):
        """A citizen who signed up after the loudspeakers spoke never
        heard them."""
        import time

        script = self._assembly()
        script.db.announced = True
        script.db.announced_at = time.time() - 1000  # long before setUp
        script.at_repeat()
        self.assertFalse(
            any(
                "Absent from mandatory civic assembly" in c
                for c in self._file_contents(self.char1)
            )
        )
        script.stop()

    # --- the honeypot -------------------------------------------------------

    def _honeypot(self):
        """A room that reads Vis 0 and is lying about it."""
        self.room2.db.visibility = 0
        seam = create.create_object(
            "typeclasses.objects.Sensor", key="a seam", location=self.room2
        )
        seam.db.sensitivity = 1
        seam.db.active = True
        seam.db.concealment = 9
        return seam

    def test_honeypot_is_not_a_dead_zone(self):
        self._honeypot()
        self.assertFalse(self.room2.is_dead_zone())
        self.room1.db.visibility = 0
        self.assertTrue(self.room1.is_dead_zone())

    def test_forge_refuses_in_the_honeypot(self):
        from world import records, watch

        self._honeypot()
        watch.add_record_note(self.char1, "DETAINED: test")
        self.char1.move_to(self.room2)
        self.char1.execute_cmd("forge 1 = Commended for vigilance")
        self.assertEqual(
            records.incident_by_number(self.char1, 1).db.content,
            "DETAINED: test",
        )

    def test_sweep_reaches_past_the_chalk_mark(self):
        from unittest.mock import patch

        from typeclasses.scripts import WatchSweepScript
        from world import watch

        self._holding_cell()
        self._honeypot()
        script = create.create_script(WatchSweepScript)
        self.char1.move_to(self.room2)
        self.char1.db.exposure = 90
        with patch("random.random", return_value=0.0):
            script.at_repeat()
        self.assertTrue(watch.is_detained(self.char1))
        script.stop()
        watch.release(self.char1)

    def test_observe_reveals_concealed_only_when_the_check_is_won(self):
        from unittest.mock import patch

        from world import tuning

        self._honeypot()
        self.char1.move_to(self.room2)
        # High enough for the (untouched) detail tier to print per-device
        # info -- isolates the concealment gate ADR 0019 actually changed.
        self.char1.db.skills = {"observation": tuning.OBSERVE_TIER_STATUS}
        with patch("world.checks.opposed_check", return_value=False):
            blob = self._captured(self.char1, "observe")
        self.assertIn("no fixed devices", blob)
        with patch("world.checks.opposed_check", return_value=True):
            blob = self._captured(self.char1, "observe")
        self.assertIn("concealed", blob)


class TestLegibility(EvenniaTest):
    """v0.7: the first human playtest's fixes, verified."""

    def test_prompt_spells_out_exposure(self):
        prompt = self.char1.get_prompt()
        self.assertIn("Exposure:", prompt)
        self.assertNotIn("Exp:", prompt.replace("Exposure:", ""))

    def test_prompt_spells_out_visibility(self):
        prompt = self.char1.get_prompt()
        self.assertIn("Visibility:", prompt)
        self.assertNotIn("Vis:", prompt)

    def test_prompt_colors_exposure_by_watch_threshold(self):
        self.char1.db.exposure = 0
        self.assertIn("|g0|n", self.char1.get_prompt())
        self.char1.db.exposure = tuning.SWEEP_MIN_EXPOSURE
        self.assertIn(f"|y{tuning.SWEEP_MIN_EXPOSURE}|n", self.char1.get_prompt())
        self.char1.db.exposure = tuning.DETAIN_THRESHOLD
        self.assertIn(f"|r{tuning.DETAIN_THRESHOLD}|n", self.char1.get_prompt())

    def test_prompt_shows_exposure_trend(self):
        self.char1.db.exposure = 10
        self.char1.get_prompt()  # establishes the baseline to compare against
        steady = self.char1.get_prompt()
        self.assertNotIn("|r^|n", steady)
        self.assertNotIn("|gv|n", steady)
        self.char1.db.exposure = 15
        self.assertIn("|r^|n", self.char1.get_prompt())
        self.char1.db.exposure = 5
        self.assertIn("|gv|n", self.char1.get_prompt())

    def test_prompt_flags_live_visibility_above_the_static_digit(self):
        self.room1.db.visibility = 3
        quiet = self.char1.get_prompt()
        self.assertNotIn("(+", quiet)
        sensor = create.create_object(
            "typeclasses.objects.Sensor", key="a scanner", location=self.room1
        )
        sensor.db.sensitivity = 2
        loud = self.char1.get_prompt()
        self.assertIn("|=m(|n+2|=m)|n", loud)

    def test_the_prefixed_keys_get_no_article(self):
        chalk = create.create_object(
            "typeclasses.objects.Object", key="the chalk marks",
            location=self.room1,
        )
        name = chalk.get_numbered_name(1, self.char1, return_string=True)
        self.assertEqual(str(name), "the chalk marks")

    def test_npc_display_name_capitalized(self):
        clerk = create.create_object(
            "typeclasses.npcs.Citizen", key="the ration clerk",
            location=self.room1,
        )
        self.assertEqual(clerk.get_display_name(self.char1), "The ration clerk")
        self.assertEqual(clerk.key, "the ration clerk")  # key untouched

    def test_help_available_while_detained(self):
        from commands.detention import DetainedCmdSet

        cmdset = DetainedCmdSet()
        cmdset.at_cmdset_creation()
        keys = {cmd.key for cmd in cmdset.commands}
        self.assertIn("help", keys)

    def test_score_reaches_the_dossier(self):
        old = self.char1.msg
        seen = []
        self.char1.msg = lambda text=None, **kw: seen.append(str(text))
        try:
            self.char1.execute_cmd("score")
        finally:
            self.char1.msg = old
        self.assertIn("CITIZEN FILE", "\n".join(seen))

    def test_help_entries_well_formed(self):
        from world.help_entries import HELP_ENTRY_DICTS

        keys = {entry["key"] for entry in HELP_ENTRY_DICTS}
        self.assertIn("exposure", keys)
        self.assertIn("visibility", keys)
        for entry in HELP_ENTRY_DICTS:
            self.assertTrue(entry["text"].strip())


class TestRoomSpacing(EvenniaTest):
    """
    The room description gets its own paragraph; Exits/Characters/You-see
    stay tight together as one scannable block. The whole display is
    wrapped in a blank line on each side, so a room's own look reads as
    its own paragraph next to whatever ambient text or movement message
    lands beside it in the scrolling log.
    """

    def test_blank_line_separates_desc_from_the_grid_block(self):
        appearance = self.room1.return_appearance(self.char1)
        self.assertIn("room_desc\n\n|wExits:", appearance)

    def test_exits_characters_and_things_stay_tight(self):
        appearance = self.room1.return_appearance(self.char1)
        self.assertIn("out\n|wCharacters:", appearance)
        self.assertIn("Char2\n|wYou see:", appearance)
        self.assertNotIn("out\n\n|wCharacters:", appearance)
        self.assertNotIn("Char2\n\n|wYou see:", appearance)

    def test_whole_display_wrapped_in_a_single_blank_line(self):
        appearance = self.room1.return_appearance(self.char1)
        self.assertTrue(appearance.startswith("\n") and not appearance.startswith("\n\n"))
        self.assertTrue(appearance.endswith("\n") and not appearance.endswith("\n\n"))

    def test_no_stray_blank_line_when_a_block_is_missing(self):
        bare = create.create_object(self.room_typeclass, key="Bare Room", nohome=True)
        bare.db.desc = "bare_desc"
        self.char1.move_to(bare, quiet=True, move_type="teleport")
        self.char2.move_to(bare, quiet=True, move_type="teleport")

        appearance = bare.return_appearance(self.char1)

        self.assertNotIn("\n\n\n", appearance)
        self.assertIn("bare_desc\n\n|wCharacters:", appearance)


class TestOnboarding(EvenniaTest):
    """v0.15: the Wing teaches by making you do the verb."""

    def setUp(self):
        super().setUp()
        self.room1.tags.add("workplace", category="grid")

    def _sent(self, cmd_string):
        seen = []
        old = self.char1.msg
        self.char1.msg = lambda text=None, **kw: seen.append(str(text))
        try:
            self.char1.execute_cmd(cmd_string)
        finally:
            self.char1.msg = old
        return "\n".join(seen)

    def test_map_acknowledges_first_use_once(self):
        first = self._sent("map")
        self.assertIn("The sector unfolds", first)
        second = self._sent("map")
        self.assertNotIn("The sector unfolds", second)

    def test_observe_acknowledges_first_use_once(self):
        first = self._sent("observe")
        self.assertIn("noticing you", first)
        second = self._sent("observe")
        self.assertNotIn("noticing you", second)

    def test_dossier_acknowledges_first_use_once(self):
        first = self._sent("dossier")
        self.assertIn("on request, as promised", first)
        second = self._sent("dossier")
        self.assertNotIn("on request, as promised", second)

    def test_grade_acknowledges_first_use_once(self):
        first = self._sent("grade")
        self.assertIn("standing in for a citizen", first)
        second = self._sent("grade")
        self.assertNotIn("standing in for a citizen", second)

    def test_report_acknowledges_first_use_once(self):
        first = self._sent("report")
        self.assertIn("The first stamp", first)
        second = self._sent("report")
        self.assertNotIn("The first stamp", second)

    def test_work_acknowledges_first_use(self):
        first = self._sent("work")
        self.assertIn("Visible usefulness, logged", first)

    def test_errands_take_acknowledges_first_use(self):
        create.create_object(
            "typeclasses.npcs.Citizen", key="the orientation clerk",
            location=self.room1,
        ).tags.add("errand_giver", category="grid")
        first = self._sent("errands take rounds")
        self.assertIn("Work found you", first)

    def _archivist(self):
        archivist = create.create_object(
            "typeclasses.npcs.Citizen", key="the archivist", location=self.room1
        )
        archivist.tags.add("records_service", category="grid")
        return archivist

    def test_listen_acknowledges_first_use(self):
        self.room1.tags.add("gossip_spot", category="grid")
        from world import records

        records.add_record(self.char2, "Papers checked in the street; cleared.")
        first = self._sent("listen")
        self.assertIn("says more than it means to", first)

    def test_petition_acknowledges_first_use(self):
        from world import records, tuning

        self._archivist()
        rec = records.add_record(self.char1, "A minor infraction.")
        self.char1.db.credits = tuning.REDACT_COST
        first = self._sent(f"petition redact {rec.db.number}")
        self.assertIn("sanctioned route", first)

    def test_research_acknowledges_first_use(self):
        self._archivist()
        first = self._sent("research")
        self.assertIn("exactly as dull as it looks", first)

    def test_apply_acknowledges_first_use(self):
        self._archivist()
        first = self._sent("apply")
        self.assertIn("only the versions of them it has", first)

    def test_vouch_and_unvouch_acknowledge_first_use(self):
        from world import tuning

        self.char1.db.credits = tuning.VOUCH_STAKE
        first = self._sent(f"vouch {self.char2.key}")
        self.assertIn("character reference, quietly filed", first)
        second = self._sent("unvouch")
        self.assertIn("taken back, whatever you staked returned in full", second)

    def test_list_and_buy_acknowledge_first_use(self):
        vendor = create.create_object(
            "typeclasses.npcs.Citizen", key="the requisitions clerk",
            location=self.room1,
        )
        vendor.tags.add("vendor", category="grid")
        vendor.db.stock = ["badge"]
        first = self._sent("list")
        self.assertIn("what's for sale", first.lower())
        self.char1.db.credits = 10
        second = self._sent("buy badge")
        self.assertIn("want-ladder has a first rung", second)

    def test_wear_acknowledges_first_use(self):
        item = create.create_object(
            "typeclasses.gear.Gear", key="test badge", location=self.char1
        )
        item.db.gear_kind = "badge"
        item.db.slot = "wrist"
        first = self._sent("wear test badge")
        self.assertIn("one item per place it's worn", first.lower())

    def test_next_gives_wing_specific_hint_inside_the_wing(self):
        self.room1.tags.add("wing_watched", category="grid")
        advice = self._sent("next")
        self.assertIn("observe", advice)

    def test_next_falls_back_to_generic_advice_outside_the_wing(self):
        advice = self._sent("next")
        self.assertIn("five rooms long", advice)


class TestCircleBenefits(EvenniaTest):
    """v0.11: the pay side of trust — the stash and joint work."""

    def _circle(self, name="redbird"):
        from world import circles

        slug, err = circles.form(self.char1, name)
        self.assertIsNone(err)
        self.char2.tags.add(slug, category="circle")
        return slug

    def test_stash_establishes_in_dead_zones_only(self):
        from world import circles

        slug = self._circle()
        thing = create.create_object(
            "typeclasses.objects.Object", key="a tin of tea",
            location=self.char1,
        )
        self.room1.db.visibility = 3
        self.char1.execute_cmd(f"stash {thing.key}")
        self.assertIsNone(circles.cache_of(slug))
        self.room1.db.visibility = 0
        self.char1.execute_cmd(f"stash {thing.key}")
        cache = circles.cache_of(slug)
        self.assertIsNotNone(cache)
        self.assertIn(thing, cache.contents)
        # Invisible to everyone: knowing where it is IS the membership.
        self.assertFalse(cache.access(self.char2, "view"))

    def test_stash_take_is_in_person(self):
        from world import circles

        self._circle()
        thing = create.create_object(
            "typeclasses.objects.Object", key="a tin of tea",
            location=self.char1,
        )
        self.char1.execute_cmd(f"stash {thing.key}")
        self.char1.move_to(self.room2)
        self.char1.execute_cmd(f"stash take {thing.key}")
        self.assertNotIn(thing, self.char1.contents)  # wrong room
        self.char1.move_to(self.room1)
        self.char1.execute_cmd(f"stash take {thing.key}")
        self.assertIn(thing, self.char1.contents)

    def test_betrayal_confiscates_the_cache(self):
        from world import circles, watch

        holding = create.create_object(
            "typeclasses.rooms.Room", key="Holding Cell (test)"
        )
        holding.tags.add("holding_cell", category="grid")
        self.room1.tags.add("release_point", category="grid")
        slug = self._circle()
        thing = create.create_object(
            "typeclasses.objects.Object", key="a tin of tea",
            location=self.char1,
        )
        self.char1.execute_cmd(f"stash {thing.key}")
        self.char1.db.exposure = 60
        watch.detain(self.char1)
        self.char1.execute_cmd("confess names")
        self.assertIsNone(circles.cache_of(slug))
        self.assertIsNone(thing.pk)  # the Ministry keeps it now

    def test_last_member_out_spills_the_cache(self):
        from world import circles

        slug = self._circle()
        thing = create.create_object(
            "typeclasses.objects.Object", key="a tin of tea",
            location=self.char1,
        )
        self.char1.execute_cmd(f"stash {thing.key}")
        self.char2.tags.remove(slug, category="circle")
        circles.leave(self.char1)
        self.assertIsNone(circles.cache_of(slug))
        self.assertEqual(thing.location, self.room1)  # spilled where it was

    def test_four_hands_needs_both_pairs(self):
        from world import errands

        self._circle()
        giver = create.create_object(
            "typeclasses.npcs.Citizen", key="the lamp-mender",
            location=self.room1,
        )
        giver.tags.add("errand_giver", category="grid")
        self.char1.db.errands_done = ["look-closer", "legs"]
        self.char1.execute_cmd("errands take four-hands")
        self.room2.key = "Tunnel B"
        self.char2.move_to(self.room1)  # mate elsewhere first
        self.char1.move_to(self.room2)
        self.assertIsNotNone(errands.current(self.char1))  # alone: no
        self.char2.move_to(self.room2)  # the other pair of hands arrives
        self.assertIsNone(errands.current(self.char1))


class TestCircleProjects(EvenniaTest):
    """ADR 0013: a joint pot that only pays out whole."""

    def _circle(self, name="redbird"):
        from world import circles

        slug, err = circles.form(self.char1, name)
        self.assertIsNone(err)
        self.char2.tags.add(slug, category="circle")
        return slug

    def _sensor(self, room=None):
        sensor = create.create_object(
            "typeclasses.objects.Sensor", key="a lens", location=room or self.room1,
        )
        sensor.db.sensitivity = 1
        sensor.db.active = True
        return sensor

    def _broker(self):
        broker = create.create_object(
            "typeclasses.npcs.Citizen", key="the broker", location=self.room1
        )
        broker.tags.add("courier_broker", category="grid")
        return broker

    def test_start_requires_a_circle(self):
        from world import circle_projects

        err = circle_projects.start(self.char1)
        self.assertIsNotNone(err)

    def test_only_one_project_at_a_time(self):
        from world import circle_projects

        slug = self._circle()
        self.assertIsNone(circle_projects.start(self.char1))
        err = circle_projects.start(self.char2)
        self.assertIsNotNone(err)
        self.assertEqual(circle_projects.project_of(slug)["stage"], 0)

    def test_casing_tally_is_shared_across_members(self):
        from unittest.mock import patch

        from world import circle_projects, tuning

        slug = self._circle()
        circle_projects.start(self.char1)
        self.room1.db.visibility = 0
        for _ in range(tuning.PROJECT_CASING_THRESHOLD - 1):
            sensor = self._sensor()
            with patch("world.checks.opposed_check", return_value=True):
                self.char1.execute_cmd("sabotage lens")
        self.assertEqual(circle_projects.project_of(slug)["stage"], 0)
        sensor = self._sensor()
        with patch("world.checks.opposed_check", return_value=True):
            self.char2.execute_cmd("sabotage lens")  # a different member finishes it
        self.assertEqual(circle_projects.project_of(slug)["stage"], 1)  # advanced to the Run

    def test_casing_records_the_last_event_room(self):
        # ADR 0015: the room of the most recent qualifying act, not the
        # actor -- kept for informant reports to reference.
        from unittest.mock import patch

        from world import circle_projects

        slug = self._circle()
        circle_projects.start(self.char1)
        self.room1.db.visibility = 0
        self.room1.key = "Tunnel B"
        sensor = self._sensor()
        with patch("world.checks.opposed_check", return_value=True):
            self.char1.execute_cmd("sabotage lens")
        self.assertEqual(
            circle_projects.project_of(slug)["last_event_room"], "Tunnel B"
        )

    def test_run_tally_advances_to_the_split(self):
        from unittest.mock import patch

        from world import circle_projects, tuning, underground

        slug = self._circle()
        reg = circle_projects._registry()
        reg[slug] = {"stage": 1, "progress": 0, "started": 0}
        circle_projects._save_registry(reg)
        self._broker()
        dest_key, _, _ = tuning.COURIER_JOBS["quiet"]
        self.room2.key = dest_key
        for member in (self.char1, self.char2):
            member.execute_cmd("carry quiet")
            member.move_to(self.room2)
            with patch("world.underground.random.random", return_value=0.99):
                underground.deliver(member)
        self.assertEqual(circle_projects.project_of(slug)["stage"], 2)

    def test_split_needs_two_members_in_a_dead_zone_at_once(self):
        from world import circle_projects

        slug = self._circle()
        reg = circle_projects._registry()
        reg[slug] = {"stage": 2, "progress": 0, "started": 0}
        circle_projects._save_registry(reg)
        self.room2.key = "Tunnel B"
        self.room2.db.visibility = 0
        # char2 stays put in room1 (its default starting location, apart
        # from char1) until the reunion below — moving it there explicitly
        # first would falsely reunite the pair in room1, itself a dead zone.
        self.char1.move_to(self.room2)
        self.assertIsNotNone(circle_projects.project_of(slug))  # alone: no
        self.char2.move_to(self.room2)  # the other pair of hands arrives
        self.assertIsNone(circle_projects.project_of(slug))

    def test_split_payout_splits_evenly(self):
        from world import circle_projects, tuning

        slug = self._circle()
        reg = circle_projects._registry()
        reg[slug] = {"stage": 2, "progress": 0, "started": 0}
        circle_projects._save_registry(reg)
        self.room2.key = "Tunnel B"
        self.room2.db.visibility = 0
        self.char1.move_to(self.room2)
        self.char2.move_to(self.room2)
        share = tuning.PROJECT_PAYOUT // 2
        for member in (self.char1, self.char2):
            self.assertEqual(
                (member.db.standing or {}).get(tuning.UNDERGROUND), share
            )
            self.assertEqual(member.db.credits, share)

    def test_completed_confession_forfeits_the_project(self):
        from world import circle_projects, watch

        holding = create.create_object(
            "typeclasses.rooms.Room", key="Holding Cell (test)"
        )
        holding.tags.add("holding_cell", category="grid")
        self.room1.tags.add("release_point", category="grid")
        slug = self._circle()
        circle_projects.start(self.char1)
        self.char1.db.exposure = 60
        watch.detain(self.char1)
        self.char1.execute_cmd("confess names")
        self.assertIsNone(circle_projects.project_of(slug))

    def test_leaving_does_not_forfeit_the_project(self):
        from world import circle_projects, circles

        slug = self._circle()
        circle_projects.start(self.char1)
        circles.leave(self.char2)
        self.assertIsNotNone(circle_projects.project_of(slug))


class TestVouching(EvenniaTest):
    """ADR 0014: a small, sanctioned stake on someone else's name."""

    def _fund(self, char, amount):
        char.gain_credits(amount)

    def test_vouch_costs_the_stake_and_is_one_at_a_time(self):
        from world import tuning, vouching

        self._fund(self.char1, tuning.VOUCH_STAKE)
        self.char1.execute_cmd("vouch Char2")
        self.assertEqual(self.char1.db.credits, 0)
        self.assertEqual(vouching.current(self.char1)["target"], self.char2)
        self.assertIn(self.char1, vouching.backers_of(self.char2))
        # Already vouching for someone: refused, no second stake taken.
        self._fund(self.char1, tuning.VOUCH_STAKE)
        self.char1.execute_cmd("vouch Char2")
        self.assertEqual(self.char1.db.credits, tuning.VOUCH_STAKE)

    def test_vouch_with_standing_takes_nothing_up_front(self):
        from world import tuning, vouching

        self.char1.db.standing = {"Ministry of Records": tuning.VOUCH_STAKE}
        self.char1.execute_cmd("vouch Char2 with standing")
        self.assertEqual(
            (self.char1.db.standing or {}).get("Ministry of Records"),
            tuning.VOUCH_STAKE,
        )
        self.assertEqual(vouching.current(self.char1)["resource"], "standing")
        self.assertEqual(vouching.current(self.char1)["target"], self.char2)

    def test_vouch_refuses_without_credits(self):
        from world import vouching

        self.char1.execute_cmd("vouch Char2")
        self.assertIsNone(vouching.current(self.char1))

    def test_cannot_vouch_for_yourself(self):
        from world import tuning, vouching

        self._fund(self.char1, tuning.VOUCH_STAKE)
        err = vouching.vouch(self.char1, self.char1, "credits")
        self.assertIsNotNone(err)
        self.assertIsNone(vouching.current(self.char1))

    def test_unvouch_returns_the_credits_stake_in_full(self):
        from world import tuning, vouching

        self._fund(self.char1, tuning.VOUCH_STAKE)
        self.char1.execute_cmd("vouch Char2")
        self.char1.execute_cmd("unvouch")
        self.assertIsNone(vouching.current(self.char1))
        self.assertNotIn(self.char1, vouching.backers_of(self.char2))
        self.assertEqual(self.char1.db.credits, tuning.VOUCH_STAKE)

    def test_unvouch_standing_stake_is_a_no_op_on_the_ledger(self):
        from world import tuning, vouching

        self.char1.execute_cmd("vouch Char2 with standing")
        self.char1.execute_cmd("unvouch")
        self.assertIsNone(vouching.current(self.char1))
        self.assertNotIn(self.char1, vouching.backers_of(self.char2))
        self.assertEqual((self.char1.db.standing or {}).get("Ministry of Records"), 0)

    def test_confess_alone_does_not_forfeit_backers(self):
        from world import circles, tuning, vouching, watch

        # confess names/alone only exist as real choices for a confessor
        # who has a circle at all (CmdConfess's "no associates" branch
        # short-circuits straight to release otherwise), and detain() only
        # works on a citizen with a live session -- EvenniaTest only logs
        # in char1's account, so char1 has to be the confessor here, with
        # char2 as the backer.
        cell = create.create_object(
            "typeclasses.rooms.Room", key="Holding Cell (test)"
        )
        cell.tags.add("holding_cell", category="grid")
        self.room1.tags.add("release_point", category="grid")
        slug, err = circles.form(self.char1, "redbird")
        self.assertIsNone(err)
        self._fund(self.char2, tuning.VOUCH_STAKE)
        self.char2.execute_cmd("vouch Char")
        self.assertIsNotNone(vouching.current(self.char2))
        self.char1.db.exposure = 60
        watch.detain(self.char1)
        self.char1.execute_cmd("confess alone")
        self.assertFalse(watch.is_detained(self.char1))  # confirms it ran
        self.assertIsNotNone(vouching.current(self.char2))

    def test_confess_names_forfeits_backers(self):
        from world import circles, tuning, vouching, watch

        cell = create.create_object(
            "typeclasses.rooms.Room", key="Holding Cell (test)"
        )
        cell.tags.add("holding_cell", category="grid")
        self.room1.tags.add("release_point", category="grid")
        slug, err = circles.form(self.char1, "redbird")
        self.assertIsNone(err)
        self._fund(self.char2, tuning.VOUCH_STAKE)
        self.char2.execute_cmd("vouch Char")
        self.char1.db.exposure = 60
        watch.detain(self.char1)
        self.char1.execute_cmd("confess names")
        self.assertFalse(watch.is_detained(self.char1))  # confirms it ran
        self.assertIsNone(vouching.current(self.char2))
        self.assertEqual(vouching.backers_of(self.char1), [])

    def test_confess_names_forfeits_a_standing_stake_and_can_demote_grade(self):
        from world import circles, grades, tuning, watch

        self.assertGreater(tuning.GRADE_THRESHOLDS[5], tuning.VOUCH_STAKE)
        cell = create.create_object(
            "typeclasses.rooms.Room", key="Holding Cell (test)"
        )
        cell.tags.add("holding_cell", category="grid")
        self.room1.tags.add("release_point", category="grid")
        slug, err = circles.form(self.char1, "redbird")
        self.assertIsNone(err)
        # Just enough standing to hold Grade 5.
        self.char2.db.standing = {"Ministry of Records": tuning.GRADE_THRESHOLDS[5]}
        grades.check_reclassification(self.char2)
        self.assertEqual(grades.grade_of(self.char2), 5)
        self.char2.execute_cmd("vouch Char with standing")
        self.char1.db.exposure = 60
        watch.detain(self.char1)
        self.char1.execute_cmd("confess names")
        remaining = tuning.GRADE_THRESHOLDS[5] - tuning.VOUCH_STAKE
        self.assertEqual(
            (self.char2.db.standing or {}).get("Ministry of Records"), remaining
        )
        # Forfeiture, unlike spending, is allowed to demote -- the standing
        # was never spent, it was staked and lost to someone else's
        # betrayal.
        self.assertEqual(grades.grade_of(self.char2), grades.GRADE_MIN)

    def test_backer_offsets_one_incident_at_form_c1(self):
        from world import functions, vouching, watch

        functions.assign_function(self.char1)
        watch.add_record_note(self.char1, "DETAINED: test")
        watch.add_record_note(self.char1, "Was unruly in detention.")
        # Two visible incidents: rejected with no backer.
        approved, reason = functions.adjudicate_c1(self.char1)
        self.assertFalse(approved)
        self.assertIn("references", reason)
        # The same file, backed: tolerated.
        self.char2.db.vouch = {
            "target": self.char1,
            "resource": "credits",
            "faction": "Ministry of Records",
            "amount": 1,
            "started": 0,
        }
        self.char1.db.vouched_by = [self.char2]
        self.assertTrue(vouching.has_backers(self.char1))
        approved, _ = functions.adjudicate_c1(self.char1)
        self.assertTrue(approved)


class TestGear(EvenniaTest):
    """v0.10: the implant catalog, worn — every item a trade."""

    def _vendor(self, stock=("badge", "cuff"), underground=None):
        vendor = create.create_object(
            "typeclasses.npcs.Citizen", key="the requisitions clerk",
            location=self.room1,
        )
        vendor.tags.add("vendor", category="grid")
        vendor.db.stock = list(stock)
        if underground:
            vendor.db.stock_underground = list(underground)
        return vendor

    def _gear(self, kind, slot="wrist", worn=True):
        item = create.create_object(
            "typeclasses.gear.Gear", key=f"test {kind}", location=self.char1
        )
        item.db.gear_kind = kind
        item.db.slot = slot
        item.db.worn = worn
        return item

    def test_buy_costs_credits_and_state_issue_is_recorded(self):
        from world import records, tuning

        self._vendor()
        self.char1.db.credits = 10
        self.char1.execute_cmd("buy badge")
        self.assertEqual(
            self.char1.db.credits, 10 - tuning.GEAR_PRICES["badge"]
        )
        self.assertTrue(
            any(
                "Issued" in r.db.content
                for r in records.records_for(self.char1, kind="observation")
            )
        )
        # No spares.
        self.char1.db.credits = 10
        self.char1.execute_cmd("buy badge")
        badges = [
            o for o in self.char1.contents if o.db.gear_kind == "badge"
        ]
        self.assertEqual(len(badges), 1)

    def test_underground_shelf_needs_standing(self):
        from world import tuning

        vendor = self._vendor(stock=(), underground=("pocket",))
        from commands.gear import _stock_for

        self.assertEqual(_stock_for(vendor, self.char1), [])
        self.char1.db.standing = {tuning.UNDERGROUND: 1}
        self.assertEqual(_stock_for(vendor, self.char1), ["pocket"])

    def test_one_item_per_slot(self):
        self._gear("badge", slot="wrist", worn=True)
        cuff = self._gear("cuff", slot="wrist", worn=False)
        self.char1.execute_cmd(f"wear {cuff.key}")
        self.assertFalse(cuff.db.worn)

    def test_badge_pays_and_burns(self):
        from world import tuning

        self._gear("badge")
        self.room1.tags.add("workplace", category="grid")
        self.char1.execute_cmd("work")
        self.assertEqual(
            (self.char1.db.standing or {}).get("Ministry of Records"),
            tuning.WORK_INFLUENCE + tuning.BADGE_WORK_BONUS,
        )
        # And it identifies you in watched rooms.
        self.room2.db.visibility = tuning.BADGE_VIS_THRESHOLD
        self.char1.db.exposure = 0
        self.char1.move_to(self.room2)
        expected = (
            tuning.VISIBILITY_EXPOSURE[tuning.BADGE_VIS_THRESHOLD]
            + tuning.BADGE_ROOM_EXPOSURE
        )
        self.assertEqual(self.char1.db.exposure, expected)

    def test_dampener_shaves_room_exposure(self):
        from world import tuning

        self._gear("dampener", slot="coat")
        self.room2.db.visibility = 4
        self.char1.db.exposure = 0
        self.char1.move_to(self.room2)
        self.assertEqual(
            self.char1.db.exposure,
            tuning.VISIBILITY_EXPOSURE[4] - tuning.DAMPENER_ROOM_RELIEF,
        )

    def test_cuff_cools_faster(self):
        from typeclasses.scripts import ExposureDecayScript
        from world import tuning

        self._gear("cuff")
        script = create.create_script(ExposureDecayScript)
        self.char1.db.exposure = 10
        script.at_repeat()
        self.assertEqual(
            self.char1.db.exposure,
            10 - tuning.EXPOSURE_DECAY_AMOUNT * tuning.CUFF_DECAY_MULT,
        )
        script.stop()

    def test_pocket_eats_exactly_one_search(self):
        from world import records, underground

        broker = create.create_object(
            "typeclasses.npcs.Citizen", key="the broker", location=self.room1
        )
        broker.tags.add("courier_broker", category="grid")
        self.char1.execute_cmd("carry quiet")
        pocket = self._gear("pocket", slot="pocket")
        # First search: eaten — cargo survives, no incident, pocket spent.
        self.assertFalse(underground.seize_contraband(self.char1))
        self.assertEqual(len(underground.carried_parcels(self.char1)), 1)
        self.assertFalse(
            any(
                "unregistered goods" in r.db.content
                for r in records.records_for(self.char1)
            )
        )
        self.assertIsNone(pocket.pk)  # spent
        # Second search: the usual afternoon.
        self.assertTrue(underground.seize_contraband(self.char1))
        self.assertEqual(len(underground.carried_parcels(self.char1)), 0)


class TestErrands(EvenniaTest):
    """v0.9: the quest system listens to verbs the player already has."""

    def _giver(self, key="the orientation clerk"):
        giver = create.create_object(
            "typeclasses.npcs.Citizen", key=key, location=self.room1
        )
        giver.tags.add("errand_giver", category="grid")
        return giver

    def test_take_requires_the_giver_present(self):
        from world import errands

        self.char1.execute_cmd("errands take rounds")
        self.assertIsNone(errands.current(self.char1))
        self._giver()
        self.char1.execute_cmd("errands take rounds")
        self.assertEqual(errands.current(self.char1)["key"], "rounds")
        # One at a time.
        self.char1.execute_cmd("errands take usefulness")
        self.assertEqual(errands.current(self.char1)["key"], "rounds")

    def test_visit_errand_progresses_and_completes(self):
        from world import errands, tuning

        self._giver()
        self.char1.execute_cmd("errands take rounds")
        spec = errands.ERRANDS["rounds"]
        for name in spec["rooms"]:
            room = create.create_object("typeclasses.rooms.Room", key=name)
            self.char1.move_to(room)
        self.assertIsNone(errands.current(self.char1))
        self.assertEqual(
            (self.char1.db.standing or {}).get("Ministry of Records"),
            tuning.ERRAND_REWARD_SMALL,
        )

    def test_shifts_errand_rides_work(self):
        from world import errands

        self.room1.tags.add("workplace", category="grid")
        self._giver()
        self.char1.db.errands_done = ["rounds"]  # chain gate
        self.char1.execute_cmd("errands take usefulness")
        for _ in range(3):
            self.char1.db.last_work = 0
            self.char1.execute_cmd("work")
        self.assertIsNone(errands.current(self.char1))

    def test_chains_gate_and_never_repeat(self):
        from world import errands

        self._giver()
        # A chained link is closed until its prerequisite is done...
        self.char1.execute_cmd("errands take usefulness")
        self.assertIsNone(errands.current(self.char1))
        # ...and a completed errand never re-opens.
        self.char1.db.errands_done = ["rounds"]
        self.assertFalse(errands.available_to(self.char1, "rounds"))
        self.assertTrue(errands.available_to(self.char1, "usefulness"))

    def test_attend_errand_rides_the_assembly(self):
        from typeclasses.scripts import AssemblyScript
        from world import errands, records

        self._giver()
        self.char1.db.errands_done = ["rounds", "usefulness"]  # chain gate
        self.char1.execute_cmd("errands take countable")
        self.room2.tags.add("assembly_point", category="grid")
        script = create.create_script(AssemblyScript)
        script.db.announced = True
        self.char1.move_to(self.room2)
        script.at_repeat()
        self.assertIsNone(errands.current(self.char1))
        observations = [
            r.db.content
            for r in records.records_for(self.char1, kind="observation")
        ]
        self.assertTrue(any("Commended" in c for c in observations))
        script.stop()

    def test_deliver_errand_rides_the_courier_board(self):
        from unittest.mock import patch

        from world import errands, tuning, underground

        self._giver("the lamp-mender")
        self.char1.db.errands_done = ["look-closer"]  # chain gate
        self.char1.execute_cmd("errands take legs")
        broker = create.create_object(
            "typeclasses.npcs.Citizen", key="the broker", location=self.room1
        )
        broker.tags.add("courier_broker", category="grid")
        self.char1.execute_cmd("carry street")
        dest_key, _, _ = tuning.COURIER_JOBS["street"]
        self.room2.key = dest_key
        self.char1.move_to(self.room2)
        with patch("world.underground.random.random", return_value=0.99):
            underground.deliver(self.char1)
        self.assertIsNone(errands.current(self.char1))
        self.assertGreater(
            (self.char1.db.standing or {}).get(tuning.UNDERGROUND, 0),
            0,
        )

    def test_drop_clears_the_errand(self):
        from world import errands

        self._giver()
        self.char1.execute_cmd("errands take rounds")
        self.char1.execute_cmd("errands drop")
        self.assertIsNone(errands.current(self.char1))


class TestJuice(EvenniaTest):
    """v0.8.5: near-misses felt, digests delivered, rooms murmuring."""

    def _captured_msgs(self, char):
        seen = []
        char.msg = lambda text=None, **kw: seen.append(str(text))
        return seen

    def test_sweep_near_miss_is_felt(self):
        from unittest.mock import patch

        from typeclasses.scripts import WatchSweepScript
        from world import tuning

        script = create.create_script(WatchSweepScript)
        self.room1.db.visibility = 3  # dead zones are skipped by design
        self.char1.db.exposure = tuning.SWEEP_MIN_EXPOSURE + 10
        old = self.char1.msg
        seen = self._captured_msgs(self.char1)
        try:
            with patch("random.random", return_value=0.999):  # always miss
                script.at_repeat()
        finally:
            self.char1.msg = old
        blob = "\n".join(seen)
        self.assertTrue(
            any(phrase in blob for phrase in ("visor", "hum", "van", "photograph")),
            f"no near-miss line in: {blob!r}",
        )
        script.stop()

    def test_login_digest_reports_new_entries(self):
        import time

        from world import records

        self.char1.db.last_on = time.time() - 60
        records.add_record(self.char1, "Absent from mandatory civic assembly")
        digest = self.char1.login_digest()
        self.assertIsNotNone(digest)
        self.assertIn("Absent from mandatory", digest)
        # Nothing new: no digest.
        self.char1.db.last_on = time.time() + 60
        self.assertIsNone(self.char1.login_digest())

    def test_ambience_murmurs_occupied_rooms(self):
        from unittest.mock import patch

        from typeclasses.scripts import AmbienceScript

        script = create.create_script(AmbienceScript)
        self.room1.db.ambience = ["The pipes knock twice, politely."]
        self.room1.db.last_ambience = 0
        old = self.char1.msg
        seen = self._captured_msgs(self.char1)
        try:
            with patch("random.random", return_value=0.0):  # always murmur
                script.at_repeat()
        finally:
            self.char1.msg = old
        self.assertTrue(any("pipes knock" in s for s in seen))
        # Cooldown: an immediate second tick stays quiet.
        seen.clear()
        old = self.char1.msg
        seen = self._captured_msgs(self.char1)
        try:
            with patch("random.random", return_value=0.0):
                script.at_repeat()
        finally:
            self.char1.msg = old
        self.assertFalse(any("pipes knock" in s for s in seen))
        script.stop()


class TestMap(EvenniaTest):
    """v0.8: the mental map — visibility digits over the room graph."""

    def _map_text(self):
        from commands.map import GridMap

        return GridMap(self.char1, size=3).show_map()

    def test_map_shows_you_and_neighbor_visibility(self):
        self.room1.db.visibility = 0
        self.room2.db.visibility = 4
        # EvenniaTest's stock exit is "out" (non-compass); give it a compass
        # exit so the mapper can walk it (ADR 0007's whole point).
        create.create_object(
            "typeclasses.exits.Exit", key="north", location=self.room1,
            destination=self.room2,
        )
        create.create_object(
            "typeclasses.exits.Exit", key="south", location=self.room2,
            destination=self.room1,
        )
        text = self._map_text()
        self.assertIn("@", text)   # you are here
        self.assertIn("4", text)   # the neighbor's visibility digit

    def test_locked_exits_hide_whats_beyond(self):
        create.create_object(
            "typeclasses.exits.Exit", key="north", location=self.room1,
            destination=self.room2,
        )
        self.room2.db.visibility = 5
        exit_obj = [e for e in self.room1.contents if e.destination][-1]
        exit_obj.locks.add("traverse:false()")
        text = self._map_text()
        self.assertNotIn("5", text)  # beyond your clearance = not anywhere

    def test_map_command_runs(self):
        old = self.char1.msg
        seen = []
        self.char1.msg = lambda text=None, **kw: seen.append(str(text))
        try:
            self.char1.execute_cmd("map")
        finally:
            self.char1.msg = old
        blob = "\n".join(seen)
        self.assertIn("Sector 9", blob)


class TestOpposedChecks(EvenniaTest):
    """ADR 0019: the shared opposed_check() helper itself."""

    def test_actor_wins_on_higher_total(self):
        from unittest.mock import patch

        from world import checks

        self.char1.db.skills = {"observation": 0}
        with patch("world.checks._roll", side_effect=[15, 10]):
            self.assertTrue(checks.opposed_check(self.char1, "observation", 3))

    def test_obstacle_wins_ties(self):
        from unittest.mock import patch

        from world import checks

        self.char1.db.skills = {"observation": 0}
        with patch("world.checks._roll", side_effect=[10, 10]):
            self.assertFalse(checks.opposed_check(self.char1, "observation", 5))

    def test_skill_raises_the_actors_total(self):
        from unittest.mock import patch

        from world import checks, tuning

        self.char1.db.skills = {"observation": tuning.CHECK_SKILL_DIVISOR * 3}
        # Actor rolls low (5) but skill contributes +3; obstacle rolls high
        # (7) with a difficulty of 0 -- skill alone should carry the win.
        with patch("world.checks._roll", side_effect=[5, 7]):
            self.assertTrue(checks.opposed_check(self.char1, "observation", 0))

    def test_obstacle_difficulty_can_overcome_skill(self):
        from unittest.mock import patch

        from world import checks

        self.char1.db.skills = {"observation": 0}
        with patch("world.checks._roll", side_effect=[15, 1]):
            self.assertFalse(checks.opposed_check(self.char1, "observation", 20))


class TestTheGrind(EvenniaTest):
    """v0.6 (ADR 0008): sabotage circuit, courier runs, the underground."""

    def _file_contents(self, char):
        from world import records

        return [rec.db.content for rec in records.records_for(char)]

    def _sensor(self, room=None, active=True, concealment=0):
        sensor = create.create_object(
            "typeclasses.objects.Sensor",
            key="a lens",
            location=room or self.room1,
        )
        sensor.db.sensitivity = 1
        sensor.db.active = active
        sensor.db.concealment = concealment
        return sensor

    def _broker(self):
        broker = create.create_object(
            "typeclasses.npcs.Citizen", key="the broker", location=self.room1
        )
        broker.tags.add("courier_broker", category="grid")
        return broker

    # --- sabotage -----------------------------------------------------------

    def test_sabotage_success_pays_the_underground(self):
        from unittest.mock import patch

        from world import tuning

        sensor = self._sensor()
        self.room1.db.visibility = 0  # one sensor is all that watches here
        with patch("world.checks.opposed_check", return_value=True):
            self.char1.execute_cmd("sabotage lens")
        self.assertFalse(sensor.db.active)
        self.assertIsNotNone(sensor.db.sabotaged_at)
        self.assertEqual(self.char1.skill("sabotage"), 1)
        # Room went fully dark: base pay + dark bonus.
        self.assertEqual(
            (self.char1.db.standing or {}).get(tuning.UNDERGROUND),
            tuning.SABOTAGE_INFLUENCE + tuning.SABOTAGE_DARK_BONUS,
        )
        self.assertEqual(
            self.char1.db.credits,
            tuning.SABOTAGE_INFLUENCE + tuning.SABOTAGE_DARK_BONUS,
        )

    def test_sabotage_failure_is_an_incident(self):
        from unittest.mock import patch

        from world import tuning

        sensor = self._sensor()
        self.char1.db.exposure = 0
        with patch("world.checks.opposed_check", return_value=False):
            self.char1.execute_cmd("sabotage lens")
        self.assertTrue(sensor.db.active)  # device survives
        self.assertEqual(self.char1.db.exposure, tuning.SABOTAGE_FAIL_EXPOSURE)
        self.assertTrue(
            any("interference" in c for c in self._file_contents(self.char1))
        )

    def test_concealed_devices_need_the_check_won_twice(self):
        """Once to be spotted (observation vs. concealment), once to be cut
        (sabotage vs. difficulty) -- both routed through opposed_check."""
        from unittest.mock import patch

        sensor = self._sensor(concealment=9)
        with patch("world.checks.opposed_check", return_value=False):
            self.char1.execute_cmd("sabotage lens")
        self.assertTrue(sensor.db.active)  # can't cut what you can't find
        with patch("world.checks.opposed_check", return_value=True):
            self.char1.execute_cmd("sabotage lens")
        self.assertFalse(sensor.db.active)

    def test_maintenance_repairs_oldest_first(self):
        from typeclasses.scripts import MaintenanceScript

        # Script first: it fires at_repeat once on creation, and must find
        # an empty backlog then.
        script = create.create_script(MaintenanceScript)
        first = self._sensor()
        second = self._sensor()
        first.db.active = False
        first.db.sabotaged_at = 100.0
        second.db.active = False
        second.db.sabotaged_at = 200.0
        script.at_repeat()
        self.assertTrue(first.db.active)
        self.assertFalse(second.db.active)
        script.at_repeat()
        self.assertTrue(second.db.active)
        # The alley pattern: broken-but-never-sabotaged stays broken.
        unreported = self._sensor(active=False)
        script.at_repeat()
        self.assertFalse(unreported.db.active)
        script.stop()

    # --- courier runs -------------------------------------------------------

    def test_carry_and_deliver_pays(self):
        from unittest.mock import patch

        from world import tuning, underground

        self._broker()
        dest_key, pay, _ = tuning.COURIER_JOBS["quiet"]
        self.room2.key = dest_key
        self.char1.execute_cmd("carry quiet")
        self.assertEqual(underground.current_job(self.char1), "quiet")
        self.assertEqual(len(underground.carried_parcels(self.char1)), 1)
        # Wrong room: no dice.
        result = underground.deliver(self.char1)
        self.assertIsInstance(result, str)
        self.char1.move_to(self.room2)
        with patch("world.underground.random.random", return_value=0.99):
            total, jackpot = underground.deliver(self.char1)
        self.assertEqual(total, pay)
        self.assertFalse(jackpot)
        self.assertIsNone(underground.current_job(self.char1))
        self.assertEqual(len(underground.carried_parcels(self.char1)), 0)
        self.assertEqual(
            (self.char1.db.standing or {}).get(tuning.UNDERGROUND), pay
        )
        self.assertEqual(self.char1.db.credits, pay)
        self.assertEqual(self.char1.skill("couriering"), 1)

    def test_papers_check_seizes_contraband(self):
        from typeclasses.scripts import WatchSweepScript

        from world import underground

        self._broker()
        self.char1.execute_cmd("carry quiet")
        self.char1.db.exposure = 30
        WatchSweepScript.papers_check(self.char1)
        self.assertEqual(len(underground.carried_parcels(self.char1)), 0)
        self.assertIsNone(underground.current_job(self.char1))
        self.assertTrue(
            any(
                "unregistered goods" in c
                for c in self._file_contents(self.char1)
            )
        )
        # And no cleared-is-an-alibi relief when you're caught holding.
        self.assertEqual(self.char1.db.exposure, 30)

    def test_papers_check_record_is_throttled_but_relief_is_not(self):
        """Same class of bug as the assembly-absence farm: nothing capped
        how often an identical 'Papers checked' incident could be filed.
        The relief (the point of the interaction) should still apply every
        time; only the file entry should be throttled."""
        from typeclasses.scripts import WatchSweepScript
        from world import tuning

        self.char1.db.exposure = 30
        WatchSweepScript.papers_check(self.char1)
        self.assertEqual(self.char1.db.exposure, 30 - tuning.PAPERS_CHECK_RELIEF)
        self.assertEqual(
            len(
                [
                    c
                    for c in self._file_contents(self.char1)
                    if "Papers checked in the street; cleared." in c
                ]
            ),
            1,
        )
        # Immediately checked again (a back-to-back sweep tick): relief
        # applies again, but no duplicate incident within the cooldown.
        WatchSweepScript.papers_check(self.char1)
        self.assertEqual(
            self.char1.db.exposure, 30 - 2 * tuning.PAPERS_CHECK_RELIEF
        )
        self.assertEqual(
            len(
                [
                    c
                    for c in self._file_contents(self.char1)
                    if "Papers checked in the street; cleared." in c
                ]
            ),
            1,
        )
        # Past the cooldown, a new one is logged.
        self.char1.db.last_papers_check_record -= tuning.PAPERS_CHECK_RECORD_COOLDOWN
        WatchSweepScript.papers_check(self.char1)
        self.assertEqual(
            len(
                [
                    c
                    for c in self._file_contents(self.char1)
                    if "Papers checked in the street; cleared." in c
                ]
            ),
            2,
        )

    def test_scanner_gate_rolls_for_contraband(self):
        from unittest.mock import patch

        from world import underground

        self._broker()
        self.char1.execute_cmd("carry quiet")
        self.exit.db.exposure_modifier = 2
        with patch("random.random", return_value=0.0):
            self.char1.execute_cmd(self.exit.key)
        self.assertEqual(self.char1.location, self.room2)  # you pass; it doesn't
        self.assertEqual(len(underground.carried_parcels(self.char1)), 0)
        self.assertTrue(
            any(
                "unregistered goods" in c
                for c in self._file_contents(self.char1)
            )
        )

    def test_detainment_processing_seizes(self):
        from world import underground, watch

        room = create.create_object(
            "typeclasses.rooms.Room", key="Holding Cell (test)"
        )
        room.tags.add("holding_cell", category="grid")
        self.room1.tags.add("release_point", category="grid")
        self._broker()
        self.char1.execute_cmd("carry quiet")
        self.char1.db.exposure = 60
        watch.detain(self.char1)
        self.assertEqual(len(underground.carried_parcels(self.char1)), 0)
        watch.release(self.char1)

    def test_dossier_hides_the_unsanctioned(self):
        # Playtest catch: the citizen file was printing underground standing
        # and off-the-books aptitudes. The Ministry's file contains only
        # what the Ministry could have observed.
        from world import tuning

        self.char1.db.skills = {"clerking": 3, "sabotage": 5, "forgery": 2}
        self.char1.db.standing = {
            "Ministry of Records": 4,
            tuning.UNDERGROUND: 14,
        }
        old = self.char1.msg
        seen = []
        self.char1.msg = lambda text=None, **kw: seen.append(str(text))
        try:
            self.char1.execute_cmd("dossier")
        finally:
            self.char1.msg = old
        blob = "\n".join(seen)
        self.assertIn("clerking", blob)
        self.assertIn("Ministry of Records", blob)
        self.assertNotIn("sabotage", blob)
        self.assertNotIn("forgery", blob)
        self.assertNotIn(tuning.UNDERGROUND, blob)

    def test_papers_sink_closes_the_loop(self):
        from world import tuning

        self._broker()
        self.char1.db.exposure = 40
        self.char1.execute_cmd("papers")  # can't afford it yet
        self.assertEqual(self.char1.db.exposure, 40)
        self.char1.db.credits = tuning.PAPERS_COST
        self.char1.execute_cmd("papers")
        self.assertEqual(
            self.char1.db.exposure, 40 - tuning.PAPERS_RELIEF
        )
        self.assertEqual(self.char1.db.credits, 0)

    # --- the shadow ladder (ADR 0009) ----------------------------------------

    def _capture(self, char, cmd):
        captured = []
        old_msg = char.msg
        char.msg = lambda text="", **kw: captured.append(str(text))
        try:
            char.execute_cmd(cmd)
        finally:
            char.msg = old_msg
        return "\n".join(captured)

    def test_shadow_standing_names_tiers_and_the_gap(self):
        from world import tuning, underground

        self.char1.db.standing = {tuning.UNDERGROUND: 0}
        standing, tier, next_tier, threshold = underground.shadow_standing(self.char1)
        self.assertEqual(tier, "a face nobody's placed yet")
        self.assertEqual(next_tier, "a runner")
        self.assertEqual(threshold, 5)

        self.char1.db.standing = {tuning.UNDERGROUND: 45}
        standing, tier, next_tier, threshold = underground.shadow_standing(self.char1)
        self.assertEqual(tier, "one of the old hands")
        self.assertIsNone(next_tier)
        self.assertIsNone(threshold)

    def test_word_deflects_in_a_watched_room(self):
        from world import tuning

        self.room1.db.visibility = tuning.SHADOW_LADDER_MAX_VISIBILITY + 1
        text = self._capture(self.char1, "word")
        self.assertIn("Not here", text)

    def test_word_names_the_tier_somewhere_dark(self):
        from world import tuning

        self.room1.db.visibility = 0
        self.char1.db.standing = {tuning.UNDERGROUND: 7}
        text = self._capture(self.char1, "word")
        self.assertIn("a runner", text)
        self.assertIn("reliable", text)


class TestGrades(EvenniaTest):
    """v0.12: the citizen grade — one visible ladder over existing merit."""

    def test_fresh_citizen_is_probationary(self):
        from world import grades

        self.assertEqual(grades.grade_of(self.char1), grades.GRADE_MIN)
        self.assertEqual(grades.merit(self.char1), 0)

    def test_orientation_credit_reaches_grade_5(self):
        # Endowed progress: walking the Demonstration Corridor is sized to
        # land the first grade-up minutes into play. ADR 0018: credit
        # requires having actually tried the four core verbs first.
        from world import grades, records

        self.char1.db.first_use_verbs = {"map", "observe", "dossier", "grade"}
        self.room2.db.visibility = 0
        self.room2.tags.add("orients", category="grid")
        self.char1.move_to(self.room2)
        self.assertTrue(self.char1.db.oriented)
        self.assertEqual(grades.grade_of(self.char1), 5)
        stamped = [
            rec.db.content
            for rec in records.records_for(self.char1, kind="observation")
        ]
        self.assertIn("Reclassified: Citizen, Grade 5", stamped)
        # Walking it again credits nothing twice.
        self.char1.move_to(self.room1)
        self.char1.move_to(self.room2)
        self.assertEqual(grades.merit(self.char1), tuning.GRADE_MERIT_ORIENTATION)

    def test_orientation_withholds_credit_until_core_verbs_tried(self):
        # ADR 0018: walking into the corridor without having tried the
        # four core verbs doesn't silently credit attendance as attention.
        from world import grades

        self.room2.db.visibility = 0
        self.room2.tags.add("orients", category="grid")
        self.char1.move_to(self.room2)
        self.assertFalse(self.char1.db.oriented)
        self.assertEqual(grades.merit(self.char1), 0)
        # Doing the rest, then re-entering, credits it -- no hard lock,
        # just a gate on the credit itself.
        self.char1.db.first_use_verbs = {"map", "observe", "dossier", "grade"}
        self.char1.move_to(self.room1)
        self.char1.move_to(self.room2)
        self.assertTrue(self.char1.db.oriented)
        self.assertEqual(grades.grade_of(self.char1), 5)

    def test_sanctioned_standing_is_merit_but_underground_is_not(self):
        from world import grades

        self.char1.gain_standing_and_credits("Ministry of Records", 10)
        self.assertEqual(grades.merit(self.char1), 10)
        self.char1.gain_standing_and_credits(tuning.UNDERGROUND, 50)
        # The Grid ranks what the Grid can see.
        self.assertEqual(grades.merit(self.char1), 10)

    def test_spending_credits_never_demotes(self):
        from world import grades

        self.char1.gain_standing_and_credits("Ministry of Records", 20)
        grade_before = grades.grade_of(self.char1)
        self.char1.spend_credits(18)
        self.assertEqual(grades.merit(self.char1), 20)
        self.assertEqual(grades.grade_of(self.char1), grade_before)

    def test_unsanctioned_errands_earn_no_merit(self):
        from world import grades

        self.char1.db.errands_done = ["rounds", "legs"]
        # "rounds" pays the Ministry (counts); "legs" pays the underground.
        self.assertEqual(
            grades.merit(self.char1), tuning.GRADE_MERIT_PER_ERRAND
        )

    def test_function_suspension_demotes(self):
        from world import functions, grades

        self.char1.gain_standing_and_credits("Ministry of Records", 12)
        functions.assign_function(self.char1)
        self.assertEqual(grades.grade_of(self.char1), 4)  # 12 + 5 = 17
        functions.suspend_function(self.char1)
        self.assertEqual(grades.grade_of(self.char1), 5)  # back to 12

    def test_clearance_counts(self):
        from world import functions, grades

        functions.grant_c1(self.char1)
        self.assertEqual(
            grades.merit(self.char1), tuning.GRADE_MERIT_CLEARANCE
        )

    def test_prompt_and_dossier_show_the_ladder(self):
        from world import grades

        self.assertIn("Grade:6", self.char1.get_prompt())
        self.char1.db.oriented = True
        grades.check_reclassification(self.char1)
        self.assertIn("Grade:5", self.char1.get_prompt())
        old_msg = self.char1.msg
        captured = []
        self.char1.msg = lambda text="", **kw: captured.append(str(text))
        try:
            self.char1.execute_cmd("dossier")
        finally:
            self.char1.msg = old_msg
        text = "\n".join(captured)
        self.assertIn("Grade:     Citizen, Grade 5", text)
        self.assertIn("Review threshold for Grade 4", text)


class TestFirstHour(EvenniaTest):
    """v0.13: staged help, the `next` advisor, `grade`, and the aliases."""

    def _capture(self, char, cmd):
        captured = []
        old_msg = char.msg
        char.msg = lambda text="", **kw: captured.append(str(text))
        try:
            char.execute_cmd(cmd)
        finally:
            char.msg = old_msg
        return "\n".join(captured)

    def test_bare_help_is_abridged_until_oriented(self):
        text = self._capture(self.char1, "help")
        self.assertIn("ABRIDGED", text)
        self.assertIn("help all", text)
        self.char1.db.oriented = True
        text = self._capture(self.char1, "help")
        self.assertNotIn("ABRIDGED", text)

    def test_help_all_is_always_the_full_index(self):
        text = self._capture(self.char1, "help all")
        self.assertNotIn("ABRIDGED", text)
        # The full index shows commands the abridged card never names.
        self.assertIn("sabotage", text)

    def test_help_topic_unaffected(self):
        text = self._capture(self.char1, "help exposure")
        self.assertIn("down is good", text)

    def test_next_walks_the_priority_ladder(self):
        # Unoriented: pointed at the Wing.
        text = self._capture(self.char1, "next")
        self.assertIn("orientation", text)
        # Oriented but unassigned: pointed at `report`.
        self.char1.db.oriented = True
        text = self._capture(self.char1, "next")
        self.assertIn("report", text)
        # Assigned and hot: pointed at cooling down.
        from world import functions

        functions.assign_function(self.char1)
        # Assigned, cool, errandless: pointed at a giver — and at the
        # clerk's safe chain first, never the underground's.
        text = self._capture(self.char1, "next")
        self.assertIn("orientation clerk", text)
        self.char1.db.exposure = tuning.HOT_EXPOSURE
        text = self._capture(self.char1, "next")
        self.assertIn("work", text)
        # An active errand outranks everything.
        self.char1.db.errand = {"key": "rounds", "progress": []}
        text = self._capture(self.char1, "next")
        self.assertIn("The Rounds", text)

    def test_grade_command_and_muscle_memory_aliases(self):
        for cmd in ("grade", "level", "rank"):
            text = self._capture(self.char1, cmd)
            self.assertIn("Citizen, Grade 6", text)
            self.assertIn("Review threshold", text)

    def test_quests_alias_reaches_errands(self):
        text = self._capture(self.char1, "quests")
        self.assertIn("errand", text.lower())

    def test_next_names_alternatives_once_catalog_exhausted(self):
        """Round-two playtest finding 3: the fallback used to be vague."""
        from world import errands, functions

        self.char1.db.oriented = True
        functions.assign_function(self.char1)
        self.char1.db.errands_done = list(errands.ERRANDS.keys())
        text = self._capture(self.char1, "next")
        self.assertIn("underground", text)
        self.assertIn("circle", text)

    def test_report_sets_oriented(self):
        """Round-two playtest finding 4: skippers were locked out of `help`
        forever. Taking a function is the other real milestone."""
        self.room1.tags.add("workplace", category="grid")
        self.assertFalse(self.char1.db.oriented)
        self.char1.execute_cmd("report")
        self.assertTrue(self.char1.db.oriented)

    def test_x_is_an_alias_for_look(self):
        text = self._capture(self.char1, "x")
        self.assertIn(self.room1.key, text)

    def test_help_the_grid_reaches_the_entry_not_a_category_listing(self):
        """Round-two playtest finding 1: key/category collision. "sector 9"
        dropped as an alias here since it's now the shared category name
        for this whole file — see help_entries.py's comment."""
        for cmd in ("help the grid", "help 2084", "help basics"):
            text = self._capture(self.char1, cmd)
            self.assertIn("not a game about killing things", text)

    def test_help_standing_exists(self):
        """Round-two playtest finding 2: no help coverage at all."""
        text = self._capture(self.char1, "help standing")
        self.assertIn("institution", text.lower())


class TestGridHearsYou(EvenniaTest):
    """v0.14: the no-match handler — directions, instincts, clean hints."""

    def _capture(self, char, cmd):
        captured = []
        old_msg = char.msg
        char.msg = lambda text="", **kw: captured.append(str(text))
        try:
            char.execute_cmd(cmd)
        finally:
            char.msg = old_msg
        return "\n".join(captured)

    def test_missing_direction_names_the_real_exits(self):
        text = self._capture(self.char1, "west")
        self.assertIn("Nothing leads west", text)
        self.assertIn(self.exit.key, text)
        self.assertNotIn("Maybe you meant", text)

    def test_kill_gets_the_thesis_not_boilerplate(self):
        text = self._capture(self.char1, "kill guard")
        self.assertIn("paperwork", text)
        self.assertNotIn("not available", text)

    def test_hide_points_at_the_mechanic_that_exists(self):
        text = self._capture(self.char1, "hide")
        self.assertIn("visibility", text)

    def test_talk_points_at_say(self):
        text = self._capture(self.char1, "talk to the clerk")
        self.assertIn("say", text)

    def test_npc_deflection_line_used_when_present(self):
        npc = create.create_object(
            "typeclasses.npcs.Citizen", key="the test clerk", location=self.room1
        )
        npc.db.deflection = "The clerk has nothing to say to you."
        text = self._capture(self.char1, "ask clerk about badges")
        self.assertIn("nothing to say", text)

    def test_npc_deflection_matches_the_named_target(self):
        clerk = create.create_object(
            "typeclasses.npcs.Citizen", key="the ration clerk", location=self.room1
        )
        clerk.db.deflection = "The clerk says nothing useful."
        broker = create.create_object(
            "typeclasses.npcs.Citizen", key="the broker", location=self.room1
        )
        broker.db.deflection = "The broker recites her line about turnips."
        text = self._capture(self.char1, "ask broker about turnips")
        self.assertIn("turnips", text)
        self.assertNotIn("nothing useful", text)

    def test_suggestions_never_leak_the_chalk_or_the_engine(self):
        # Near-misses on unsanctioned and engine verbs must not be
        # corrected toward them.
        for probe in ("sabotag", "stashh", "charcreat", "setdes"):
            text = self._capture(self.char1, probe)
            # A suggestion may be offered (e.g. 'setdes' -> dossier), but
            # never a chalk or engine verb.
            for forbidden in ("|csabotage|n", "|cstash|n",
                              "|ccharcreate|n", "|csetdesc|n"):
                self.assertNotIn(forbidden, text)
        # ...while sanctioned near-misses still get help.
        text = self._capture(self.char1, "dossie")
        self.assertIn("dossier", text)

    def test_go_walks_a_real_exit(self):
        self.assertEqual(self.char1.location, self.room1)
        self._capture(self.char1, f"go {self.exit.key}")
        self.assertEqual(self.char1.location, self.room2)


class TestRecordCompaction(EvenniaTest):
    """ADR 0011: old routine incidents fold into a lifetime count."""

    def _old_incident(self, char, content, type_key, age=None):
        import time

        from world import records, tuning

        rec = records.add_record(char, content, kind="incident", type_key=type_key)
        rec.db.created = time.time() - (age or tuning.RECORD_COMPACTION_AGE + 1)
        return rec

    def _archivist(self):
        archivist = create.create_object(
            "typeclasses.npcs.Citizen", key="the archivist", location=self.room1
        )
        archivist.tags.add("records_service", category="grid")
        return archivist

    def _captured(self, char, command):
        old = char.msg
        seen = []
        char.msg = lambda text=None, **kw: seen.append(str(text))
        try:
            char.execute_cmd(command)
        finally:
            char.msg = old
        return "\n".join(seen)

    def test_compaction_folds_old_untouched_routine_incidents(self):
        from world import records

        self._old_incident(self.char1, "Papers checked in the street; cleared.", "papers_check")
        self._old_incident(self.char1, "Papers checked in the street; cleared.", "papers_check")
        records.compact_incidents(self.char1)
        self.assertEqual(records.summary_for(self.char1, "papers_check"), (2, 2))
        self.assertEqual(len(records.records_for(self.char1, kind="incident")), 0)

    def test_compaction_skips_recent_and_milestone_and_touched(self):
        from world import records

        # Too recent: not eligible yet.
        self._old_incident(
            self.char1, "Papers checked in the street; cleared.", "papers_check", age=60
        )
        # Milestone (no type_key): never eligible.
        self._old_incident(self.char1, "DETAINED: routine sweep.", None)
        # Touched (redacted before compaction runs): pinned forever.
        touched = self._old_incident(
            self.char1, "Papers checked in the street; cleared.", "papers_check"
        )
        records.redact(touched, actor=self.char1)

        records.compact_incidents(self.char1)
        self.assertEqual(records.summary_for(self.char1, "papers_check"), (0, 0))
        self.assertEqual(len(records.records_for(self.char1, kind="incident")), 3)

    def test_compaction_grows_the_same_bucket_over_multiple_passes(self):
        from world import records

        self._old_incident(self.char1, "Papers checked in the street; cleared.", "papers_check")
        records.compact_incidents(self.char1)
        self._old_incident(self.char1, "Papers checked in the street; cleared.", "papers_check")
        records.compact_incidents(self.char1)
        self.assertEqual(records.summary_for(self.char1, "papers_check"), (2, 2))

    def test_prune_observations_keeps_only_the_retention_window(self):
        from world import records, tuning

        for i in range(tuning.MOVEMENT_LOG_RETENTION + 5):
            records.add_record(
                self.char1,
                f"Logged at Room {i}",
                kind="observation",
                type_key="sensor_movement",
            )
        records.prune_observations(self.char1)
        remaining = records.records_for(self.char1, kind="observation")
        self.assertEqual(len(remaining), tuning.MOVEMENT_LOG_RETENTION)
        # The oldest were the ones pruned; the newest survive.
        self.assertEqual(remaining[-1].db.content, "Logged at Room 24")

    def test_dossier_shows_the_summarized_section(self):
        from world import records

        self._old_incident(self.char1, "Papers checked in the street; cleared.", "papers_check")
        self._old_incident(self.char1, "Papers checked in the street; cleared.", "papers_check")
        records.compact_incidents(self.char1)
        blob = self._captured(self.char1, "dossier")
        self.assertIn("Routine incidents on file:", blob)
        self.assertIn("Papers checked in the street; cleared.: 2 on file", blob)
        self.assertIn("papers-checks", blob)

    def test_petition_redact_by_keyword(self):
        from world import records, tuning

        self._archivist()
        self._old_incident(self.char1, "Papers checked in the street; cleared.", "papers_check")
        self._old_incident(self.char1, "Papers checked in the street; cleared.", "papers_check")
        records.compact_incidents(self.char1)
        self.char1.db.credits = tuning.REDACT_COST
        self.char1.execute_cmd("petition redact papers-checks")
        self.assertEqual(records.summary_for(self.char1, "papers_check"), (2, 1))
        self.assertEqual(self.char1.db.credits, 0)

    def test_petition_amend_refuses_a_keyword_target(self):
        from world import records

        self._archivist()
        self._old_incident(self.char1, "Papers checked in the street; cleared.", "papers_check")
        records.compact_incidents(self.char1)
        blob = self._captured(
            self.char1, "petition amend papers-checks = something else"
        )
        self.assertIn("no single entry", blob)
        self.assertEqual(records.summary_for(self.char1, "papers_check"), (1, 1))

    def test_forge_by_keyword_success_and_failure(self):
        from unittest.mock import patch

        from world import records

        self.room1.db.visibility = 0
        self._old_incident(self.char1, "Papers checked in the street; cleared.", "papers_check")
        self._old_incident(self.char1, "Papers checked in the street; cleared.", "papers_check")
        records.compact_incidents(self.char1)

        with patch("world.checks.opposed_check", return_value=False):
            self._captured(self.char1, "forge papers-checks")
        self.assertEqual(records.summary_for(self.char1, "papers_check"), (2, 2))
        contents = [r.db.content for r in records.records_for(self.char1, kind="incident")]
        self.assertTrue(any("tampering" in c for c in contents))

        with patch("world.checks.opposed_check", return_value=True):
            self._captured(self.char1, "forge papers-checks")
        self.assertEqual(records.summary_for(self.char1, "papers_check"), (2, 1))


class TestArchaeology(EvenniaTest):
    """ADR 0016: records archaeology, the third grind loop."""

    def setUp(self):
        super().setUp()
        self.archivist = create.create_object(
            "typeclasses.npcs.Citizen", key="the archivist", location=self.room1
        )
        self.archivist.tags.add("records_service", category="grid")

    def _captured(self, char, command):
        old = char.msg
        seen = []
        char.msg = lambda text=None, **kw: seen.append(str(text))
        try:
            char.execute_cmd(command)
        finally:
            char.msg = old
        return "\n".join(seen)

    def test_research_requires_the_archivist(self):
        self.char1.move_to(self.room2)
        self.char1.db.standing = {}
        self.char1.execute_cmd("research")
        self.assertFalse((self.char1.db.standing or {}).get("Ministry of Records"))

    def test_research_pays_costs_and_teaches_clerking(self):
        from unittest.mock import patch

        from world import archaeology, tuning

        self.char1.db.exposure = 0
        with patch("world.archaeology.random.random", return_value=0.99):
            archaeology.research(self.char1)
        self.assertEqual(self.char1.skill("clerking"), 1)
        self.assertEqual(
            (self.char1.db.standing or {}).get("Ministry of Records"),
            tuning.RESEARCH_INFLUENCE,
        )
        self.assertEqual(self.char1.db.exposure, tuning.RESEARCH_EXPOSURE)

    def test_research_off_cooldown_texture_reflects_proximity(self):
        import time

        from commands.civic import CmdResearch
        from world import tuning

        self.char1.db.last_research = time.time()
        blob = self._captured(self.char1, "research")
        self.assertIn(blob, CmdResearch.FAR_LINES)

        self.char1.db.last_research = (
            time.time()
            - tuning.RESEARCH_COOLDOWN * tuning.WORK_NEAR_COOLDOWN_FRACTION
        )
        blob = self._captured(self.char1, "research")
        self.assertIn(blob, CmdResearch.NEAR_LINES)

    def test_generic_case_completes_and_pays_underground(self):
        from unittest.mock import patch

        from world import archaeology, tuning

        with patch("world.archaeology.random.random", return_value=0.99):
            for _ in range(tuning.CASE_FRAGMENTS_REQUIRED):
                archaeology.research(self.char1)
        self.assertIsNone(self.char1.db.archaeology_case)
        self.assertEqual(
            (self.char1.db.standing or {}).get(tuning.UNDERGROUND),
            tuning.CASE_COMPLETION_PAYOUT,
        )

    def test_a_new_case_starts_after_completion(self):
        from unittest.mock import patch

        from world import archaeology, tuning

        with patch("world.archaeology.random.random", return_value=0.99):
            for _ in range(tuning.CASE_FRAGMENTS_REQUIRED):
                archaeology.research(self.char1)
            archaeology.research(self.char1)
        self.assertIsNotNone(self.char1.db.archaeology_case)
        self.assertEqual(len(self.char1.db.archaeology_case["found"]), 1)

    def test_named_case_completes_marks_solved_and_pays_more(self):
        from unittest.mock import patch

        from world import archaeology, tuning

        key = next(iter(archaeology.NAMED_CASES))
        count = len(archaeology.NAMED_CASES[key]["fragments"])
        with patch("world.archaeology.random.random", return_value=0.0), patch(
            "world.archaeology._next_named_draw", return_value=key
        ):
            for _ in range(count):
                archaeology.research(self.char1)
        self.assertIn(key, self.char1.db.archaeology_solved)
        self.assertEqual(
            (self.char1.db.standing or {}).get(tuning.UNDERGROUND),
            tuning.NAMED_CASE_PAYOUT,
        )
        self.assertNotIn(key, self.char1.db.archaeology_named or {})

    def test_solved_named_cases_are_never_redrawn(self):
        from world import archaeology

        self.char1.db.archaeology_solved = list(archaeology.NAMED_CASES.keys())
        self.assertIsNone(archaeology._next_named_draw(self.char1))


class TestPropaganda(EvenniaTest):
    """ADR 0017: the propaganda engine narrates the existing alert level."""

    def setUp(self):
        super().setUp()
        from world import propaganda, watch

        propaganda._save_registry({"sabotage": 0, "courier": 0})
        watch.set_alert(0)

    def test_pick_bulletin_resets_the_tally(self):
        from world import propaganda

        propaganda.record("sabotage")
        propaganda.record("sabotage")
        propaganda.pick_bulletin()
        self.assertEqual(propaganda._registry(), {"sabotage": 0, "courier": 0})

    def test_quiet_tick_is_usually_silent(self):
        from unittest.mock import patch

        from world import propaganda

        with patch("world.propaganda.random.random", return_value=0.99):
            self.assertIsNone(propaganda.pick_bulletin())

    def test_quiet_tick_occasionally_speaks_anyway(self):
        from unittest.mock import patch

        from world import propaganda

        with patch("world.propaganda.random.random", return_value=0.0):
            blob = propaganda.pick_bulletin()
        self.assertIn(blob, propaganda.QUIET_BULLETINS)

    def test_low_activity_reads_as_low_tier(self):
        from world import propaganda, tuning

        self.assertGreater(tuning.PROPAGANDA_ELEVATED_THRESHOLD, 1)
        propaganda.record("courier")
        blob = propaganda.pick_bulletin()
        self.assertIn(blob, propaganda.LOW_BULLETINS)

    def test_heavy_activity_reads_as_high_tier(self):
        from world import propaganda, tuning

        for _ in range(tuning.PROPAGANDA_HIGH_THRESHOLD):
            propaganda.record("sabotage")
        blob = propaganda.pick_bulletin()
        self.assertIn(blob, propaganda.HIGH_BULLETINS)

    def test_existing_alert_alone_reads_as_elevated_or_higher(self):
        from world import propaganda, watch, tuning

        watch.set_alert(1)
        blob = propaganda.pick_bulletin()
        self.assertIn(blob, propaganda.ELEVATED_BULLETINS)

        watch.set_alert(tuning.ALERT_MAX)
        blob = propaganda.pick_bulletin()
        self.assertIn(blob, propaganda.HIGH_BULLETINS)

    def test_sabotage_and_delivery_record_events(self):
        from unittest.mock import patch

        from world import propaganda, tuning, underground

        self.room1.tags.add("workplace", category="grid")
        sensor = create.create_object(
            "typeclasses.objects.Sensor", key="a lens", location=self.room1
        )
        with patch("world.checks.opposed_check", return_value=True):
            self.char1.execute_cmd("sabotage lens")
        self.assertEqual(propaganda._registry()["sabotage"], 1)

        broker = create.create_object(
            "typeclasses.npcs.Citizen", key="the broker", location=self.room1
        )
        broker.tags.add("courier_broker", category="grid")
        dest_key, _, _ = tuning.COURIER_JOBS["quiet"]
        self.room2.key = dest_key
        self.char1.execute_cmd("carry quiet")
        self.char1.move_to(self.room2)
        with patch("world.underground.random.random", return_value=0.99):
            underground.deliver(self.char1)
        self.assertEqual(propaganda._registry()["courier"], 1)

    def test_script_stays_silent_with_nobody_online(self):
        from unittest.mock import patch

        from typeclasses.scripts import PropagandaScript
        from world import propaganda

        propaganda.record("sabotage")
        propaganda.record("sabotage")
        # Script creation can fire an immediate first tick, so the patch
        # must be in place before create_script, not just before the
        # explicit at_repeat() call below.
        with patch.object(PropagandaScript, "_citizens", return_value=[]):
            script = create.create_script(PropagandaScript)
            script.at_repeat()
        script.stop()
        # Tally untouched: the tick was skipped outright, not consumed.
        self.assertEqual(propaganda._registry()["sabotage"], 2)

    def test_script_broadcasts_to_online_citizens(self):
        from unittest.mock import patch

        from typeclasses.scripts import PropagandaScript
        from world import propaganda

        propaganda.record("sabotage")
        seen = []
        old = self.char1.msg
        self.char1.msg = lambda text=None, **kw: seen.append(str(text))
        try:
            script = create.create_script(PropagandaScript)
            with patch("world.propaganda.random.random", return_value=0.0):
                script.at_repeat()
            script.stop()
        finally:
            self.char1.msg = old
        self.assertTrue(seen)


class TestUpperSpire(EvenniaTest):
    """ADR 0021: floor C-2 -- escalating Form C-2, elevation reuses Exposure."""

    def test_adjudicate_c2_requires_c1_first(self):
        from world import functions

        self.char1.db.civic_status = {}
        approved, reason = functions.adjudicate_c2(self.char1)
        self.assertFalse(approved)
        self.assertIn("C-1", reason)

    def test_adjudicate_c2_rejects_already_holding_c2(self):
        from world import functions

        self.char1.db.civic_status = {"clearance": "C-2"}
        approved, reason = functions.adjudicate_c2(self.char1)
        self.assertFalse(approved)
        self.assertIn("already holds", reason)

    def test_adjudicate_c2_tighter_incident_bar_than_c1(self):
        from world import functions, watch

        self.char1.db.civic_status = {"clearance": "C-1"}
        functions.assign_function(self.char1)
        # C-1's own bar tolerates one visible incident (tuning.CLEARANCE_
        # MAX_INCIDENTS == 1); C-2's bar (== 0) does not.
        watch.add_record_note(self.char1, "Papers checked in the street; cleared.")
        approved, reason = functions.adjudicate_c2(self.char1)
        self.assertFalse(approved)
        self.assertIn("references", reason)

    def test_adjudicate_c2_approves_clean_c1_holder_with_function(self):
        from world import functions

        self.char1.db.civic_status = {"clearance": "C-1"}
        functions.assign_function(self.char1)
        approved, _ = functions.adjudicate_c2(self.char1)
        self.assertTrue(approved)

    def test_grant_c2_sets_clearance_and_taxes_exposure(self):
        from world import functions, tuning

        self.char1.db.civic_status = {"clearance": "C-1"}
        self.char1.db.exposure = 0
        functions.grant_c2(self.char1)
        self.assertEqual(functions.clearance_level(self.char1), 2)
        self.assertEqual(
            self.char1.db.exposure, tuning.CLEARANCE_C2_GRANT_EXPOSURE
        )

    def test_apply_routes_to_form_c2_for_c1_holders(self):
        from world import functions, records, tuning

        archivist = create.create_object(
            "typeclasses.npcs.Citizen", key="the archivist", location=self.room1
        )
        archivist.tags.add("records_service", category="grid")
        # Order matters: assign_function reads-merges-writes db.civic_status,
        # so setting clearance first (not after) keeps both keys instead of
        # the second assignment wiping out function_key.
        self.char1.db.civic_status = {"clearance": "C-1"}
        functions.assign_function(self.char1)
        self.char1.db.credits = tuning.CLEARANCE_FEE
        self.char1.execute_cmd("apply")  # menu: start
        self.char1.execute_cmd("1")  # take up the pen
        self.char1.execute_cmd("1")  # purpose: service
        self.char1.execute_cmd("1")  # affirm and submit
        self.assertEqual(functions.clearance_level(self.char1), 2)
        outcomes = [
            r.db.content
            for r in records.records_for(self.char1, kind="observation")
        ]
        self.assertTrue(
            any("Form C-2" in c and "APPROVED" in c for c in outcomes)
        )

    def test_apply_declines_when_already_c2(self):
        archivist = create.create_object(
            "typeclasses.npcs.Citizen", key="the archivist", location=self.room1
        )
        archivist.tags.add("records_service", category="grid")
        self.char1.db.civic_status = {"clearance": "C-2"}
        seen = []
        old = self.char1.msg
        self.char1.msg = lambda text=None, **kw: seen.append(str(text))
        try:
            self.char1.execute_cmd("apply")
        finally:
            self.char1.msg = old
        self.assertTrue(any("Nothing further" in s for s in seen))

    def test_c2_gate_requires_clearance_two(self):
        self.exit.locks.add("traverse:clearance(2)")
        self.exit.db.err_traverse = "Turned away."
        self.char1.db.civic_status = {"clearance": "C-1"}
        self.char1.execute_cmd(self.exit.key)
        self.assertEqual(self.char1.location, self.room1)  # blocked at C-1
        self.char1.db.civic_status = {"clearance": "C-2"}
        self.char1.execute_cmd(self.exit.key)
        self.assertEqual(self.char1.location, self.room2)  # admitted at C-2

    def test_spire_idle_script_raises_exposure_after_window(self):
        import time

        from typeclasses.scripts import SpireIdleScript
        from world import tuning

        self.room1.tags.add("spire_c2_corridor", category="grid")
        self.char1.db.exposure = 0
        script = create.create_script(SpireIdleScript)
        try:
            # Pre-seed as if the character has already been standing here
            # past the idle window, rather than waiting real time out.
            script.db.seen_since = {
                self.char1.id: time.time() - tuning.SPIRE_IDLE_EXPOSURE_WINDOW - 1
            }
            script.at_repeat()
        finally:
            script.stop()
        self.assertEqual(self.char1.db.exposure, tuning.SPIRE_IDLE_EXPOSURE_GAIN)

    def test_spire_idle_script_does_not_fire_on_first_sighting(self):
        from typeclasses.scripts import SpireIdleScript

        self.room1.tags.add("spire_c2_corridor", category="grid")
        self.char1.db.exposure = 0
        script = create.create_script(SpireIdleScript)
        try:
            script.at_repeat()  # first sighting only -- registers, no fire
        finally:
            script.stop()
        self.assertEqual(self.char1.db.exposure, 0)


class TestOutsideTheGrid(EvenniaTest):
    """ADR 0022: shadow-standing gate, land/water records as Parcel subjects."""

    def _parcel(self, kind="survey", owner=None, content="Land survey: within projection."):
        from world import records

        parcel = create.create_object(
            "typeclasses.land.Parcel", key=f"a {kind} parcel"
        )
        parcel.db.parcel_kind = kind
        parcel.db.owner = owner
        records.add_record(
            parcel, content, author="Ministry of Records", kind=kind
        )
        return parcel

    def test_shadow_standing_lockfunc_gates_exit(self):
        from world import tuning

        self.exit.locks.add(
            f"traverse:shadow_standing({tuning.OUTSIDE_GRID_ENTRY_STANDING})"
        )
        self.exit.db.err_traverse = "Turned away."
        self.char1.db.standing = {tuning.UNDERGROUND: tuning.OUTSIDE_GRID_ENTRY_STANDING - 1}
        self.char1.execute_cmd(self.exit.key)
        self.assertEqual(self.char1.location, self.room1)  # blocked below
        self.char1.db.standing = {tuning.UNDERGROUND: tuning.OUTSIDE_GRID_ENTRY_STANDING}
        self.char1.execute_cmd(self.exit.key)
        self.assertEqual(self.char1.location, self.room2)  # admitted at threshold

    def test_parcel_records_reuse_the_generic_subject_api(self):
        from world import records

        parcel = self._parcel(owner=self.char1)
        found = records.records_for(parcel, kind="survey")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].db.subject, parcel)

    def test_forge_survey_success_as_owner(self):
        from unittest.mock import patch

        self._parcel(kind="survey", owner=self.char1)
        self.room1.db.visibility = 0
        with patch("world.checks.opposed_check", return_value=True):
            self.char1.execute_cmd("forge survey = Boundary revised, quietly")
        from world import records

        parcel = self._owned_parcel_helper()
        rec = [
            r
            for r in records.records_for(parcel, kind="survey")
            if not r.db.redacted
        ][-1]
        self.assertEqual(rec.db.content, "Boundary revised, quietly")

    def _owned_parcel_helper(self):
        from typeclasses.land import Parcel

        for parcel in Parcel.objects.all():
            if parcel.db.owner is self.char1:
                return parcel
        return None

    def test_forge_survey_failure_is_an_incident(self):
        from unittest.mock import patch

        from world import records, tuning

        self._parcel(kind="survey", owner=self.char1)
        self.room1.db.visibility = 0
        self.char1.db.exposure = 0
        with patch("world.checks.opposed_check", return_value=False):
            self.char1.execute_cmd("forge survey = Boundary revised, quietly")
        self.assertEqual(self.char1.db.exposure, tuning.FORGE_FAIL_EXPOSURE)
        incident_contents = [
            r.db.content for r in records.records_for(self.char1, kind="incident")
        ]
        self.assertTrue(any("tampering" in c for c in incident_contents))

    def test_forge_rejects_non_owner(self):
        from typeclasses.land import Parcel
        from world import records

        self._parcel(kind="survey", owner=self.char2)
        self.room1.db.visibility = 0
        self.char1.execute_cmd("forge survey = Boundary revised, quietly")
        # Char1 owns nothing, so the record on char2's parcel is untouched.
        parcel = next(p for p in Parcel.objects.all() if p.db.owner is self.char2)
        rec = records.records_for(parcel, kind="survey")[0]
        self.assertEqual(rec.db.content, "Land survey: within projection.")

    def test_forge_land_needs_a_dead_zone(self):
        self._parcel(kind="survey", owner=self.char1)
        self.room1.db.visibility = 3
        self.char1.execute_cmd("forge survey = Boundary revised, quietly")
        parcel = self._owned_parcel_helper()
        from world import records

        rec = records.records_for(parcel, kind="survey")[0]
        self.assertEqual(rec.db.content, "Land survey: within projection.")

    def test_petition_amend_survey_full_flow(self):
        from world import functions, records, tuning

        archivist = create.create_object(
            "typeclasses.npcs.Citizen", key="the archivist", location=self.room1
        )
        archivist.tags.add("records_service", category="grid")
        self._parcel(kind="survey", owner=self.char1)
        self.char1.db.credits = tuning.AMEND_COST
        self.char1.execute_cmd("petition amend survey = Corrected boundary")
        parcel = self._owned_parcel_helper()
        rec = [
            r
            for r in records.records_for(parcel, kind="survey")
            if not r.db.redacted
        ][-1]
        self.assertEqual(rec.db.content, "Corrected boundary")
        self.assertEqual(self.char1.db.credits, 0)

    def test_petition_land_rejects_non_owner(self):
        archivist = create.create_object(
            "typeclasses.npcs.Citizen", key="the archivist", location=self.room1
        )
        archivist.tags.add("records_service", category="grid")
        self._parcel(kind="allotment", owner=self.char2)
        from world import tuning

        self.char1.db.credits = tuning.AMEND_COST
        self.char1.execute_cmd("petition redact allotment")
        from typeclasses.land import Parcel
        from world import records

        parcel = next(p for p in Parcel.objects.all() if p.db.owner is self.char2)
        rec = records.records_for(parcel, kind="allotment")[0]
        self.assertFalse(rec.db.redacted)
