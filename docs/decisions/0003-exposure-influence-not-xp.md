# ADR 0003 — Exposure and Influence replace XP and levels

- **Status:** Accepted
- **Date:** 2026-07-17

## Context

XP-and-levels assumes the world is a resource to harvest; our world is an antagonist to
survive (principle 1). But progression is retention — replacing XP with *nothing* is
fatal; the replacement must be visible, attributable, and mostly-upward early
([mud-design-landscape.md §3](../research/mud-design-landscape.md)).

## Decision

Three numbers carry progression, none of them XP:

- **Skills** (per-skill, 0–100): rise through use, slowly and automatically. The
  "number goes up" comfort, attached to what you actually do (ADR 0002).
- **Influence** (per-faction ledger): earned by being useful to institutions and
  people; *spent* on access, favors, record services. A currency with sinks, not a
  score.
- **Exposure** (single value, 0–100): how visible you currently are to the state.
  Rises from being seen doing things; decays slowly. **Down is good** — the genre's
  rare inversion. Consequences scale with it (ADR 0004).

There are no levels. Access is gated by standing and clearance (institutional, per ADR
0002), never by a character-level check.

## Consequences

**Good**

- Progression *is* theme: getting ahead means becoming useful to power or invisible to
  it — the setting's actual dilemma, now the actual game loop.
- Influence-as-spendable creates sinks from day one; we dodge the mudflation treadmill.
- Exposure gives even a lone new player a live number to play against (principle 8).

**Bad / accepted costs**

- **Harder to teach than "kill things, level up."** Three numbers with different signs
  and rhythms. The prompt shows only what matters moment-to-moment (exposure); the
  dossier explains the rest. Still a real onboarding tax.
- **Exposure is loss-shaped.** A mechanic whose good direction is *down* risks reading
  as pure anxiety. Principle 3 (telegraphing) and principle 10 (shallow end) are the
  mitigations; the risk is registered in
  [future-features.md](../product/future-features.md#known-risks-in-shipped-features).
- **Influence economies inflate** without constant sink-tending. Accepted as ongoing
  balance work; every influence source ships with a sink.
- **Content is harder to write.** A mob grind generates its own content; social
  progression needs authored institutions, services, and consequences. This is the real
  cost of principle 1, paid deliberately.

## Revisit when

- Playtests show players can't articulate "what I'm working toward" after two sessions.
- Influence balances trend upward across the population for two straight playtests
  (sink failure).
