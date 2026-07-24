# Architecture

How the code is arranged and why. The ADRs decide *what*; this doc records *where it
lives*. Engine background: [../research/evennia-capabilities.md](../research/evennia-capabilities.md).

## Process model

Standard Evennia: a **portal** (holds client connections) and a **server** (game logic)
as cooperating processes over an SQLite database. The server can reload without
dropping connections — live-development is the normal workflow (`evennia reload`).

## Repository layout

```
2084/
├── docs/               # the workflow: research → product → decisions → engineering
├── game/               # the Evennia game dir (created by `evennia --init game`)
│   ├── commands/       # our commands + cmdsets (incl. future detained-state cmdset)
│   ├── server/conf/    # settings.py — SERVERNAME, pinned config
│   ├── typeclasses/    # Room, Exit, Character, Scripts — where 2084 mostly lives
│   ├── world/          # batch-code world files + tuning constants
│   └── ...             # web/ overrides, evennia scaffolding
└── .venv/              # pinned Python env (evennia 6.1.x), not committed
```

## Where each system lives (v0.1, and the plan)

| System | Home | Notes |
|---|---|---|
| Room visibility | `typeclasses/rooms.py` — `GridRoom.visibility` (AttributeProperty, 0–5) | Static per room; set in batch code ([ADR 0004](../decisions/0004-surveillance-is-event-driven.md)) |
| Exposure accrual | `typeclasses/characters.py` — `Character.gain_exposure()`, called from `GridRoom.at_object_receive` on movement | Event-driven, never polled |
| Exit modifiers | `typeclasses/exits.py` — `GridExit.exposure_modifier` | Scanners/checkpoints cost extra on traverse |
| Exposure decay | `typeclasses/scripts.py` — `ExposureDecayScript`, one global script on an interval | The only timer in v0.1 |
| Prompt (`Vis:n Exp:n`) | `Character.get_prompt()` + sent on move/look | The trend-telegraph required by principle 3 |
| Dossier | `commands/dossier.py` | v0.1: a stub view over plain attributes. Replaced in v0.3 by record objects per [ADR 0005](../decisions/0005-records-are-objects.md) — the stub's calcification risk is named in that ADR |
| Skills / influence / standing | Attributes on `Character` (`skills` dict, `influence` dict, `standing` dict) | No class column anywhere, enforced by review ([ADR 0002](../decisions/0002-no-race-no-class.md)) |
| Tuning constants | `world/tuning.py` | Every gameplay number in one file, because [ADR 0004](../decisions/0004-surveillance-is-event-driven.md) promises permanent tuning — hunting magic numbers across typeclasses is the failure mode |
| The world | `world/` batch code, one file per district | Versioned, reviewable, rebuildable; grid-consistency rule from [ADR 0007](../decisions/0007-room-graph-grid-consistent.md) applies to every room added |
| Sensors | `typeclasses/objects.py` — `Sensor` | Objects, not ambience; active ones add `sensitivity` to the room's `exposure_gain()`, broken ones just hang there |
| Watch sweep | `typeclasses/scripts.py` — `WatchSweepScript` | Samples connected citizens by exposure; papers-checks the middling, detains the hot. Emits the `watchlog:` dev trace ADR 0004 owes us |
| Patrols & alert | `typeclasses/npcs.py` (`Citizen`, `WatchPatrol`) + `PatrolManagerScript`; alert level in `ServerConfig` | Density = baseline + alert; patrols keep to visibility ≥ 2 (the tunnels are unpatrolled on purpose) |
| Detainment | `commands/detention.py` (cmdset, `Replace` at prio 120) + `world/watch.py` (detain/release) | The ADR 0006 ladder; the holding cell is exitless and off-plan (documented ADR 0007 exception) |
| NPC arrival reactions | `Room.at_object_receive` → deferred `at_watched_arrival` on contents | Deferred 0.3s so reactions (incl. detainment) land after the move resolves. NB: real exits pass `move_type="traverse"`, not `"move"` — a bug the claude-account playtest caught that unit tests missed |
| Records | `typeclasses/records.py` (`Record`) + `world/records.py` (the only mutation path) | Two layers per ADR 0005: `db.content`/`db.redacted` are the mutable record; `db.audit` is the append-only truth. Subject lookup via Tags (`record_subject`) |
| Record services | `commands/civic.py` — `petition` (sanctioned, costs standing + exposure) and `forge` (unsanctioned, dead-zones only, failure is an incident) | Both routes write the audit truthfully — a forged amendment names the forger in the layer nobody in-fiction sees |
| Skill loops | `commands/civic.py` — `work`, `observe`, `forge`; helpers `improve_skill`/`skill_check` on Character | Skill-by-use per ADR 0002/0003, soft-capped in tuning |
| Async traces | sensor movement-logging in `Room._maybe_log_movement` (rate-limited); `listen` gossip over recent incidents | Principle 8: absent players stay present through their files |
| Functions | `world/functions.py` + `report`/`work` in `commands/civic.py` | The regime assigns your function from your recorded aptitudes; suspended on detention release. Not a class — a revocable stamp (ADR 0002) |
| Clearance | `clearance(N)` lockfunc in `server/conf/lockfuncs.py`; granted by Form C-1 | Access is a lock string, never a plot flag |
| Form C-1 | `world/form_c1.py` (EvMenu ceremony) over `functions.adjudicate_c1` (pure decision logic) | Ceremony and logic split so the paperwork is testable without the theatre |
| Gridwide channel | `typeclasses/channels.py` (`MonitoredChannel`) + `DEFAULT_CHANNELS` in settings | Defined in settings, not renamed post-hoc — renaming after creation silently breaks auto-subscription (playtest finding) |
| Circles | `world/circles.py` (registry in `ServerConfig`, membership as Tags, category `circle`) + `commands/circles.py` | Renamed from "cells" in v0.7 (holding-cell collision, playtest finding). No circle object exists to seize — the Ministry learns of circles only through Section C, intercepted signals, or plants |
| Section C | `commands/detention.py` (`CmdConfess` modes) + `circles.betray()` | The prisoner's dilemma at the heart of principle 6; the form knows the member count before you confirm it |
| Informants | `typeclasses/npcs.py` (`Informant`, hidden `db.loyalty`) + recruit/judge/flip in `commands/circles.py`; plant reports collected on the sweep tick | Loyalty readable only at `OBSERVE_TIER_DETAIL`; demeanor hints below that are true but inconclusive |
| Helpfiles | `world/help_entries.py` via `FILE_HELP_ENTRY_MODULES` | The core stats (visibility, exposure) and `help the grid`, in the world's voice (v0.7) |
| The map | `commands/map.py` — `GridMap`/`CmdMap` over the `ingame_map_display` contrib | Rooms render as visibility digits (v0.8); traverse-locked exits aren't drawn past, so clearance shapes the map |
| Juice | near-misses in `WatchSweepScript`/`Exit.at_traverse`; `Character.login_digest()`; `AmbienceScript` + per-room `db.ambience` | v0.8.5, from fun-and-game-feel.md: anticipation surfaced, absence reported, silence textured |
| Errands | `world/errands.py` (catalog + `check()` dispatch) + `commands/errands.py`; givers tagged `errand_giver` | v0.9: quests complete through existing verbs (the system listens, never adds quest actions); chains gate on prerequisites, nothing repeats |
| Circle benefits | `stash` in `commands/circles.py` + cache helpers in `world/circles.py` (tag category `circle_cache`); `joint_visit` errand type | v0.11: one invisible cache per circle; betrayal confiscates it, dissolution spills it; joint work completes on co-presence |
| Circle projects | `world/circle_projects.py` (registry in `ServerConfig`, same shape as `circles.py`) + `circle project` in `commands/circles.py`; hooks in `CmdSabotage`, `underground.deliver()`, `Room.at_object_receive` | ADR 0013: three stages (cumulative solo sabotage, cumulative solo couriering, synchronous two-member climax); forfeited whole by `circles.betray()`, same idiom as the stash confiscation above |
| Citizen grades | `world/grades.py` (pure merit/grade functions + `check_reclassification`); lifetime earnings in `db.influence_earned`; cached grade in `db.citizen_grade` | v0.12: one visible ladder derived from sanctioned merit only; checks fire at the choke points that change merit (`gain_influence`, errand completion, function/clearance changes, the `orients` room tag); display-only — gates nothing |
| The first hour | `commands/firsthour.py`: `CmdHelpStaged` (abridged bare `help` until `db.oriented`), `CmdNext` (state-read advisory), `CmdGrade`; FORM 1-A welcome in `Character.at_post_puppet` (`db.welcomed`) | v0.13: sequencing, never locking — `help all` is always the full index; `next` prefers the safe chain by catalog order |
| No-match handling | `commands/nomatch.py`: `CmdNoMatch` keyed `__nomatch_command` — direction answers, instinct-verb table, whitelist-only suggestions | v0.14: replaces Evennia's default suggester, which leaked chalk verbs (`sabotage`, `stash`) and engine verbs (`charcreate`) to wrong guesses |
| Gear | `typeclasses/gear.py` (slots, `worn_kind`) + `commands/gear.py` (catalog, list/buy/wear/remove); vendors tagged `vendor` | v0.10: effects dispatch by `gear_kind` at existing hook sites (room entry, work pay, decay tick, seizure); every item a trade, never an upgrade |
| Assemblies | `typeclasses/scripts.py` — `AssemblyScript` (announce tick, roll-call tick, rest) | Absence-is-data: the roll writes incidents no sensor could; detainees excused |
| Dead-zone truth | `Room.is_dead_zone()` — visibility 0 **and** zero exposure gain | Single source of truth for the sweep, `forge`, and the underground verbs; what makes the Bolt-Hole honeypot honest (concealed live sensor ⇒ not a dead zone) |
| The underground | `world/underground.py` + `commands/underground.py` (`sabotage`/`carry`/`deliver`/`papers`) | ADR 0008's grind loops; both pay the `UNDERGROUND` ledger, which the dossier deliberately cannot see (`UNSANCTIONED_SKILLS`/`_FACTIONS` in tuning) |
| Maintenance crew | `typeclasses/scripts.py` — `MaintenanceScript` | Repairs the sabotage backlog oldest-first; only repairs *sabotage* — the alley screen predates the backlog and stays broken |
| Contraband seizure | `underground.seize_contraband`, called from papers checks, `watch.detain`, and scanner-gate `at_traverse` | The courier run's "death"; the Watch never hunts couriers, it just finds them through systems that already exist |

## Data-model conventions

- **Attributes for state, Tags for membership.** Exposure/skills/influence are
  Attributes; district, faction, and flag-type facts ("wanted") are Tags — Tags are the
  fast bulk-query path ("everyone wanted in Market Belt").
- **Typeclasses stay thin.** Mechanics that span objects (the sweep, decay) live in
  scripts; typeclass methods are the verbs on one object's own state.
- **No gameplay logic in the database layer.** The DB persists; Python decides.
- **Every number is in `world/tuning.py`.** No literals in mechanics code.

## Testing

Evennia ships a test framework (`evennia test --settings settings.py .` from the game
dir) with `EvenniaTest` base classes that stand up in-memory objects. v0.1 tests cover
the exposure loop (accrual on movement by visibility, exit modifiers, decay, floor at
zero) — the mechanics; tone is playtested, not unit-tested.

## Performance posture

MUD-scale (tens of players) on event-driven design has no hot paths; we deliberately do
not optimize ahead of measurement. The known future pressure points, both accepted in
ADRs: record-object growth (ADR 0005) and tuning-script frequency (ADR 0004).
