# ADR 0006 — Conflict is non-lethal; there is no death and no lethal PvP

- **Status:** Accepted
- **Date:** 2026-07-17

## Context

MUD tradition says conflict resolution ends in death and corpse retrieval. Our source
material says the regime doesn't make martyrs — it converts, hollows out, and *then*
disposes (M5). Death as a game-over-and-respawn loop would be both tonally wrong and
mechanically weaker than what the setting offers instead. Prior drafts already leaned
this way ("non-lethal by default"); this ADR removes the "by default."

## Decision

- **No character death as a game outcome.** Not from NPCs, not from players, not from
  the environment.
- The escalation ladder instead: exposure → questioning → **detainment** (a cmdset
  swap: movement gone, `confess`/`wait`/`demand` in its place) → interrogation →
  release *changed* (standing dinged, record annotated, possibly memories revised per
  ADR 0005) → and at the far end, **unpersoning** — the record-erasure arc parked in
  [future-features.md](../product/future-features.md).
- **Physical confrontation exists** (subdue, restrain, flee) and resolves in seconds
  with those same non-lethal outcomes. It is deliberately not deep; depth lives in the
  social and stealth systems.
- **PvP is social**: denunciation, forgery, informing, honeypots. No player can be
  killed by another; any player can be *ruined* by one — with the audit trail (ADR
  0005) as the long-road answer.

## Consequences

**Good**

- Stakes get *worse*, not softer: what the regime does to you is scarier than respawn,
  and it happens on-screen to a character who continues existing (principle 5's test).
- Detention-as-cmdset makes the worst moment playable instead of a death screen — the
  interrogation is a scene, not a stat check.
- No death spiral for new players; recoverability is structural (principle 10).

**Bad / accepted costs**

- **We will lose the hack-and-slash audience.** Players arriving from DIKU muscle
  memory (`kill guard`) will bounce off. Accepted openly — anti-principle 1. The
  listing copy should say what we are so they don't waste an evening finding out.
- **Social PvP is still PvP**, and ruin-by-paperwork can grief harder than ganking.
  The mitigation burden lands on ADR 0005's costs-and-appeals machinery, and it must
  ship *with* the tools, not after them.
- **"No death ever" removes an authored tool.** Some stories want a corpse. If a
  narrative death is ever essential, it's an authored, consented story beat — never a
  system outcome — and doing it well will be hard within this ADR. We accept the
  constraint.
- **Detainment must be interesting or it's a timeout.** A boring jail is worse than a
  clean death; the v0.2 detainment loop carries a real content burden.

## Revisit when

- Playtests show confrontation feels weightless rather than terse — the fix is better
  consequences, not lethality; but if consequence-tuning fails twice, this ADR gets a
  successor rather than quiet erosion.
