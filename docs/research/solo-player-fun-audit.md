# Solo-player fun audit: what's thin after the first session

Follow-on to [fun-and-game-feel.md](fun-and-game-feel.md), narrowed to a question
[mud-design-landscape.md §1](mud-design-landscape.md) and
[principles.md](../product/principles.md)'s principle 8 already committed us to
answering honestly: not "is the game solo-viable" (it structurally is, and every
version since v0.1 has been checked against that test) but "is a solo session still
*fun* once the first-hour content is spent." Lauren's ask, 2026-07-26: after five
straight versions (v0.19–v0.23) built entirely for the trust machine, shift focus to
solo-player fun.

**High confidence** claims below are counted directly from the code (errand count,
version history); **medium confidence** claims are read off the ten-persona playtest's
own findings, not re-litigated here.

## 1. What already passes principle 8, and shouldn't be re-litigated

Every core loop is single-player-viable by design and by test:

- Sabotage and couriering (ADR 0008, v0.6) — the grind shelf's chosen loops, both
  solo-completable, both currently the *only* two repeatable underground actions.
- `work` (v0.3/v0.4) — the sanctioned repeatable loop, solo by construction.
- Five of six built errands (v0.9) are solo; only "Four Hands" requires a circle-mate.
- Grade (v0.12), the first-hour spine (v0.13), and the no-match overhaul (v0.14) were
  all measured solo, explicitly (parsons: Grade 3 in ~3 driven minutes; tillotson
  skipped orientation and the ladder met him anyway).
- The shadow ladder (`word`, ADR 0009) and `judge` reading citizens (ADR 0010) are both
  readable alone, no circle required to check your own standing or someone else's file.

None of this is broken. The diagnosis below is specifically about *volume and variety*
of solo content past the first session, not about whether solo play works at all.

## 2. The diagnosis: two gaps, one never triaged at all

### 2a. Repeatable solo content hasn't grown since v0.6

**High confidence** (counted directly): `world/errands.py` defines exactly six errands
across two chains, all written in v0.9 (2026-07-2x) and never added to since. One of
the six ("Four Hands") isn't solo. Once a citizen finishes both chains — one evening's
play, going by the playtest timings above — there is no more one-shot content ever
again. Everything past that point is the same two repeatable verbs the game shipped in
v0.6: `sabotage` and `deliver`/`carry`. Seven versions of subsequent work (v0.7–v0.18)
polished legibility, onboarding, and NPC texture around those two loops; the trust-
machine work since (v0.19–v0.23) added five versions of entirely multiplayer-facing
mechanics on top of them. Solo content variety has had zero net investment since v0.6.

This isn't a new finding — it's the literal shape [fun-and-game-feel.md](fun-and-game-feel.md)
predicted with dullness #5 ("progress has no horizon") and dullness #4 ("no goal
gradient"), and the Grind Shelf ([grind-loops-without-killing.md](grind-loops-without-killing.md))
named two more solo-viable loop candidates at the time (below) that were priced,
scoped, and then simply never picked up once options 1+2 shipped.

### 2b. A concrete finding from the ten-persona playtest was never triaged

**Medium confidence** (one playtester's read, not re-tested since): the
[ten-persona playtest](playtest-2026-07-20-ten-personas.md)'s "small frictions" section
(finding 6, first bullet) says, verbatim: *"`work` off-cooldown gives no sense of when
the next shift opens; the 45 dead seconds at a post have nothing in them (this is where
'a bit dull' still lives)."* Checked against `future-features.md` and every roadmap
version since: **this was never carried forward into the parking lot at all.** It isn't
in "known risks," it isn't in the cleanup backlog, it isn't marked fixed or explicitly
parked anywhere. It fell out of the pipeline between the playtest and the triage pass
that followed it (v0.16–v0.18 picked up findings 1, 2, and 4 from the same document;
this one didn't survive).

It's a small, cheap, single-loop finding that happens to sit exactly on top of the
gap named in 2a: `work` is one of the only two repeatable things a solo player does for
the entire rest of the game, and its own dead time was flagged as dull and then lost.

## 3. What's already sitting in the parking lot, unbuilt, and solo by design

Two Grind Shelf options ([future-features.md](../product/future-features.md#the-grind-shelf))
were scoped in the same 2026-07-18 pass that produced sabotage and couriering, explicitly
priced against the same psychology (measurable progress, small frequent pay, variable
jackpots, opt-in risk) and explicitly solo-viable (principle 8 was a stated constraint
on the whole shelf) — and never picked up since, because Lauren chose options 1+2 for
v0.6 and nothing has revisited the shelf since:

4. **Records archaeology.** `research` at the Annex surfaces fragments of the archive;
   assembling a story about an unperson pays influence jackpots. The rare-drop table is
   *narrative* — this is the one candidate that adds a genuinely new kind of solo
   activity (reading/piecing-together) rather than another skill-check-and-payout loop,
   and it plays directly into principle 4 (the record is not the truth) and the
   doublethink groundwork ADR 0011 already laid.
5. **Watch-the-Watch bounties.** The underground pays for verified observation: patrol
   schedules, sensor sharpness reports — `observe`'s existing output becomes a sellable
   commodity. Turns an already-built skill (observation, already trained by `judge` and
   sabotage-adjacent play) into its own income loop, cheaply, since the skill and its
   tiers already exist.

Also parked, more atmospheric than loop-shaped, but explicitly named as a principle-8
device: **the propaganda engine** (world news reacting to aggregate player action) —
"the brainstorm's best liveness idea and a strong principle-8 machine (world feels
inhabited at low population)," parked only because early versions wouldn't have had
enough player action to react to. That constraint has long since lifted (v0.6 onward
gives sabotage/courier/circle-project volume to react to); it was never revisited
because nothing has gone back to the parking lot to check.

## 4. What this doc is not proposing

Not a recommendation to build all of the above. Not an ADR — there's a real fork here
(a full new grind loop vs. a cheap juice-pass fix vs. an atmospheric feature) and design
forks with real trade-offs go to Lauren as an explicit choice, same as every prior
version's fork (0009, 0010, 0013, 0014, 0015). This doc exists to make that choice an
informed one: the two-year-old parking lot already has priced, principle-8-checked
candidates sitting unbuilt, and one concrete small-friction finding fell through the
triage pipeline entirely and should probably be picked up regardless of which bigger
direction gets chosen.

## Sources

- [fun-and-game-feel.md](fun-and-game-feel.md) — the five dullnesses, dullness #4/#5
  specifically
- [mud-design-landscape.md §1](mud-design-landscape.md) — the empty-world problem and
  the single-player-viability requirement it produces
- [grind-loops-without-killing.md](grind-loops-without-killing.md) — the Grind Shelf's
  five options, 1+2 shipped as ADR 0008, 3 stays parked (Lauren's 2026-07-23 call), 4
  and 5 never revisited
- [playtest-2026-07-20-ten-personas.md](playtest-2026-07-20-ten-personas.md) — finding
  6's first bullet, the un-triaged `work`-cooldown finding
- Counted directly: `game/world/errands.py` (six errands, two chains, unchanged since
  v0.9); `docs/product/roadmap.md` (v0.6 through v0.23, confirming no new solo grind
  content shipped in that span)
