"""
Scripts

Scripts are powerful jacks-of-all-trades. They have no in-game
existence and can be used to represent persistent game systems in some
circumstances. Scripts can also have a time component that allows them
to "fire" regularly or a limited number of times.

There is generally no "tree" of Scripts inheriting from each other.
Rather, each script tends to inherit from the base Script class and
just overloads its hooks to have it perform its function.

"""

from evennia.scripts.scripts import DefaultScript


class Script(DefaultScript):
    """
    This is the base TypeClass for all Scripts. Scripts describe
    all entities/systems without a physical existence in the game world
    that require database storage (like an economic system or
    combat tracker). They
    can also have a timer/ticker component.

    A script type is customized by redefining some or all of its hook
    methods and variables.

    * available properties (check docs for full listing, this could be
      outdated).

     key (string) - name of object
     name (string)- same as key
     aliases (list of strings) - aliases to the object. Will be saved
              to database as AliasDB entries but returned as strings.
     dbref (int, read-only) - unique #id-number. Also "id" can be used.
     date_created (string) - time stamp of object creation
     permissions (list of strings) - list of permission strings

     desc (string)      - optional description of script, shown in listings
     obj (Object)       - optional object that this script is connected to
                          and acts on (set automatically by obj.scripts.add())
     interval (int)     - how often script should run, in seconds. <0 turns
                          off ticker
     start_delay (bool) - if the script should start repeating right away or
                          wait self.interval seconds
     repeats (int)      - how many times the script should repeat before
                          stopping. 0 means infinite repeats
     persistent (bool)  - if script should survive a server shutdown or not
     is_active (bool)   - if script is currently running

    * Handlers

     locks - lock-handler: use locks.add() to add new lock strings
     db - attribute-handler: store/retrieve database attributes on this
                        self.db.myattr=val, val=self.db.myattr
     ndb - non-persistent attribute handler: same as db but does not
                        create a database entry when storing data

    * Helper methods

     create(key, **kwargs)
     start() - start script (this usually happens automatically at creation
               and obj.script.add() etc)
     stop()  - stop script, and delete it
     pause() - put the script on hold, until unpause() is called. If script
               is persistent, the pause state will survive a shutdown.
     unpause() - restart a previously paused script. The script will continue
                 from the paused timer (but at_start() will be called).
     time_until_next_repeat() - if a timed script (interval>0), returns time
                 until next tick

    * Hook methods (should also include self as the first argument):

     at_script_creation() - called only once, when an object of this
                            class is first created.
     is_valid() - is called to check if the script is valid to be running
                  at the current time. If is_valid() returns False, the running
                  script is stopped and removed from the game. You can use this
                  to check state changes (i.e. an script tracking some combat
                  stats at regular intervals is only valid to run while there is
                  actual combat going on).
      at_start() - Called every time the script is started, which for persistent
                  scripts is at least once every server start. Note that this is
                  unaffected by self.delay_start, which only delays the first
                  call to at_repeat().
      at_repeat() - Called every self.interval seconds. It will be called
                  immediately upon launch unless self.delay_start is True, which
                  will delay the first call of this method by self.interval
                  seconds. If self.interval==0, this method will never
                  be called.
      at_pause()
      at_stop() - Called as the script object is stopped and is about to be
                  removed from the game, e.g. because is_valid() returned False.
      at_script_delete()
      at_server_reload() - Called when server reloads. Can be used to
                  save temporary variables you want should survive a reload.
      at_server_shutdown() - called at a full server shutdown.
      at_server_start()

    """

    pass


class ExposureDecayScript(Script):
    """
    The only timer in v0.1: everyone's exposure drifts slowly down.

    Global, persistent, event-granular — the surveillance model never polls
    finer than this tick (ADR 0004).
    """

    def at_script_creation(self):
        from world import tuning

        self.key = "exposure_decay"
        self.desc = "Slowly decays citizen exposure."
        self.interval = tuning.EXPOSURE_DECAY_INTERVAL
        self.persistent = True

    def at_repeat(self):
        from world import tuning

        from .characters import Character

        for char in Character.objects.all():
            exposure = char.db.exposure or 0
            if exposure > 0:
                char.db.exposure = max(0, exposure - tuning.EXPOSURE_DECAY_AMOUNT)


class WatchSweepScript(Script):
    """
    The Watch samples the population (ADR 0004: probability scales with
    exposure; below the shallow-end floor you are never sampled at all).
    High exposure means detainment; middling exposure means a papers check —
    a sanctioned interaction, which *lowers* exposure. Quiet ticks let the
    district alert level subside.
    """

    def at_script_creation(self):
        from world import tuning

        self.key = "watch_sweep"
        self.desc = "Periodic Watch sampling of the population."
        self.interval = tuning.WATCH_SWEEP_INTERVAL
        self.persistent = True

    # Near-miss telegraphy (v0.8.5): a sweep roll that MISSES is dread we
    # already computed — the player should feel the machine consider them
    # and move on (fun-and-game-feel.md, dullness #2).
    NEAR_MISSES = [
        "|yA visor across the street holds on you a half-second too "
        "long,|n then moves on.",
        "|ySomewhere nearby, a scanner's idle hum changes pitch,|n and "
        "then decides it was nothing.",
        "|yA grey van slows as it passes you.|n It does not stop. This "
        "time it does not stop.",
        "|yYou have the sudden, specific feeling of a photograph being "
        "compared to your face.|n The feeling passes.",
    ]

    def at_repeat(self):
        import random

        from evennia.utils import logger

        from world import tuning, watch

        from .characters import Character

        detained_anyone = False
        for char in Character.objects.all():
            if not char.has_account or not char.sessions.count():
                continue
            if watch.is_detained(char):
                continue
            # Dead zones are dead: the sweep cannot select someone the Grid
            # cannot currently see (in-game verification caught the sweep
            # reaching into Tunnel B, where the fiction says nothing does).
            # Hiding works — but exposure barely decays, and you have to
            # come up sometime. NB: *truly* dead (v0.5) — a visibility-0
            # room with a live device hidden in it shelters nobody.
            loc = char.location
            if loc and getattr(loc, "is_dead_zone", lambda: False)():
                continue
            exposure = char.db.exposure or 0
            if exposure < tuning.SWEEP_MIN_EXPOSURE:
                continue
            span = tuning.EXPOSURE_MAX - tuning.SWEEP_MIN_EXPOSURE
            chance = (
                (exposure - tuning.SWEEP_MIN_EXPOSURE) / span
            ) * tuning.SWEEP_MAX_CHANCE
            roll = random.random()
            logger.log_info(
                f"watchlog: sweep {char.key} exposure={exposure} "
                f"chance={chance:.2f} roll={roll:.2f}"
            )
            if roll >= chance:
                char.msg(random.choice(self.NEAR_MISSES))
                continue
            if exposure >= tuning.DETAIN_THRESHOLD:
                watch.detain(char, reason="selected in a routine sweep")
                detained_anyone = True
            else:
                self.papers_check(char)

        if detained_anyone:
            self.db.quiet_ticks = 0
        else:
            quiet = (self.db.quiet_ticks or 0) + 1
            self.db.quiet_ticks = quiet
            if quiet >= 5:
                self.db.quiet_ticks = 0
                watch.set_alert(watch.get_alert() - 1)

        # The sweep also collects from its sources (v0.5): recruited
        # Ministry plants file on the circles that trusted them.
        from world import circles

        circles.collect_informant_reports()

    @staticmethod
    def papers_check(char):
        from world import tuning, underground, watch

        # A pat-down finds what a wrist scan wouldn't (v0.6): carrying
        # contraband turns a routine check into a much worse afternoon —
        # and forfeits the cleared-is-an-alibi relief.
        if underground.seize_contraband(char, found_by="a papers check"):
            char.send_prompt()
            return
        char.msg(
            "|yAn officer of the Watch angles across your path and stops you "
            "with two fingers.|n Papers. You produce them. A scanner passes "
            "over your wrist, hums, and finds you insufficiently interesting."
            "\n|=mBeing checked and cleared is, itself, a kind of alibi.|n"
        )
        if char.location:
            char.location.msg_contents(
                f"An officer of the Watch stops {char.key}, scans their papers, "
                "and moves on.",
                exclude=(char,),
            )
        char.gain_exposure(-tuning.PAPERS_CHECK_RELIEF)
        watch.add_record_note(char, "Papers checked in the street; cleared.")
        char.send_prompt()


class AssemblyScript(Script):
    """
    Scheduled civic assemblies (v0.5, mechanism M8): the Grid periodically
    requires everyone somewhere at once, and then reads the room. Presence
    is rewarded the way cooperation always is; absence is *data* — the one
    thing surveillance can collect without seeing you at all. Hiding in a
    dead zone during roll call produces an incident precisely because
    nothing saw you: the list did.

    State machine on a fixed tick: rest for ASSEMBLY_REST_TICKS, announce,
    then take attendance one tick later.
    """

    def at_script_creation(self):
        from world import tuning

        self.key = "assembly"
        self.desc = "Announces civic assemblies and takes attendance."
        self.interval = tuning.ASSEMBLY_TICK
        self.persistent = True
        self.db.rest = tuning.ASSEMBLY_REST_TICKS
        self.db.announced = False

    @staticmethod
    def _assembly_point():
        from evennia.utils.search import search_object_by_tag

        rooms = search_object_by_tag("assembly_point", category="grid")
        return rooms[0] if rooms else None

    @staticmethod
    def _citizens():
        from .characters import Character

        return [
            char
            for char in Character.objects.all()
            if char.has_account and char.sessions.count()
        ]

    def at_repeat(self):
        from evennia.utils import logger

        from world import tuning, watch

        point = self._assembly_point()
        if not point:
            return

        if not self.db.announced:
            rest = (self.db.rest or 0) - 1
            self.db.rest = rest
            if rest > 0:
                return
            self.db.announced = True
            minutes = max(1, tuning.ASSEMBLY_TICK // 60)
            for char in self._citizens():
                char.msg(
                    "|yEvery loudspeaker in Sector 9 clears its throat at "
                    "once.|n\n\"CITIZENS. A CIVIC ASSEMBLY CONVENES AT "
                    f"{point.key.upper()} IN {minutes} MINUTE"
                    f"{'S' if minutes != 1 else ''}. ATTENDANCE IS THE "
                    "GRID'S PLEASURE. THE ROLL IS THE GRID'S MEMORY.\""
                )
            logger.log_info("watchlog: assembly announced")
            return

        # Roll call.
        self.db.announced = False
        self.db.rest = tuning.ASSEMBLY_REST_TICKS
        from world import records

        present, absent = [], []
        for char in self._citizens():
            if watch.is_detained(char):
                continue  # the Ministry knows exactly where you are
            (present if char.location == point else absent).append(char)

        point.msg_contents(
            "The loudspeakers deliver four minutes of production figures "
            "and one minute of gratitude. Somewhere behind the numbers, "
            "a roll completes itself."
        )
        for char in present:
            records.add_record(
                char,
                "Attended civic assembly",
                author="Office of Assemblies",
                kind="observation",
            )
            char.gain_exposure(-tuning.ASSEMBLY_ATTEND_RELIEF)
            char.msg(
                "|=mYour presence is recorded. Being countable is the "
                "cheapest virtue the Grid sells.|n"
            )
            char.send_prompt()
        for char in absent:
            records.add_record(
                char,
                "Absent from mandatory civic assembly",
                author="Office of Assemblies",
                kind="incident",
            )
            char.gain_exposure(tuning.ASSEMBLY_ABSENT_EXPOSURE)
            char.msg(
                "|yFar away, a roll is read, and a silence occurs where "
                "your name is.|n Absence is the one thing the Grid can "
                "see anywhere."
            )
            char.send_prompt()
        logger.log_info(
            f"watchlog: assembly roll — {len(present)} present, "
            f"{len(absent)} absent"
        )


class AmbienceScript(Script):
    """
    Texture (v0.8.5, fun-and-game-feel.md dullness #3): the world speaks
    between events. Occupied rooms murmur on a slow, rate-limited tick —
    loudspeakers, queue shuffles, distant vans; dead zones get their
    silence described. Rooms opt in via `db.ambience` (a list of lines,
    set by the world build); rooms without get quiet defaults by
    visibility.
    """

    DEFAULT_WATCHED = [
        "A loudspeaker somewhere clears its throat, reconsiders, and "
        "resumes the production figures.",
        "A grey van passes at the speed of a vehicle with nowhere "
        "particular to be, which is a speed the Grid practices.",
        "High up, a lens turns through its arc with a sound like a "
        "patient tongue-click.",
    ]
    DEFAULT_DARK = [
        "Water ticks somewhere in the dark, keeping its own census.",
        "The silence here has texture: pipes, breath, distance. Nothing "
        "in it is listening. You check anyway.",
    ]

    def at_script_creation(self):
        from world import tuning

        self.key = "ambience"
        self.desc = "Gives occupied rooms their murmur."
        self.interval = tuning.AMBIENCE_INTERVAL
        self.persistent = True

    def at_repeat(self):
        import random
        import time

        from world import tuning

        from .characters import Character

        now = time.time()
        rooms = {
            char.location
            for char in Character.objects.all()
            if char.has_account and char.sessions.count() and char.location
        }
        for room in rooms:
            if random.random() >= tuning.AMBIENCE_CHANCE:
                continue
            if now - (room.db.last_ambience or 0) < tuning.AMBIENCE_ROOM_COOLDOWN:
                continue
            lines = room.db.ambience
            if not lines:
                lines = (
                    self.DEFAULT_DARK
                    if getattr(room, "visibility", 0) == 0
                    else self.DEFAULT_WATCHED
                )
            room.db.last_ambience = now
            room.msg_contents(f"|=m{random.choice(lines)}|n")


class MaintenanceScript(Script):
    """
    The maintenance crew (v0.6, ADR 0008): works the sabotage backlog
    oldest-first, one device per interval. This is what makes sabotage a
    circuit instead of a heist — the map respawns. Note the crew only
    repairs *sabotage*: the alley watchscreen predates the backlog, and
    nobody has filed the form.
    """

    def at_script_creation(self):
        from world import tuning

        self.key = "maintenance"
        self.desc = "Repairs sabotaged devices, oldest first."
        self.interval = tuning.REPAIR_INTERVAL
        self.persistent = True

    def at_repeat(self):
        from evennia.utils import logger

        from world import underground

        sensor = underground.oldest_sabotaged_sensor()
        if not sensor:
            return
        sensor.db.active = True
        sensor.db.sabotaged_at = None
        if sensor.location:
            sensor.location.msg_contents(
                "A maintenance crew in Ministry coveralls arrives, replaces "
                f"a component in {sensor.key} with six practiced motions, "
                "and leaves without looking at anyone. The diode comes back "
                "on like an opinion."
            )
        logger.log_info(f"watchlog: maintenance repaired {sensor.key}")


class PatrolManagerScript(Script):
    """
    Keeps patrol density matched to the district alert level
    (PATROL_BASELINE + alert, so more detentions visibly mean more grey
    uniforms — the telegraph), and walks each patrol one step.
    """

    def at_script_creation(self):
        from world import tuning

        self.key = "patrol_manager"
        self.desc = "Spawns, culls and walks Watch patrols."
        self.interval = tuning.PATROL_MOVE_INTERVAL
        self.persistent = True

    def at_repeat(self):
        from evennia import create_object
        from evennia.utils.search import search_object_by_tag

        from world import tuning, watch

        from .npcs import WatchPatrol

        patrols = list(WatchPatrol.objects.all())
        desired = tuning.PATROL_BASELINE + watch.get_alert()

        spawn_points = search_object_by_tag("patrol_spawn", category="grid")
        while len(patrols) < desired and spawn_points:
            patrol = create_object(
                WatchPatrol, key="an officer of the Watch", location=spawn_points[0]
            )
            spawn_points[0].msg_contents(
                "A Watch officer steps off the Spire transit line and falls "
                "into an easy patrol pace."
            )
            patrols.append(patrol)
        while len(patrols) > max(desired, tuning.PATROL_BASELINE):
            extra = patrols.pop()
            if extra.location:
                extra.location.msg_contents(
                    f"{extra.key} receives something on the visor feed, turns, "
                    "and is gone toward the Spire."
                )
            extra.delete()

        for patrol in patrols:
            patrol.patrol_step()
