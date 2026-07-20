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
            (self.char1.db.standing or {}).get("function"),
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
        self.assertFalse((self.char1.db.influence or {}).get("Ministry of Order"))
        create.create_object(
            "typeclasses.objects.Sensor", key="a lens", location=self.room1
        )
        self.char1.db.last_work = 0
        self.char1.execute_cmd("work")
        self.assertEqual(
            (self.char1.db.influence or {}).get("Ministry of Order"),
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
            "suspended", (self.char1.db.standing or {}).get("function", "")
        )

    def test_clearance_lock_gates_exit(self):
        from evennia.utils.search import search_object

        self.exit.locks.add("traverse:clearance(1)")
        self.exit.db.err_traverse = "Turned away."
        self.char1.execute_cmd(self.exit.key)
        self.assertEqual(self.char1.location, self.room1)  # blocked
        self.char1.db.standing = {"clearance": "C-1"}
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
        self.char1.db.influence = {"Ministry of Records": tuning.CLEARANCE_FEE}
        self.char1.execute_cmd("apply")   # menu: start
        self.char1.execute_cmd("1")       # take up the pen
        self.char1.execute_cmd("1")       # purpose: to better serve
        self.char1.execute_cmd("1")       # affirm and submit
        self.assertEqual(functions.clearance_level(self.char1), 1)
        self.assertEqual(
            (self.char1.db.influence or {}).get("Ministry of Records"), 0
        )
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
        self.char1.db.influence = {}
        self.char1.execute_cmd("flip tea vendor")
        self.assertEqual(npc.db.loyalty, "ministry")  # can't afford it
        self.char1.db.influence = {"Ministry of Commerce": tuning.FLIP_COST}
        self.char1.execute_cmd("flip tea vendor")
        self.assertEqual(npc.db.loyalty, "street")
        self.assertEqual(
            (self.char1.db.influence or {}).get("Ministry of Commerce"), 0
        )

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

    # --- the honeypot -------------------------------------------------------

    def _honeypot(self):
        """A room that reads Vis 0 and is lying about it."""
        self.room2.db.visibility = 0
        seam = create.create_object(
            "typeclasses.objects.Sensor", key="a seam", location=self.room2
        )
        seam.db.sensitivity = 1
        seam.db.active = True
        seam.db.concealed = True
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

    def test_observe_reveals_concealed_only_to_practiced_eyes(self):
        from world import tuning

        self._honeypot()
        self.char1.move_to(self.room2)
        self.char1.db.skills = {"observation": tuning.OBSERVE_TIER_DETAIL}
        blob = self._captured(self.char1, "observe")
        self.assertIn("no fixed devices", blob)
        self.char1.db.skills = {"observation": tuning.OBSERVE_TIER_CONCEALED}
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

    def test_buy_costs_standing_and_state_issue_is_recorded(self):
        from world import records, tuning

        self._vendor()
        self.char1.db.influence = {"Ministry of Records": 10}
        self.char1.execute_cmd("buy badge")
        self.assertEqual(
            (self.char1.db.influence or {}).get("Ministry of Records"),
            10 - tuning.GEAR_PRICES["badge"][1],
        )
        self.assertTrue(
            any(
                "Issued" in r.db.content
                for r in records.records_for(self.char1, kind="observation")
            )
        )
        # No spares.
        self.char1.db.influence = {"Ministry of Records": 10}
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
        self.char1.db.influence = {tuning.UNDERGROUND: 1}
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
            (self.char1.db.influence or {}).get("Ministry of Records"),
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
            (self.char1.db.influence or {}).get("Ministry of Records"),
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
            (self.char1.db.influence or {}).get(tuning.UNDERGROUND, 0),
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


class TestTheGrind(EvenniaTest):
    """v0.6 (ADR 0008): sabotage circuit, courier runs, the underground."""

    def _file_contents(self, char):
        from world import records

        return [rec.db.content for rec in records.records_for(char)]

    def _sensor(self, room=None, active=True, concealed=False):
        sensor = create.create_object(
            "typeclasses.objects.Sensor",
            key="a lens",
            location=room or self.room1,
        )
        sensor.db.sensitivity = 1
        sensor.db.active = active
        sensor.db.concealed = concealed
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
        with patch("world.underground.random.random", return_value=0.0):
            self.char1.execute_cmd("sabotage lens")
        self.assertFalse(sensor.db.active)
        self.assertIsNotNone(sensor.db.sabotaged_at)
        self.assertEqual(self.char1.skill("sabotage"), 1)
        # Room went fully dark: base pay + dark bonus.
        self.assertEqual(
            (self.char1.db.influence or {}).get(tuning.UNDERGROUND),
            tuning.SABOTAGE_INFLUENCE + tuning.SABOTAGE_DARK_BONUS,
        )

    def test_sabotage_failure_is_an_incident(self):
        from unittest.mock import patch

        from world import tuning

        sensor = self._sensor()
        self.char1.db.exposure = 0
        with patch("world.underground.random.random", return_value=0.99):
            self.char1.execute_cmd("sabotage lens")
        self.assertTrue(sensor.db.active)  # device survives
        self.assertEqual(self.char1.db.exposure, tuning.SABOTAGE_FAIL_EXPOSURE)
        self.assertTrue(
            any("interference" in c for c in self._file_contents(self.char1))
        )

    def test_concealed_devices_need_a_practiced_eye(self):
        from unittest.mock import patch

        from world import tuning

        sensor = self._sensor(concealed=True)
        with patch("world.underground.random.random", return_value=0.0):
            self.char1.execute_cmd("sabotage lens")
        self.assertTrue(sensor.db.active)  # can't cut what you can't find
        self.char1.db.skills = {"observation": tuning.OBSERVE_TIER_CONCEALED}
        with patch("world.underground.random.random", return_value=0.0):
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
            (self.char1.db.influence or {}).get(tuning.UNDERGROUND), pay
        )
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
        self.char1.db.influence = {
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
        self.char1.db.influence = {tuning.UNDERGROUND: tuning.PAPERS_COST}
        self.char1.execute_cmd("papers")
        self.assertEqual(
            self.char1.db.exposure, 40 - tuning.PAPERS_RELIEF
        )
        self.assertEqual(
            (self.char1.db.influence or {}).get(tuning.UNDERGROUND), 0
        )


class TestGrades(EvenniaTest):
    """v0.12: the citizen grade — one visible ladder over existing merit."""

    def test_fresh_citizen_is_probationary(self):
        from world import grades

        self.assertEqual(grades.grade_of(self.char1), grades.GRADE_MIN)
        self.assertEqual(grades.merit(self.char1), 0)

    def test_orientation_credit_reaches_grade_5(self):
        # Endowed progress: walking the Demonstration Corridor is sized to
        # land the first grade-up minutes into play.
        from world import grades, records

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

    def test_sanctioned_influence_is_merit_but_underground_is_not(self):
        from world import grades

        self.char1.gain_influence("Ministry of Records", 10)
        self.assertEqual(grades.merit(self.char1), 10)
        self.char1.gain_influence(tuning.UNDERGROUND, 50)
        # The Grid ranks what the Grid can see.
        self.assertEqual(grades.merit(self.char1), 10)

    def test_spending_never_demotes(self):
        from world import grades

        self.char1.gain_influence("Ministry of Records", 20)
        grade_before = grades.grade_of(self.char1)
        self.char1.spend_influence("Ministry of Records", 18)
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

        self.char1.gain_influence("Ministry of Records", 12)
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

        self.assertIn("G6", self.char1.get_prompt())
        self.char1.db.oriented = True
        grades.check_reclassification(self.char1)
        self.assertIn("G5", self.char1.get_prompt())
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
