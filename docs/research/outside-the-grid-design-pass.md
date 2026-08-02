# Design pass: the world outside the Grid

The second half of [ADR 0020](../decisions/0020-world-expansion-gated-by-progression.md)'s
new geography, following [the principle-9 research pass](outside-the-grid-principle-9-pass.md)
and Lauren's answers to its four open questions. Same posture as the
[Upper Spire design pass](upper-spire-design-pass.md): proposes a concrete
shape, names the real open questions, decides nothing, isn't shippable prose.

## What's settled, going in

Lauren's answers, taken as fixed premises for this pass:

1. **The Perimeter and "outside the Grid" are the same idea at two altitudes**
   (confirmed). This pass treats `worldbuilding-ideas.md`'s existing Perimeter
   sketch — fenced boundary, outer manufacturing zones, agricultural communes,
   "unmonitored prole housing... too insignificant for the Ministry of Records
   to index" — as the place, and builds the design from there rather than
   starting over.
2. **An actual playable area**, not lore-only — with an accompanying lore
   doc, per the project's existing Lore-Code Parity Rule (`docs/lore/README.md`),
   the same requirement every other user-facing feature already follows (Form
   C-1 has `forms-and-notices.md#form-c-1`, the chalk has
   `the-chalk-marks.md`, and so on).
3. **Mechanical spine confirmed: record-vs-truth on land/water records.**
   Principle 3's low-density reshaping (what surveillance/dread looks like out
   here) stays explicitly open — Lauren confirmed the spine, not the
   surveillance mechanism.
4. **Pressure valve: NPC texture**, not a physical gathering place like
   Sector 9's pub.

## Geometry: genuinely a blank page (unlike the Spire)

Checked directly: nothing in `game/world/build.py` currently references a
perimeter, fringe, farm, or agricultural room — no partial stub exists the way
the Spire Lobby already did. This is real, unstarted geography, which means
this pass has to propose an entry point, not just extend one.

The Perimeter sketch already frames it as *fenced* — a boundary, not a smooth
gradient out of Sector 9. Proposed shape, not final: a single gate room off
the existing map (candidate: south or west of the Plaza/Hall cluster, keeping
Sector 9's own footprint untouched, matching ADR 0007's compass-consistency
rule) leading to the fenced perimeter itself, then out into the communes
proper. Mirrors the Spire's own shape (checkpoint, then the district behind
it) rather than inventing a second pattern.

## Who gets in, and why: the gating question this area needs that the Spire didn't

ADR 0020 requires new geography to gate behind *earned* progression, so
newcomers stay dense in Sector 9. The Spire's answer was obvious — Clearance,
because the Spire is explicitly the sanctioned track's own territory. This
area's answer isn't obvious, and picking the wrong one would misread what the
place is:

- **Clearance**, mirroring the Spire: reads wrong. The Perimeter sketch is
  explicit that this is *unindexed* territory — "too insignificant for the
  Ministry of Records to index." Gating it behind institutional standing the
  Ministry grants contradicts the fiction of a place the Ministry barely
  bothers with.
- **Function**, assigned at the Assignment Hall: plausible (an Agricultural
  Oversight or Requisitions function posts a citizen out here on Ministry
  business), and it would give a sanctioned, legible reason to be there —
  but functions today (Clerk, Auditor, Steward) are all interior-Grid roles;
  adding one for this area is a small, real addition, not a repurposing of
  something existing.
- **Underground/shadow standing**: the strongest fit on current evidence.
  The Perimeter's own sketch pairs "unmonitored prole housing" with
  "high-risk escape routes or smuggling chokepoints for underground courier
  runs" — this area is already, in the one paragraph that exists about it,
  imagined as continuous with the Underground's territory, not the Grid's.
  Gating entry behind shadow standing (the same tier system `word` already
  reads, ADR 0009) would be the **inverse** of the Spire's gate — the Spire
  rewards sanctioned elevation, this area would reward unsanctioned
  standing — which is a clean, legible split for a player to understand: two
  new frontiers, opposite directions, both earned.

This pass's lean is shadow standing, on the strength of the existing Perimeter
sketch's own framing, but it's a real fork and Lauren's call, the same way the
Spire's clearance-grant mechanism was left open rather than assumed.

## The mechanical spine, worked concretely: land/water records are cheaper than they look

Confirmed as the spine: falsifiable land/water records, the "near-exact
structural twin" of the citizen dossier forgery/petition loop the research
pass found. Checked against the actual code, this reuse is more literal than
it sounds, not just thematically parallel. `world/records.py`'s `add_record()`
takes a generic `subject` — the docstring says "a citizen's file" and every
current caller passes a `Character`, but nothing in the function itself
requires that; `subject.key` and `subject.id` are the only things it touches.
A land parcel or water allotment, given its own lightweight typeclass (or
even just a plain object tagged as a parcel), could be a `subject` today,
with zero changes to `records.py` itself. The existing `kind=` parameter
(already `"incident"`, `"observation"`) would just gain new values —
`"survey"`, `"allotment"` — and `petition`/`forge`'s existing logic (reading
the record layer, not the truth, per ADR 0005) extends the same way it
already handles citizen incidents. This is the strongest evidence this pass
found that the spine Lauren confirmed is actually cheap to build, not just
thematically right.

What's genuinely new, not reuse: the *content* of a land/water record (a
yield figure, a boundary line, a requisition order) and who's allowed to
`petition`/`forge` it — presumably the farmer/landholder whose parcel it is,
not the citizen the record is about in the existing dossier sense. That
actor/subject split (I hold standing to contest a record about *my land*,
not about *me*) is a small but real deviation from how `petition`/`forge`
work today and needs its own look before implementation, not assumed away
here.

## Principle 3, still open: three candidates, one lean

The research pass named three candidates for what surveillance looks like at
low camera-density; Lauren confirmed this stays open rather than picking one.
Restating them here with a lean, for the next decision point:

1. **Overflight/drone sweeps**, slower and more visible cadence than Sector
   9's Watch sampling — dread from predictability instead of ambient
   uncertainty.
2. **The permit/survey paperwork itself as the surveillance surface** — you're
   watched through what you're required to file, not through cameras. Pairs
   naturally with the land/water records spine above: the same record that
   can be falsified is also the thing that exposes you when checked.
3. **Informants drawn from the rural community itself** (M6, relocated) —
   betrayal risk from neighbors rather than cameras.

This pass's lean: **(2), with (3) layered on top, not (1).** Overflight
sweeps would be a genuinely new mechanic (new script, new sweep logic) for a
single district, which cuts against principle 9's discipline the same way a
second Exposure-like stat did for the Spire — reuse before invention.
Permit-paperwork-as-surveillance is not just cheaper, it's the *same* finding
Finding 3 already made for the spine — the record IS the surveillance
mechanism here, not a separate system bolted alongside it. Informants
layered on top costs little (NPCs already exist as a pattern) and gives this
area its own version of principle 6 the way the Spire's sponsorship option
would have given it one. Still Lauren's call, not decided here.

## The pressure valve: NPC texture, worked toward something specific

Confirmed: NPC texture, not a place. Sector 9's implied warmth is geographic
(the pub); this area's needs to be relational instead, which actually fits
the setting better — a dispersed rural community's warmth lives in *people
who show up*, not a single building. Candidate direction, not written prose:
a recurring figure (or a small handful, not one over-loaded NPC) whose
gallows humor is specifically about the land/water conflict rather than
generic Grid weariness — someone who's filed the same falsified allotment
report for years and treats it as a running joke with anyone who'll listen,
or a network of neighbors who pass warnings and gossip the way Sector 9's
proles pass rumor, just without a single physical hub to anchor it. Whether
this is one named NPC, a texture applied to several, or something else is a
real open question for whoever writes the actual lore doc and rooms — this
pass only confirms the *shape* Lauren already chose (people, not a place)
translates cleanly to something buildable.

## Lore-Code Parity: what this triggers, per the existing rule

`docs/lore/README.md`'s Lore-Code Parity Rule already requires this, not a
new obligation this pass is inventing — flagging it now so it's scoped
before implementation starts, not discovered at PR review:

- `docs/lore/historical-background.md` needs a new section for this area,
  the same way Sector 9, the Spire, and the Underground already have one
  each.
- The land/water record kind (survey, allotment) is a new state-document
  type in the same family as Form C-1, Form 77, Section C — needs an entry
  in `docs/lore/artifacts/forms-and-notices.md`, or a new artifacts doc if
  it doesn't fit that one's shape once actually drafted.
- If the informant layer (principle-3 lean, above) ships, that's new
  NPC-relationship texture — same parity obligation `recruit`/`judge`/`flip`
  already met for the Underground.

## Scope: start smaller than "the whole boundary region"

Same instinct as the Spire pass (one floor, not four): propose **one
settlement/farmstead and its immediate fenced approach**, not the entire
agricultural-communes region the Perimeter sketch gestures at. Proves the
gate mechanism, the record-vs-truth spine, and the informant/permit
surveillance texture on a small footprint before committing to more
geography — consistent with ADR 0020's own caution about pre-launch scope,
and with how "thin tutorial rooms" already landed well once.

## Open questions for Lauren

1. **Entry gate: shadow standing (this pass's lean), a new Function, or
   something else?** Shadow standing reads as the better fit given the
   Perimeter sketch's own framing, but it means this area is reachable only
   through the Underground track, not the Clearance track — worth confirming
   that's the intended split (unsanctioned frontier vs. sanctioned frontier)
   rather than assumed.
2. **Principle 3's mechanism: permit-paperwork-as-surveillance plus
   informants (this pass's lean), or overflight sweeps, or a different
   combination?**
3. **The actor/subject split for `petition`/`forge` on land records** (a
   landholder's standing over records about their land, not about
   themselves) — flagged as new logic, not decided here.
4. **The NPC-texture pressure valve's concrete shape** — one recurring
   figure, several, or an ambient texture rather than a named character?
5. **Scope: one settlement first, not the whole region — agree?**

Once these land, the natural next step is the same shape as the Spire:
an ADR that picks the specific mechanisms, then implementation against
ADR 0012's idempotent `build()` pattern, with the lore-parity work done
alongside it rather than after.
