# Roadmap

Sequenced by "what proves the thesis," not by "what's easy." The thesis: *a surveillance
state is a better MUD antagonist than a bestiary.* Each version is a playable claim.

## v0.1 — The spine (current)

Walkable world + the surveillance loop's skeleton: move through the Grid, be seen,
watch your exposure climb and decay, read your own dossier. No Watch consequences yet —
v0.1 proves the *feeling* of being watched is worth building on before anything punishes.

- [x] Docs workflow: research → principles → ADRs ([ADR 0001](../decisions/0001-evennia-engine.md)–[0007](../decisions/0007-room-graph-grid-consistent.md))
- [x] Evennia project scaffold, pinned venv, runs on Windows
- [x] Classless character: skills/standing/exposure as attributes, no class column
      anywhere ([ADR 0002](../decisions/0002-no-race-no-class.md))
- [x] Rooms with visibility levels 0–5; exits with exposure modifiers; movement through
      watched space accrues exposure ([ADR 0004](../decisions/0004-surveillance-is-event-driven.md))
- [x] Exposure decay on a global script tick
- [x] Prompt shows room visibility and current exposure (`Vis:3 Exp:12`)
- [x] `dossier` command — what the regime's record says about you (the seed of
      [ADR 0005](../decisions/0005-records-are-objects.md)'s record-vs-truth split)
- [x] Starting district: a small, grid-consistent slice of the Grid spanning the
      visibility extremes (checkpoint plaza → tenements → market → tunnels), built from
      versioned batch code ([ADR 0007](../decisions/0007-room-graph-grid-consistent.md))
- [x] Basic tests (exposure accrual, decay, dossier)

## v0.2 — Being watched has teeth

The dread loop closes: consequences arrive, telegraphed in trend, uncertain in timing
(principle 3).

- [x] Sensors as discoverable objects in rooms (spottable; active ones add exposure,
      the broken one in Neon Alley adds nothing — sabotage-able comes later)
- [x] Watch sweep script: samples players with probability scaled by exposure — never
      omniscient, per [ADR 0004](../decisions/0004-surveillance-is-event-driven.md).
      Ships with the ADR's promised dev-facing `watchlog:` trace; verification
      watched a sweep *miss* at roll 0.76 before catching at roll 0.17
- [x] Patrol NPCs whose density visibly tracks district alert level (the telegraph):
      alert rises per detention, decays over quiet sweeps; patrols = baseline + alert
- [x] **Detainment as cmdset swap**: arrested characters lose movement, gain
      `confess`/`wait`/`demand`; release loop returns them changed (exposure reset,
      record annotated) — stakes per [ADR 0006](../decisions/0006-conflict-is-non-lethal.md).
      Verified end-to-end from the player side: swept at Exp 60, celled, `demand`
      resets the wait clock, `confess` releases with the file three incidents longer
- [x] NPC reactions read exposure (the ration clerk's three tiers; patrol visor-tracks
      the noticed and detains the hot on sight)
- [x] Connection screen and all Watch prose pass principle 9's no-magic-missile rule
      (the login terminal is the Ministry's, not the engine's) ← added mid-version
      from the 3M field-research finding
- [x] New-player shallow end verified in **human** playtest (principle 10) —
      happened 2026-07-19 ([findings](../research/playtest-2026-07-19-first-human.md)).
      Verdict: mechanically safe, *experientially* rough — the confusion taxes
      (command overwhelm, unexplained stats, naming collisions) and a flat
      moment-to-moment loop ("a bit dull") spawned v0.7–v0.11 below

## v0.3 — The record is not the truth

The memory/records thesis ([ADR 0005](../decisions/0005-records-are-objects.md)) becomes
playable.

- [x] Record objects: incidents and sensor movement-logs as typeclassed objects, each
      carrying origin/author/subject/content and an **append-only audit trail** every
      mutation writes to first. Sensors log citizens above notice exposure, rate-limited
      (ADR 0005's growth concern)
- [x] Dossier v2: a view over the record layer. Redacted entries vanish but keep their
      numbers — the gap in the numbering is the visible seam
- [x] Record services: the archivist at the Annex amends (4) and redacts (8) for
      standing with the Ministry of Records, earned by `work`; using the service is
      itself noted (+10 exposure). Audit trail always kept
- [x] First skill-by-use loops: clerking (`work`), observation (`observe` — tiered
      readout of a room's devices), forgery (`forge` — rewrite your own file off the
      books, only in visibility-0 dead zones; failure *is* an incident)
- [x] Asynchronous traces, first pass: `listen` in the ration queue surfaces recent
      unredacted incidents about *other* citizens; sensor logs put your movements in
      your file. Richer ambient gossip (NPCs volunteering names unprompted) still to come
- [x] Dead zones are dead ← added mid-version from in-game verification: the sweep
      cannot select someone in a visibility-0 room. Hiding works; exposure barely
      decays; you have to come up sometime

## v0.3.5 — The Orientation Wing (pulled from the parking lot 2026-07-18)

Tutorial-as-architecture, straight from the 3M field research: rooms whose
descriptions are the manual.

- [x] Five-room lattice east of the Assignment Hall (grid-consistent, in the world's
      voice): prompt & exposure basics → the Watch → your file → civic life → a
      **Demonstration Corridor** at Vis 5 whose placard tells you to watch your Exp
      rise as it rises (+5 on entry — teaching by mechanism, not by text)
- [x] The stencilled arrow in the Hall: ATTENDANCE IS VOLUNTARY. ATTENDANCE IS NOTED.
- [x] The orientation clerk (exposure-tiered greetings, per the Citizen system)
- [x] The unsanctioned curriculum: the chalk marks in Tunnel B teach what the Ministry
      won't — dead zones, `forge`, and what a form can do
- [x] The ADR 0007 lint, automated at last: a build test that verifies every compass
      exit has a true reciprocal and the holding cell stays exitless — plus a
      described-devices-exist check (principle 9's in-world corollary)

## v0.4 — Standing and paperwork

The regime as economy: influence, clearances, and bureaucracy-as-content.

- [x] Influence ledger per faction: three ministries now pay standing (Records, Order,
      Commerce), and Records standing is the coin of petitions and Form C-1
- [x] Clearance levels gating exits (locks, not plot flags): a `clearance(N)` lockfunc,
      and the Spire Lobby behind a C-1 gate whose refusal is a palm to the sternum
- [x] EvMenu bureaucratic form: **Form C-1, Application for Elevated Clearance** —
      purposes that are not different, a declaration you must affirm ("my file is
      accurate; it has always been accurate"), a fee retained on rejection, and a
      missing-stamp rejection (Form 77: Employment Verification). The systems chain on
      purpose: a dirty file fails the references check, and the fix is v0.3's record
      laundering. No formal appeal path yet — reapplication after improving one's
      circumstances *is* the appeal, as the archivist hints
- [x] Work assignments: `report`, and the regime reads your recorded aptitudes and
      stamps a *function* on you (Clerk / Auditor / Steward — your skills are your
      application whether you meant them as one). Working your own post pays triple;
      detention **suspends your function** on release — [ADR 0002](../decisions/0002-no-race-no-class.md)'s
      revocable class, demonstrated
- [x] Monitored public channel: `gridwide`, defined in settings so citizens are
      auto-subscribed at registration (the playtest caught the rename-after-creation
      approach silently unsubscribing everyone). Speaking on it costs exposure:
      "your words join the public record"

## v0.5 — Trust

The multiplayer thesis: betrayal outguns everything (principle 6).

- [x] Cells: formed, joined, and left only where nothing watches (`cell`,
      taught by the chalk, not the Ministry); membership is a tag with no
      object to seize; `signal` passes word cell-wide — safe from quiet
      places, interceptable from watched ones. The collective risk is
      **Section C**: a detained member's confession form arrives with
      exactly as many blank lines as they have comrades — `confess names`
      walks free on everyone else's file (+25 exposure each, incident
      recorded), `confess alone` keeps faith and leaves on a shorter leash.
      Verified two-player (claude + julia): the full arc, tip → betrayal →
      julia alone in the kettle circle with two incidents she didn't earn
- [x] Informant NPCs: `recruit`/`sound`/`flip`. Two in Neon Alley; one is
      the Ministry's, and *which* is only readable at real observation
      skill. Street informants tip the cell when a member is taken; plants
      file "Reported by a source" incidents from inside on a cooldown.
      Flipping a plant is a Commerce transaction, and requires being able
      to read them at all
- [x] Scheduled world events where absence is data (M8): civic assemblies
      announce over every loudspeaker, then take the roll at Unity Plaza.
      Present: exposure relief, attendance on file. Absent — *anywhere*,
      including dead zones: an incident, because the list sees what the
      sensors can't. Detainees excused; the Ministry knows where they are
- [x] First honeypot: the Bolt-Hole off Tunnel B, chalk-marked safe,
      Vis 0 — and lying. A concealed live sensor (view-locked; the playtest
      caught it standing in plain sight under "You see:") means the sweep
      reaches in, `forge` refuses without saying why, and movements are
      logged. Fair-warning layers: the too-neat blankets, the chalk's own
      "ask yourself who," the +1 exposure tick at Vis 0, and — if you run
      hot enough to be logged — your own dossier names the room
- [ ] Not yet from this version's ambitions: cell *benefits* beyond
      communication (shared stashes, joint operations) — cells currently
      pool risk more than they pool power. Deliberate: trust must cost
      before it pays, but the pay side is v0.6+ material

## v0.6 — The grind ([ADR 0008](../decisions/0008-grind-loops-sabotage-and-couriering.md))

The mob-grind's shape without the corpse: Lauren picked options 1+2 off the
grind shelf ([research](../research/grind-loops-without-killing.md)). Both loops
pay **the underground** — the first non-Ministry ledger.

- [x] Sensor sabotage circuit: `sabotage <device>` skill checks against live
      devices; failure is an incident + heat (verified live: "the housing
      gives, then bites back", +12 Exp, fault report filed); the maintenance
      crew repairs oldest-first on a timer so the circuit respawns — and only
      repairs *sabotage*: the alley screen predates the backlog and stays
      broken, because nobody files the form. Concealed devices targetable
      only at a practiced observation skill (the honeypot can be blinded —
      temporarily, expensively, gloriously)
- [x] Courier runs: the broker in the ration queue, four destination tiers
      priced by visibility, parcels as real objects, seizure via the systems
      that already exist (papers checks, detainment processing, scanner
      gates). Verified live: a gate run that paid 8+4 jackpot, and a second
      one where gloved hands found the parcel on the second pat — and the
      exposure from *that* fed the patrol detention two rooms later. The
      systems chain without being told to
- [x] The underground's first sink: clean `papers` (standing → exposure
      relief) so the loop closes in one session. Playtest caught the dossier
      leaking the underground's ledger and the off-the-books aptitudes
      (including `forgery`, leaking since v0.3) — the Ministry's file now
      contains only what the Ministry could have observed
- [x] Curriculum audit (contributing.md rule 9, new this version): assemblies
      added to the Wing's civic placard; sabotage/carry/papers added to the
      chalk — and the audit itself caught that v0.5 never chalked the
      informant verbs (recruit/sound/flip). Now it does

## The 2026-07-19 batch (from the [first human playtest](../research/playtest-2026-07-19-first-human.md))

Sequenced legibility-first: fix what confuses before building what excites,
because renames get more expensive with every feature built on top of them,
and because confusion is a fun-tax on everything downstream. One PR per
version; merge on green tests per Lauren's standing instruction.

## v0.7 — Legibility

The playtest-response version. No new systems; the existing ones become
readable.

- [ ] Prompt spells out `Exposure` (Exp reads as experience points to every
      MUD veteran)
- [ ] Helpfiles for the two core stats (visibility, exposure) and a
      `help`-topic pass over the custom verbs
- [ ] Command-overwhelm audit: an honest doc weighing our ~15 custom verbs
      against MUD conventions, folding or renaming where cheap
- [ ] Rename: `sound` → `judge`; rename: player cells → **circles**
      (`circle form/invite/join/leave`) — the holding cell keeps the word
- [ ] Display fixes: NPC names capitalized in listings/poses; "a the chalk
      marks" article stacking
- [ ] Detention onboarding: `help` works in the holding cell, and the first
      time the door closes, the room tells you your verbs

## v0.8 — The map (left the parking lot)

The ASCII map, deferred since v0.1 on purpose (ADR 0007 kept it cheap).
Disorientation stopped being tonally useful and started being friction.
Default choice per the parking lot: the `ingame_map_display` contrib over
our grid-consistent room graph, presented in-fiction.

- [ ] `map` command rendering the local area from the room/exit graph
- [ ] In-fiction framing (a citizen's mental map / a contraband sketch, not
      a Ministry handout)

## v0.9 — Errands (the quest system)

The broker proved the shape; generalize it so any tagged NPC can hand out
work with a destination, a condition, and a payout.

- [ ] Quest framework: offer/accept/complete/abandon on any NPC, quest state
      on the character, rewards in faction standing (either kind)
- [ ] Convert courier runs to ride the framework (the broker becomes the
      first quest-giver rather than a special case)
- [ ] 3–5 launch quests spread across sanctioned (Ministry work orders) and
      unsanctioned (underground favors) givers

## v0.10 — Implants (equipment)

3M's implant catalog ([field research](../research/third-millennium-mud.md)),
inverted for the Grid: the state issues what it can monitor; the black market
sells what it can't.

- [ ] Wear/remove slots; state-issued equipment (function badges, monitor
      cuffs) with benefits *and* surveillance costs
- [ ] Black-market gear (dampeners, dead-man pockets) with exposure benefits
      and seizure risk
- [ ] Principle 9 gate: every item passes the no-magic-missile rule

## v0.11 — Circle benefits

The pay side of trust (owed since ADR 0008 named the one-sink economy).

- [ ] Shared stash (a circle-locked cache in a dead zone)
- [ ] Joint operations: at least one errand that requires two circle members
      acting together
- [ ] Underground-ledger sinks sized against what the grind now pays

## Cross-cutting for the batch

- The **fun research pass** (game feel, incentive gradients, "why dull?")
  lands before v0.9 so quests and implants inherit its answers
- Curriculum audit per version (contributing rule 9), as always

## Later / undecided

The parking lot, including the **ASCII map**: [future-features.md](future-features.md).

## Cross-cutting, always

- World stays grid-consistent — every batch-built room passes the ADR 0007 discipline
- Every loop single-player-viable before it ships (principle 8's test)
- Every version audits the curriculum before merge: new sanctioned verbs reach the
  Orientation Wing placards, new unsanctioned ones reach the Tunnel B chalk
  (contributing.md rule 9)
- Playtest gate between versions: the named risks in
  [future-features.md](future-features.md#known-risks-in-shipped-features) get checked
  against real sessions, not intuition
