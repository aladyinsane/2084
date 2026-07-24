# ADR 0012 — Building new areas without rebuilding the old ones (proposed)

- **Status:** Proposed — presenting options for Lauren's sign-off, not yet decided
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
(principle 8, anti-principle 4). This ADR exists so that when that trigger
does fire, the tooling question has already been thought through once,
instead of being solved under time pressure with whatever's fastest.

## Options

**1. Split `build()` into one function per district, each idempotent.**
Each district gets its own `build_<district>()` function, guarded by a
`get_or_create`-style check (e.g., skip creating a room if an object with its
key/tag already exists in the expected location). A new district becomes a new
function and a new call in the initial-setup hook; existing districts' calls
stay in place, now safe to re-run without side effects. Batch code remains the
single source of truth, unchanged in spirit from rule 8 — this only changes
whether re-running a given district's function twice is safe.
*Cost:* every existing district's `build_*` needs the idempotency guard
retrofitted once, which touches a lot of currently-working code purely for
future safety, not any present bug.

**2. Adopt the `mapbuilder` contrib for new districts, freeze old ones.**
`future-features.md`'s ASCII-map entry already named `mapbuilder`
(draw-the-map-to-build-the-world) as the tool for whenever hand-written batch
code stops scaling. Under this option, v0.1's starting district stays exactly
as it is, in its current batch file, untouched; any *new* district is built
with `mapbuilder` instead. Existing world-building code needs zero changes.
*Cost:* two different world-building mechanisms coexist permanently (old
districts hand-coded, new ones drawn), which is a real inconsistency for
anyone maintaining the world later, and it introduces a new contrib dependency
that today's codebase doesn't use anywhere else.

**3. Hybrid: batch code stays canonical, tooling becomes incrementally safe.**
Keep hand-written batch code as the only way districts are authored (rule 8
unchanged), but invest specifically in making the *build process* safe to
re-run — for example, a `build()` that checks a `ServerConfig` flag or a
tagged marker per district before creating anything, so calling it again is a
no-op for districts already present and only builds what's new. This is
closer to option 1 in spirit but frames the fix as "make the existing single
entry point idempotent" rather than "decompose it into many functions."
*Cost:* similar retrofit cost to option 1, with a design question of its own
(what exactly marks a district as "already built" — a tag, a `ServerConfig`
key, a room count check) that would need settling before implementation.

**Do nothing (the null option).** Keep manual one-off backfill scripts as the
answer, same as the last two times. Cheapest today; the cost compounds with
every future addition, and it means the answer to "can I add a district
without touching the others" stays "not safely, no."

## Recommendation

Option 1 (per-district idempotent functions) seems like the best fit: it keeps
rule 8's discipline fully intact, doesn't add a new contrib dependency the
codebase doesn't otherwise use, and the retrofit cost is bounded and
one-time rather than an ongoing two-mechanism split. But this is a real
judgment call between reasonable alternatives, not an obvious win, and it's
Lauren's call to make, not one to pick unilaterally.

## Revisit when

- Lauren picks a direction (or decides the null option is fine for now,
  which is a valid answer given the trigger hasn't fired).
- The "Big-world expansion" trigger in `future-features.md` actually fires —
  at that point this ADR needs a decision before the first new district gets
  built, not after.
