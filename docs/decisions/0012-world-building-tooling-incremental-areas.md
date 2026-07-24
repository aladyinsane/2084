# ADR 0012 — Building new areas without rebuilding the old ones

- **Status:** Accepted
- **Date:** 2026-07-25

## Context

Lauren's question, captured in `future-features.md`'s "World-building tooling"
entry: `world/build.py` is one-shot, invoked only once by the initial-setup hook
(`contributing.md` rule 8 — "the world is code," built by batch files, never
hand-`dig`ged on the live server). Two related but distinct asks sit behind that:

1. Can a *new* district be added later without re-running, or risking
   corrupting, the districts already built?
2. Could an area ever be built from inside the running game, rather than only
   in a batch file?

Neither is possible cleanly today. `build()` is one monolithic function; every
`create_object` call inside it runs unconditionally. Re-running it against a
live database duplicates or errors on everything already there — there is no
`get_or_create` guard anywhere in the module. This has already bitten twice at
smaller scale, both recorded in CLAUDE.md: the Tier 2 NPC/prop backfill and the
shadow-ladder chalk-text backfill both needed a hand-written one-off script run
via `evennia shell -c "..."` against the live database, because `build.py`
itself couldn't safely add to what it had already built. A new district is a
bigger version of the same problem: not "add three lines to an existing room,"
but "run the whole module again and hope nothing downstream of the first call
collides with the second."

Rule 8's discipline (the world lives in reviewable, rebuildable batch code, not
live-server `dig` commands) is working as intended and isn't in question here.
What's in question is whether the *tooling* around that discipline should get
safe to re-run incrementally, and if so, which shape.

This hasn't been urgent: no district has been added since v0.1's starting
slice, and `future-features.md`'s existing "Big-world expansion / more
districts" entry already sets the real trigger — rooms get added when a
measured, busy population asks for more space, not on builder enthusiasm
(principle 8, anti-principle 4). Three shapes were sketched and presented to
Lauren, plus a null option, so that when that trigger does fire, the tooling
question has already been thought through once, instead of being solved under
time pressure with whatever's fastest.

## Decision

**Option 1: split `build()` into one function per district, each idempotent.**
Each district gets its own `build_<district>()` function, guarded by a
`get_or_create`-style check (skip creating a room, NPC, or prop if an object
with its expected key/tag already exists). A new district becomes a new
function and a new call in the initial-setup hook; existing districts' calls
stay in place, now safe to re-run without side effects. Batch code remains the
single source of truth, unchanged in spirit from rule 8 — this only changes
whether re-running a given district's function twice is safe.

Rejected alternatives, for the record:

- **Adopt the `mapbuilder` contrib for new districts, freeze old ones.**
  Zero changes to existing code, but permanently splits world-building into
  two coexisting mechanisms (old districts hand-coded, new ones drawn) and
  introduces a contrib dependency nothing else in the codebase uses.
- **Hybrid: one entry point, made safe to re-run.** Similar retrofit cost to
  option 1, with an added open question (what marks a district "already
  built" — a tag, a `ServerConfig` key, a room count) that option 1 avoids by
  keying idempotency to each district's own objects directly.
- **Do nothing.** Keep manual one-off backfill scripts, same as the last two
  times. Cheapest today; leaves the answer to "can I add a district without
  touching the others" at "not safely, no," indefinitely.

**Not decided by this ADR: when to actually implement it.** Accepting the
shape doesn't itself schedule the retrofit — per the Context above, the
trigger for needing this at all (a measured, busy population asking for more
space) hasn't fired yet. Implementation is future work, gated the same way a
new district itself would be.

## Consequences

**Good**

- Keeps rule 8's discipline fully intact: batch code stays the only way
  districts are authored, reviewable and rebuildable from the repo.
- No new contrib dependency, unlike the `mapbuilder` alternative — one fewer
  moving part to keep working across Evennia upgrades.
- The retrofit cost is bounded and one-time (every existing district's
  `build_*` gets the idempotency guard once) rather than an ongoing
  two-mechanism split that every future contributor has to remember exists.
- Idempotency is keyed to each district's own objects (room/NPC/prop
  key or tag), not a separate bookkeeping flag — one less thing that can
  drift out of sync with what's actually in the database.

**Bad**

- Every existing district's `build_*` function needs the guard retrofitted
  before any of this pays off, which touches a lot of currently-working code
  purely for future safety, not any present bug — real effort spent ahead of
  the need actually materializing.
- In-game building (asked in Context, part 2) is still not what this
  delivers. Option 1 makes *batch code* incrementally safe; it does not add
  any live-server building capability, which rule 8 continues to rule out on
  purpose. A citizen, or a builder, still cannot `dig` a new room by hand —
  only the repo's batch files can add to the world.
- The idempotency guards themselves are new surface area with their own
  failure mode: a guard keyed on the wrong thing (a key that legitimately
  changes, a tag that gets reused) could silently skip re-creating something
  that should exist, or silently duplicate something it should have
  recognized. Worth test coverage once built, not just a visual check.

## Revisit when

- A district actually gets added — implementation should happen then, not
  before, so the idempotency guards get designed against a real new district
  rather than a hypothetical one.
- The retrofit, once built, turns out to have missed something `build.py`
  currently does implicitly (ordering dependencies between districts, for
  example) — worth a specific check during implementation, not assumed away
  by this ADR.
