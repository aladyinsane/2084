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
