# ADR 0016 — Records archaeology: a third grind loop, at the Annex

- **Status:** Accepted
- **Date:** 2026-07-26

## Context

[solo-player-fun-audit.md](../research/solo-player-fun-audit.md) found that repeatable
solo content hasn't grown since v0.6: `sabotage` and `deliver`/`carry` (ADR 0008) remain
the only two repeatable underground actions, and the last five versions (v0.19–v0.23)
invested entirely in multiplayer trust mechanics. Two Grind Shelf candidates
([grind-loops-without-killing.md](../research/grind-loops-without-killing.md), option 4
and 5) were priced against the same psychology at the same time sabotage/couriering
were, and never picked up. Lauren picked **records archaeology** (option 4) to plan
first.

The parking lot's one-line sketch: *"`research` at the Annex surfaces fragments;
assembling a story about an unperson pays influence jackpots. The rare-drop table is
narrative."* Two real forks needed resolving before this is buildable, both presented to
Lauren:

**Fork 1 — what a "case" is made of.** A finite, hand-authored pool of complete
unperson stories (errands.py's shape, at larger scale) eventually runs dry the same way
the six errands did — the exact failure mode the audit diagnosed. Pure procedural
recombination (Mad-Libs tables, no authored content) is genuinely infinite but risks
losing the narrative-assembly hook that's supposed to differentiate this from a third
flavor of `sabotage`. **Chosen: both.** Common fragments recombine from an atomic-
sentence pool (infinite, no fragile grammar-stitching — see Decision); a rare draw
instead surfaces a piece of one of a handful of hand-authored, lore-connected named
cases, each solvable once per citizen.

**Fork 2 — what completing a case pays.** The verb itself is sanctioned (a citizen
reading the public archive, logged by the archivist) but the payoff — piecing together
what the Ministry did to someone — is the subversive part. Pure Records-only payout
fits the fiction cleanly but leaves the underground ledger untouched; pure underground-
only payout matches "the grind pays the underground" (ADR 0008's rule since v0.6) but is
a real stretch for an activity that happens in a monitored public reading room in full
view of an archivist. **Chosen: hybrid**, the same shape ADR 0014 (vouching) picked for
an analogous reason — small Records standing per fragment (reachable, sanctioned,
day one), underground standing on completion (the actual payoff, earned by assembling
something the Ministry would rather stayed scattered).

## Decision

New `world/archaeology.py`, following `errands.py`'s shape (a data table + small
dispatch functions) and `circle_projects.py`'s registry-of-progress idiom, but scoped to
one citizen's own `db` state rather than shared circle state — there is no group
component here, by design (principle 8's solo test is the whole point of this version).

**The verb:** `research`, gated on the archivist's presence exactly like `petition`
(`commands/civic.py`'s `_archivist()` helper, reused) — no clearance gate, no circle
requirement, open to any citizen from their first session. `help_category = "sector 9"`
(sanctioned): taught on the Archive Annex's own placard, not the Tunnel B chalk, mirroring
vouching's precedent of a sanctioned surface with an underground-adjacent payoff.

**Generic cases (the infinite grind):** `char.db.archaeology_case = {"name": ..., "found":
[...]}`. Starting a case (automatically, whenever a citizen has none in progress) draws
one name from a small pool (~12 in-voice handles — "a printer's apprentice," "a third-
shift auditor," never a proper name, matching Sector 9's existing voice) to give the case
an identity from its first fragment. Each successful `research` draws one *atomic*
fragment sentence, without replacement within the case, from a pool of ~20–30
independently-written one-liners (e.g. "A requisition form for a coat that was never
collected." "A transfer order to a district that appears on no current map."). No
grammatical recombination — sentences stand alone and are simply presented together,
which is both easier to write well and immune to Mad-Libs agreement bugs. At
`tuning.CASE_FRAGMENTS_REQUIRED` (proposed: 3) fragments collected, the case resolves: all
found fragments print together under the case's name, underground standing pays out
(`tuning.CASE_COMPLETION_PAYOUT`, proposed: 8), and a fresh case starts on the citizen's
next `research`. With ~30 fragments drawn 3 at a time without replacement, repetition is
practically a non-issue at launch; the pool can grow later without any code change,
same as errands' catalog.

**Named cases (the jackpot):** a small hand-authored dict, `NAMED_CASES` (proposed: 3 to
start), each with its own ~3 fragments and a longer reveal paragraph tying into existing
lore where it fits naturally. On each `research` call, roll `tuning.RESEARCH_RARE_CHANCE`
(base + a small `clerking`-skill bonus, same shape as `SABOTAGE_SKILL_BONUS`) against a
citizen's not-yet-fully-collected named cases; a hit assigns the next fragment of one
instead of a generic draw. Completing a named case prints its full reveal and pays more
(`tuning.NAMED_CASE_PAYOUT`, proposed: 18) than a generic case — sized like
`PROJECT_PAYOUT` was, to move the shadow ladder a real amount. Solved once per citizen
(`char.db.archaeology_solved`, a list of case keys); other citizens can still solve the
same named case independently — this is authored content, not a world-first race.

**Cost and risk, satisfying the Grind Shelf's own checklist** (a repeatable verb, paying
immediately, with bounded telegraphed risk, an occasional jackpot, and no requirement to
ever touch it):

- Every successful `research` pays `tuning.RESEARCH_INFLUENCE` (proposed: 1) Ministry of
  Records standing and costs `tuning.RESEARCH_EXPOSURE` (proposed: 1) — routine, cheap,
  same shape as `work`.
- A rare/named draw costs more (`tuning.RESEARCH_RARE_EXPOSURE`, proposed: 4) — digging
  into what happened to someone specific is noticed more than routine consultation. This
  is the loop's telegraphed-risk axis: the jackpot draw is the one moment it costs more,
  not a hidden tax on ordinary use.
- `tuning.RESEARCH_COOLDOWN` (proposed: 60s) gates repeat use, same idiom as `work`. The
  off-cooldown rejection reuses the near/far prose-tier pattern just shipped for `work`
  (PR #51) rather than a new static line, for consistency.
- No skill check, no failure state. The "risk" here is cumulative exposure from grinding,
  not a pass/fail roll — matching `work`'s shape, not `sabotage`'s. A citizen who never
  touches this loop loses nothing; a citizen who grinds it hard trades exposure margin for
  both ledgers moving.

**Curriculum and lore, flagged for implementation (Lore Maintenance Protocol applies this
time — new NPC lines from the archivist reacting to `research`, and a new placard mention
at the Annex):** the Archive Annex's room description gains a line naming `research`; the
archivist gets reaction lines distinct from `petition`'s. The named cases are new
narrative content in their own right and should get a lore artifacts entry (a new
`docs/lore/artifacts/unperson-case-files.md`, cataloguing the authored cases the way
`forms-and-notices.md` catalogues forms) rather than folding into
`historical-background.md`'s existing prose.

## Consequences

**Good**

- Directly answers the audit's diagnosis: a third repeatable, genuinely-infinite solo
  loop, the first new one since v0.6.
- Satisfies every item on `grind-loops-without-killing.md`'s own extraction checklist,
  checked explicitly rather than assumed.
- The atomic-fragment-pool design sidesteps Mad-Libs grammar fragility entirely — no
  template stitching, no agreement bugs, just independently-good sentences presented
  together.
- Reuses architecture wholesale: `_archivist()` gating (petition's precedent), the
  near/far cooldown-texture idiom (`work`'s, just shipped), skill-bonus formulas
  (`sabotage`/`forge`'s shape), hybrid sanctioned/underground payout (vouching's
  precedent).
- Gives risk-averse players — who might never touch `sabotage`/`carry` — a third grind
  option that never requires leaving sanctioned space, addressing the same solo-content
  gap for a different player archetype than the underground-first loops do.

**Bad**

- **~20–30 hand-written atomic fragments is real, ongoing writing work**, same as any
  narrative content, and if underwritten will show its seams (a citizen who grinds hard
  will see every fragment repeat within a session or two). Sized deliberately smaller
  than a full errand catalog to keep launch scope real, with the explicit expectation
  the pool grows later, same as errands.
- **A third source of underground standing changes that ledger's math** — `word`'s shadow
  tiers (`SHADOW_TIERS`) were tuned against sabotage/courier/circle-project income alone;
  adding a third solo source (payable by anyone, no chalk-discovery required) may move
  citizens up the ladder faster than intended. Worth watching at the next playtest gate,
  same caution `SHADOW_TIERS`' own comment already names for retuned payouts generally.
- **Named cases are solved-once-per-citizen, not world-once** — deliberate (avoids a
  race/scarcity problem with a small population), but it does mean the "rare" content
  isn't actually rare in the population sense, just rare *per attempt*. A citizen who
  grinds long enough eventually collects all of them; there's no scarcity beyond time
  invested.
- **No skill gate on baseline use** (unlike `sabotage`'s check, `judge`'s tiers, or
  `flip`'s requirement) — anyone can `research` from session one. Intentional (the
  shallow-end principle), but it's the first grind loop with zero failure state at all;
  worth confirming in playtest that "cost accumulates, nothing ever fails" still reads as
  a real activity rather than a slot machine with no lose condition.
- **The Lore Maintenance Protocol scope here is bigger than ADR 0015's** — new NPC
  lines, a new placard mention, and a new lore artifacts file are all real, separate work
  at implementation time, not a single follow-up line.

## Revisit when

- Playtest shows the fragment pool repeating noticeably within a session — grow the pool;
  tuning-only, no ADR needed.
- The shadow ladder's pacing shifts noticeably once this loop is live — retune
  `RESEARCH_INFLUENCE`/`CASE_COMPLETION_PAYOUT`/`NAMED_CASE_PAYOUT`, or revisit
  `SHADOW_TIERS` itself if the whole ledger's pacing needs to move.
- A citizen finishes every named case and asks "is that all of them" — signal to author
  more, not a design problem.
- Someone wants group participation in a case (a circle piecing one together together) —
  that's a different mechanic layered on top, not an amendment to this one, which is
  deliberately solo by design.
