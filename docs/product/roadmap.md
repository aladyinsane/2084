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

- [ ] Sensors as discoverable objects in rooms (spottable, eventually sabotage-able)
- [ ] Watch sweep script: samples players with probability scaled by exposure — never
      omniscient, per [ADR 0004](../decisions/0004-surveillance-is-event-driven.md)
- [ ] Patrol NPCs whose density visibly tracks district alert level (the telegraph)
- [ ] **Detainment as cmdset swap**: arrested characters lose movement, gain
      `confess`/`wait`/`demand`; release loop returns them changed (exposure reset,
      standing dinged, record annotated) — stakes per [ADR 0006](../decisions/0006-conflict-is-non-lethal.md)
- [ ] NPC reactions read exposure (shopkeepers get curt when you're hot)
- [ ] New-player shallow end verified in playtest: low-visibility districts genuinely
      safe (principle 10)

## v0.3 — The record is not the truth

The memory/records thesis ([ADR 0005](../decisions/0005-records-are-objects.md)) becomes
playable.

- [ ] Record objects: observations logged by sensors/informants into per-character files
- [ ] Dossier v2: shows the *record*; what actually happened diverges
- [ ] Record services: NPC clerks who will (for standing, bribes, or favors) amend,
      redact, or fabricate entries — audit trail always kept
- [ ] First skill-by-use loops (forgery, observation, clerking) — progression per
      [ADR 0003](../decisions/0003-exposure-influence-not-xp.md)
- [ ] Asynchronous traces: your actions surface in NPC gossip and other players'
      dossiers (principle 8)

## v0.4 — Standing and paperwork

The regime as economy: influence, clearances, and bureaucracy-as-content.

- [ ] Influence ledger per faction; spent on access, services, amendments
- [ ] Clearance levels gating exits/districts (locks, not plot flags)
- [ ] EvMenu bureaucratic forms: apply, queue, get rejected for a missing stamp,
      appeal — the comedy and the horror of paperwork (principle 7)
- [ ] Work assignments: the regime gives you a *function*; performing it pays standing
      (your revocable "class," per [ADR 0002](../decisions/0002-no-race-no-class.md))
- [ ] Monitored public channels: what you say where has an exposure price

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
