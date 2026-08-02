# ADR 0021 — The Upper Spire: escalating paperwork to C-4, sponsorship for C-5, one floor built now

- **Status:** Proposed
- **Date:** 2026-08-02

## Context

[ADR 0020](0020-world-expansion-gated-by-progression.md) scoped in a new
in-Grid district as part of the pre-launch expansion; Lauren picked "the
Upper Spire" from `worldbuilding-ideas.md`'s existing sketch (item 1, "The
Upper Spire, Clearance C-2 through C-5"). `future-features.md` required a
design pass before any `build.py` work — that pass
([docs/research/upper-spire-design-pass.md](../research/upper-spire-design-pass.md))
found the Spire isn't a blank page: `game/world/build.py` already builds the
Central Spire Checkpoint and a Lobby dead-ended at `clearance(1)`, and the
Lobby's own shipped text ("Elevator banks... ASCENT BY APPOINTMENT") and
`map.py`'s ("the Grid above your clearance is rumor") already set up this
district almost exactly, written before this district was ever discussed.
`world/tuning.py`'s `CLEARANCE_GRANT_EXPOSURE` constant even already carries
an M2 citation ("elevation means scrutiny").

That pass left four open questions. Lauren's answers, taken as the decision
this ADR records:

1. Clearance above C-1: **escalating Form C-2 for floors C-2 through C-4,
   sponsorship for floor C-5.**
2. Elevation **reuses Exposure** as-is, different fictional triggers, no new
   stat.
3. **Build one floor (C-2) now**; C-3 through C-5 deferred.
4. This district's principle-10 pressure valve is **a room**, at least for
   C-2 — the deliberate inverse of the "outside the Grid" area's NPC-texture
   answer ([docs/research/outside-the-grid-design-pass.md](../research/outside-the-grid-design-pass.md)),
   giving the two new districts genuinely different textures rather than two
   reskins of the same idea.

## Decision

**Getting past C-1 splits by tier, not by picking one mechanism for all
four floors.** C-2, C-3, and C-4 each require their own Form (mirroring
`world/functions.py`'s existing `adjudicate_c1`/`grant_c1` shape — record
layer read, not the truth, per ADR 0005; a tighter incident threshold and a
larger `CLEARANCE_GRANT_EXPOSURE`-style tax at each tier). C-5 breaks that
pattern deliberately: no Form C-5 exists, and clearance to the top floor is
granted only by sponsorship from an existing C-5 holder (NPC initially,
player-capable later, the same shape ADR 0014's vouching already proved).
This wasn't in the design pass's own three options as a combination, only as
a fork — recording the shape it turned into, and the reasoning it implies
even though it wasn't spelled out: paperwork gets a citizen through the
upper-middle tiers, still legible, still within the Ministry's own
self-image of itself as a place that runs on forms — but the top floor is
reserved for something a form can't buy. Trust is the scarcest currency
(principle 6) precisely because it's the one thing bureaucracy can't
manufacture, which makes it the right gate for the rarest tier.

**Elevation raises Exposure, the existing stat, with new fictional
triggers** — an unmarked door, an NPC addressed out of order, idling
somewhere idling isn't done, appearing without an appointment on a floor.
Same number, same prompt, same Watch-sweep mechanism underneath; only the
fiction of what trips it changes. No second stat, no new UI.

**Only C-2 gets built now.** One floor, fully realized — geometry (an `up`
exit from `spire_lobby`, gated `clearance(2)`, the first vertical movement
in the game, using the `ingame_map_display` contrib's shaft rendering that's
never been exercised yet), Form C-2 itself, and a pressure-valve room for
this floor specifically. C-3 and C-4's Forms and C-5's sponsorship mechanism
are decided by this ADR in shape, so they don't need re-litigating when
their floors eventually get built, but their rooms, exact thresholds, and
content are not built now.

**The C-2 pressure valve is a room**, not an NPC-texture pattern — an actual
place a citizen who's reached C-2 can go, mirroring the *shape* of Sector
9's implied pub (a physical anchor for warmth) rather than its content.
What's in that room — who's there, what the joke is — is implementation
detail, not decided here; the ADR only fixes that it's a place, per Lauren's
answer, and that it's scoped to C-2 specifically rather than the whole
district.

**Not decided by this ADR:** the specific incident thresholds and Exposure
taxes for Form C-2 (C-3/C-4's specifics even further out), the C-2 room's
actual prose and NPCs, and anything about C-3 through C-5's actual content.
Per `docs/lore/README.md`'s Lore-Code Parity Rule, Form C-2 will need an
entry in `docs/lore/artifacts/forms-and-notices.md` and the Spire's section
in `docs/lore/historical-background.md` needs updating once C-2 ships — not
optional follow-up, the same obligation every other user-facing form already
met.

## Consequences

**Good**

- Reuses almost everything that already exists: the `clearance()` lockfunc,
  Form C-1's adjudicate/grant shape, Exposure, ADR 0014's vouching pattern,
  the map contrib's shaft rendering. Genuinely new mechanical surface for
  C-2 specifically is small.
- The Form/sponsorship split gives C-5 real narrative weight without
  over-building now — sponsorship is deferred exactly to the tier where it
  will matter, not built early and left idle.
- Single-floor scope keeps this consistent with ADR 0020's own caution
  against pre-launch over-commitment, and mirrors what already worked for
  the Orientation Wing's thin rooms.
- A room-based pressure valve here versus NPC-texture for "outside the
  Grid" gives the two new ADR 0020 districts genuinely distinct identities
  instead of two districts wearing the same solution.

**Bad**

- Form C-2's actual criteria (thresholds, tax amount) aren't designed yet,
  only its shape — real tuning work remains before it's buildable, not a
  rubber stamp of Form C-1's numbers.
- Deferring C-3 through C-5 means the sponsorship mechanism for C-5 won't
  get exercised or validated for a long time. If it turns out not to work
  well in play, that's discovered far downstream of this decision, not
  soon after.
- A dedicated C-2 pressure-valve room is new content-authoring effort with
  nothing to reuse from elsewhere in the game, unlike almost every other
  piece of this ADR.
- The original "C-2 through C-5" sketch implied a multi-floor bureaucracy at
  scale; what actually ships near-term is one floor. That's intentional
  (see Consequences, Good), but worth being honest that a citizen reaching
  C-2 finds a real but small addition, not the sweeping vertical Ministry
  the worldbuilding sketch gestures at — at least not yet.

## Revisit when

- C-2 ships and gets played — check whether reused Exposure actually reads
  as "elite etiquette" rather than Sector 9's Exposure with new flavor text,
  and whether the room-based pressure valve lands the way "outside the
  Grid"'s NPC-texture answer is expected to for that area.
- C-3 and C-4 get built — by the third escalating Form, check it isn't
  reading as repetitive paperwork rather than rising stakes.
- C-5 gets built — this is where sponsorship actually gets exercised for
  the first time; check it against however ADR 0014's vouching pattern has
  evolved by then, since this ADR assumes it still holds.
