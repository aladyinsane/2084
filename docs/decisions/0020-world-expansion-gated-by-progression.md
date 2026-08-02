# ADR 0020 — Growing the world before launch: a new district, the world outside the Grid, gated by progression

- **Status:** Proposed
- **Date:** 2026-08-02

## Context

Two districts exist today: Sector 9 (civilian Grid life) and the Underground (the
shadow economy). `principles.md`'s anti-principle 4 — "Not a big world. Rooms are
added when population justifies them, never because building is fun" — and
`future-features.md`'s "Big-world expansion / more districts" entry both frame
geography growth the same way: a *post-launch* trigger, fired by a measured, busy
population, never by builder enthusiasm. That framing exists for a real reason
(principle 8, "Alive at three players" — the empty-world problem is the leading
cause of MUD death) and it's worked as intended: no district has been added since
v0.1's starting slice.

That framing has a gap, though: it never addresses whether the *pre-launch*
footprint is itself sufficient before any human population exists to measure
against. Lauren's read, arrived at independently of any playtest data: two
districts isn't enough "make-believe world" to hold human players long-term, and
this was the intention from the start — build enough geography to be worth opening
the doors to other humans, before opening them. Part of what a MUD sells is the
believable world itself, not only its loops.

The ten-persona long-term-retention playtest
([docs/research/playtest-2026-08-01-long-term-retention.md](../research/playtest-2026-08-01-long-term-retention.md))
reinforces this from a different angle — sensor scarcity, small exhaustible
one-time content pools, no daily-varying hook — but it isn't the primary
justification here, and its evidence needs a caveat: those personas played at
machine pace with no competing real-life demands, so "all 5 sensors gone in ~10
minutes" is not a reliable estimate of real human pacing. It's supporting context
for "the world is thin," not proof of a specific timeline.

Acting on this carries a real risk, not just a documented one: principle 8's actual
mechanism is "geography stays small and dense so the players who *are* online
collide." Opening a bigger map onto a population that's still near zero on day one
recreates the exact problem anti-principle 4 exists to prevent — just moved
earlier, onto the first humans this project is trying to hook, rather than
prevented by never growing.

An existing primitive already resolves that risk without inventing anything new:
`clearance(N)`, a lockfunc defined in `server/conf/lockfuncs.py` and already used to
gate at least one exit (`game/world/build.py:404`, the Spire). Gating new
geography's entry points behind progression a player has to earn — rather than
opening it to a character on day one — keeps new players funneled through Sector
9's density while only invested players spread outward. Total footprint grows
without diluting the density a brand-new player actually experiences.

Two concrete additions came out of the conversation:

1. **One new district within the existing Grid/civilian frame.** Theme not yet
   chosen — a follow-up design pass, not part of this decision.
2. **The "world outside the Grid" idea already sitting in the parking lot**
   (`future-features.md`, Speculative, from Lauren's 2026-07-25 journal): a
   resource conflict between farmers/rural landholders and the Ministry, over land
   and water wanted for AI data centers. A genuinely different axis on principle
   1's antagonist — the regime's hunger for resources, not only its hunger for
   legible citizens. Already flagged in that entry as "closer in kind to Big-world
   expansion... gated on a measured busy world," with no research pass run against
   it yet.

A related but separate idea came out of the same conversation — building out the
Underground itself as the tutorial for unsanctioned commands, which ADR 0009
already anticipated as its own revisit trigger — recorded in `future-features.md`,
not part of this ADR's scope.

## Decision

**Anti-principle 4 gets a clarifying amendment, not a reversal.** Rooms are added
when *either* concurrent population supports them (the original, ongoing
post-launch trigger — unchanged) *or*, once, the pre-launch footprint itself falls
short of a believable world worth opening to humans at all. This ADR is that
one-time exercise of the second clause. It is not a standing license: after this,
"the world feels thin" stops being a valid reason on its own to add a third
district — the original population trigger governs again. `principles.md` and the
"Big-world expansion" entry in `future-features.md` get updated to say this
explicitly once this ADR is accepted, so the constraint documents and this
decision don't quietly disagree with each other.

**Two additions, both gated:**

1. A new in-Grid district (theme TBD, follow-up design pass required before any
   `build.py` work starts).
2. The "outside the Grid" axis (farmers vs. the Ministry, land and water),
   promoted out of Speculative into scoped, real work — still needs its own
   principle-9 research pass (does the fiction convert all the way down, the way
   every existing district's did) before room-by-room content gets written.

Both are gated behind progression at their entry points, using the existing
`clearance()` lockfunc idiom (or a new, equivalent lockfunc for shadow standing,
symmetric to how the Underground already partly self-gates via `word`) — not open
to a character from creation. Exact thresholds are implementation detail, not
decided here, but they need to be checked against realistic achievable pacing, not
picked because a number feels right.

**World-building tooling.** This is the first real district addition since v0.1,
which means it's the first real trigger for ADR 0012's deferred idempotent-build
retrofit (`build()` split into one idempotent function per district). Since this
ADR adds two areas, not a hypothetical one, the retrofit happens as part of this
work rather than another one-off manual edit to the monolithic `build()`.

**Not decided by this ADR:** the new in-Grid district's theme, room-by-room content
for either area, exact gate thresholds, or a build order between the two additions.
Those are follow-up design and implementation passes.

## Consequences

**Good**

- Closes a real gap in the docs: pre-launch completeness was never addressed by any
  existing principle or parking-lot entry, only post-launch scaling was.
- Gating preserves principle 8's collision-density guarantee even as total
  footprint grows — new players still experience a small, dense start.
- The "outside the Grid" axis gives principle 1 a second dimension (resource
  hunger, not only legibility hunger) instead of just more of the same two
  districts' territory.
- Reuses an existing, already-proven primitive (`clearance()`) instead of
  inventing a new gating mechanism from scratch.
- Finally exercises ADR 0012's deferred idempotent-build shape against a real
  district, the way that ADR's own "Revisit when" wanted it designed.

**Bad**

- This is exactly the kind of decision anti-principle 4 exists to make hard to
  justify. "It feels thin" is uncomfortably close to "building because building is
  fun" if the pre-launch/post-launch distinction isn't taken seriously — that
  distinction is being invented by this ADR, not one that pre-existed, and
  deserves real scrutiny rather than being treated as obviously legitimate.
- Real, non-trivial effort: two new hand-authored areas (rooms, NPCs, props,
  prose) plus the ADR 0012 tooling retrofit, all before a single human has played
  the current build. This is a meaningful scope addition, not a small patch.
- Gating has its own failure mode if the threshold is wrong: a district gated
  behind a Clearance level (or shadow-standing tier) that isn't realistically
  reachable in a normal play session just relocates "the world feels thin" behind
  a wall instead of fixing it.
- "Outside the Grid" is a bigger creative commitment than a new civilian district —
  genuinely new lore that has to survive contact with principle 9 ("alien contents
  all the way down") the same way every existing district did, and hasn't been
  research-passed yet.
- The playtest evidence that partly motivated this is bot-paced, not human-paced.
  Real validation only comes from actual human playtesting after both areas ship,
  which doesn't exist yet — this ADR is a bet in the meantime, not a proven fix.

## Revisit when

- The new in-Grid district's theme needs choosing — a dedicated design pass before
  any `build.py` work starts.
- A principle-9 research pass gets run against "outside the Grid" specifically,
  the same weight every other district's fiction got before being built.
- The first real human playtest after both areas ship — check whether gating
  actually held (do new players still collide in Sector 9, or did the bigger map
  thin things out anyway despite the gate).
- If a future population genuinely does outgrow this expanded footprint, the
  *original* anti-principle 4 trigger (concurrent population) governs a third
  district — this ADR's one-time completeness clause does not fire again.
