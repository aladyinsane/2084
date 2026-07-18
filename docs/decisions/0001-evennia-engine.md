# ADR 0001 — Build on Evennia, not a DIKU-lineage codebase or a custom server

- **Status:** Accepted
- **Date:** 2026-07-17

## Context

2084 wants CircleMUD's *feel* (rooms, compass movement, the prompt) with systems no
DIKU descendant has: mutable record objects, dossiers, bureaucratic form flows,
state-dependent command sets. Candidates: tbaMUD/CircleMUD (C), a custom Python server,
or Evennia. Research: [evennia-capabilities.md](../research/evennia-capabilities.md).

## Decision

Evennia (currently 6.1.x), pinned in a project venv. Custom logic lives in our game
folder's typeclasses, commands, and scripts; we do not fork the engine.

## Rationale

- Our differentiating systems are *data-model-shaped* — records with audit trails,
  per-faction ledgers, revocable standing. Evennia's typeclasses + schemaless
  Attributes make these afternoon projects; in C they're months of infrastructure.
- CmdSets map exactly onto our core states (detained, undercover, unpersoned): swap the
  command set, and the game state *is* the interface. This single feature is worth the
  engine choice.
- The CircleMUD feel is a surface: default commands already provide it
  ([evennia-capabilities.md](../research/evennia-capabilities.md), "CircleMUD-feel
  checklist"). Authenticity of feel doesn't require authenticity of codebase.
- Proven on our exact stack: the sibling Another World project runs Evennia 6.1 on this
  Windows/Python 3.14 machine today.
- A custom server means re-debugging login, persistence, and parsing before writing a
  single telescreen. That's the project dying of infrastructure.

## Consequences

**Good**

- All 2084-specific complexity lands in Python we own, testable with Evennia's test
  runner.
- Web client + Django admin for free — zero-install playtests, and admin as a literal
  Ministry of Records back office.
- Batch processors give us world-as-code from day one.

**Bad / accepted costs**

- **Heavy stack for a text game.** Django + Twisted + two processes. Contributor setup
  is "install Python tooling," not "run the binary."
- **Event-driven or bust.** Per-tick simulation over many objects is the engine's
  anti-pattern; ADR 0004 is partly forced by this. If we ever want dense real-time
  simulation, we'll be fighting the engine.
- **Smaller ecosystem than 30 years of DIKU snippets.** Fewer drop-in systems; we write
  more ourselves.
- **Major-version churn is real** (5→6 moved contribs). Pinning mitigates; upgrades are
  deliberate chores, not `pip install -U`.

## Revisit when

Never realistically — this is load-bearing for everything. If Evennia development
stopped *and* a required fix was refused upstream, we'd vendor, not switch.
