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
- [ ] New-player shallow end verified in **human** playtest (principle 10). The
      mechanical half is proven — sweeps skip exposure < 20 by construction, unit
      test walks 100 ticks untouched — but "genuinely safe" is a feeling, and
      feelings need a playtester who isn't the developer

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

- [ ] Cells: small player groups with shared secrets and collective risk
- [ ] Informant NPCs; recruitable, flippable, plantable
- [ ] Scheduled world events where absence is data (assemblies, audits — M8)
- [ ] First honeypot content: a safehouse that might not be

## Later / undecided

The parking lot, including the **ASCII map**: [future-features.md](future-features.md).

## Cross-cutting, always

- World stays grid-consistent — every batch-built room passes the ADR 0007 discipline
- Every loop single-player-viable before it ships (principle 8's test)
- Playtest gate between versions: the named risks in
  [future-features.md](future-features.md#known-risks-in-shipped-features) get checked
  against real sessions, not intuition
