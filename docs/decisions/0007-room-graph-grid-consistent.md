# ADR 0007 — The world is a hand-built room graph, kept grid-consistent

- **Status:** Accepted
- **Date:** 2026-07-17

## Context

An in-game ASCII map is a planned later feature — deliberately not v1 (see the parking
lot entry in [future-features.md](../product/future-features.md)). Evennia offers three
mapping paths (`ingame_map_display`, `xyzgrid`, `mapbuilder` — analyzed in
[evennia-capabilities.md](../research/evennia-capabilities.md)), and all of them assume
compass-direction exits and physically coherent geometry. Worlds that grow up without
that discipline (portal-soup exits, two rooms both "north" of a third, loops that
violate space) make every mapping option degrade or die. The decision that must be made
*now* is not which map to build — it's whether the world stays mappable.

## Decision

- The world is a **hand-built graph of rooms**, created from versioned batch code — no
  coordinate system, no grid engine, in v1.
- **Grid-consistency is a build rule from room one:**
  1. Exits between adjacent rooms use compass directions (`n/s/e/w/u/d`) with true
     reciprocals (the exit back from your `north` is `south`);
  2. Geometry must embed in a sane 2D plan per z-level — no overlapping rooms, no
     spatial paradoxes. District plans are sketched on graph paper (or ASCII in a
     comment) *before* batch code is written;
  3. Non-compass exits (`enter kiosk`, transit lines, service hatches) are allowed as
     explicit exceptions — they represent portals/transitions, they're expected to
     render specially or not at all on any future map, and each one is a deliberate
     choice, not a default.
- When the ASCII map feature leaves the parking lot, `ingame_map_display` (graph-
  derived, no migration) is the default door; `xyzgrid` remains possible but is
  understood to be a world-file rebuild.

## Consequences

**Good**

- Every mapping option stays open at near-zero ongoing cost — the discipline is a
  building convention, not code.
- Grid-consistent geography is *also* better geography for play: players build mental
  maps (principle 9's veteran does it by reflex), and a small dense district
  (principle 8) rewards that.
- Batch-code worlds diff, review, and rebuild — the world gets the same
  version-control discipline as the docs.

**Bad / accepted costs**

- **Builders are genuinely constrained.** Weird Escher spaces, teleport mazes, and
  "bigger on the inside" tricks — legitimate tools in MUD building — are off the menu
  or budgeted as rare exceptions. Note the fiction offers compensation: the Grid is a
  *planned city*; oppressive regularity is on-theme.
- **A convention without enforcement will drift.** Nothing in the engine stops an
  inconsistent exit; only review does (a lint script over the room graph is cheap and
  worth writing when building outgrows one district).
- **Hand-built means small.** No procedural districts; growth is authored. Aligned
  with anti-principle 4, but it's still a ceiling, accepted.
- **If we ever *do* want `xyzgrid`** (say, for pathfinding patrols), this ADR made it
  *possible*, not cheap: the migration is real work we're consciously deferring.

## Revisit when

- The ASCII map feature is scheduled — that's the moment to pick a door, in a new ADR
  that supersedes the "no coordinate system" clause if needed.
