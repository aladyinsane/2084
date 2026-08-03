# ADR 0022 — The world outside the Grid: shadow-standing gate, land/water records, one settlement now

- **Status:** Proposed
- **Date:** 2026-08-02

## Context

[ADR 0020](0020-world-expansion-gated-by-progression.md) scoped in "the world
outside the Grid" (farmers/rural landholders vs. the Ministry, over land and
water for AI data centers) as the second half of the pre-launch expansion.
Two research passes preceded this ADR:
[the principle-9 audit](../research/outside-the-grid-principle-9-pass.md)
(confirmed the area is the same idea as `worldbuilding-ideas.md`'s Perimeter
sketch at a different altitude, and that principle 1 only survives if the
spine is record-vs-truth on land/water, not a farming minigame), and
[the follow-up design pass](../research/outside-the-grid-design-pass.md)
(found `world/records.py`'s `add_record()` takes a generic `subject`, so
land/water records can reuse the existing forgery/petition machinery almost
as-is; proposed shadow standing as the entry gate, the inverse of the
Spire's Clearance gate; leaned toward permit-paperwork-as-surveillance plus
informants for principle 3; and proposed NPC texture as the pressure valve).

That pass left five open questions. Lauren's answers, taken as the decision
this ADR records:

1. **Entry gate: shadow standing**, confirmed — this area is reachable only
   through the Underground track, the deliberate inverse of the Spire's
   Clearance track ([ADR 0021](0021-upper-spire-clearance-c2-through-c5.md)).
2. **Principle 3: permit-paperwork-as-surveillance plus informants**,
   confirmed over inventing a new overflight-sweep mechanic.
3. **The actor/subject split for `petition`/`forge` on land records**
   confirmed — a landholder holds standing over records about *their land*,
   not about themselves, a real deviation from how those verbs work today.
4. **The NPC-texture pressure valve starts as one recurring figure**, with
   room to add more later if one isn't enough.
5. **Scope: one settlement first**, not the whole boundary region,
   confirmed.

## Decision

**Entry is gated by shadow standing**, using the same tier system `word`
already reads (ADR 0009), not `clearance()`. This is the intended split
named in the design pass: two new frontiers in opposite directions, the
Spire rewarding sanctioned elevation and this area rewarding unsanctioned
standing. A citizen who has only ever worked within the Grid's sanctioned
track has no route in; reaching this area requires having built up
Underground standing first, same as reaching any shadow-ladder tier does
today.

**The mechanical spine is land/water records, built on `records.py`'s
existing generic `subject` parameter.** New `kind=` values (`"survey"`,
`"allotment"`) join the existing `"incident"`/`"observation"` kinds; a land
parcel or water allotment gets its own lightweight subject (a typeclassed
object, tagged the way `records.py` already tags any subject) rather than a
new records system. `petition`/`forge` extend to these record kinds with one
real change: **the actor who may contest or falsify a land/water record is
the landholder whose parcel it concerns, not the citizen the record
happens to name** — a citizen's standing over their own land record, not
over themselves. This is new logic in `petition`/`forge`'s authorization
check, not present today, and needs its own look during implementation
rather than being assumed to fall out of the existing citizen-dossier code
unchanged.

**Principle 3 (surveillance, reshaped for low density) is permit-paperwork-
as-surveillance plus informants.** The same land/water record that can be
falsified is also the surface that exposes a citizen when checked — the
paperwork itself is the surveillance mechanism, not a separate camera/sweep
system. Informants (M6, relocated to a rural community) layer on top,
reusing the existing NPC-relationship pattern rather than inventing new
mechanics. No overflight/drone sweep system gets built for this area.

**The pressure valve is one recurring NPC figure**, to start — not an
ambient texture applied to several unnamed characters, and not a physical
room (the deliberate inverse of the Spire's answer, per ADR 0021). If one
figure doesn't carry enough of the district's warmth once it's played,
expanding to several is explicitly left open rather than ruled out.

**Scope: one settlement and its immediate fenced approach**, not the full
agricultural-communes region the Perimeter sketch gestures at. Proves the
gate, the records spine, and the permit/informant surveillance texture on a
small footprint before any further geography gets committed.

**Not decided by this ADR:** the specific shadow-standing tier required for
entry, the settlement's actual geometry and room count, the recurring NPC's
identity and voice, and the specific content of land/water records once
authored. Per `docs/lore/README.md`'s Lore-Code Parity Rule, this area will
need a new section in `docs/lore/historical-background.md` and an entry for
the new record kind in `docs/lore/artifacts/forms-and-notices.md` (or a new
artifacts doc if the shape doesn't fit) once implementation starts — not
optional follow-up.

## Consequences

**Good**

- The records spine is cheap, not just thematically right: `records.py`
  needed no changes to support this, only new `kind=` values and a new
  subject type. The forgery/petition gameplay loop already exists; this
  points it at a second kind of subject.
- The shadow-standing gate and the Spire's Clearance gate give ADR 0020's
  two new districts a legible, opposite-facing structure — sanctioned
  elevation versus unsanctioned standing — rather than two districts
  reachable the same way.
- Permit-paperwork-as-surveillance reuses the records spine itself as the
  surveillance mechanism, avoiding a second new system for principle 3 the
  way the Spire avoided a second stat for elevation.
- One NPC figure as the pressure valve is cheap to build and easy to
  expand later if it doesn't land — no commitment to a larger cast before
  anyone's played the area.
- Single-settlement scope keeps this consistent with ADR 0020's caution
  against pre-launch over-commitment.

**Bad**

- The actor/subject split for `petition`/`forge` is new authorization logic
  that doesn't exist today — a real implementation cost, not free reuse,
  despite the records spine itself being cheap.
- Gating entirely behind shadow standing means a citizen who has invested
  only in the sanctioned track (Clearance, Grade, Function) has no way into
  this area at all, by design — worth being explicit that this is a
  deliberate exclusion, not an oversight, since it forecloses one whole
  playstyle from ever seeing this content.
- One recurring NPC carrying the entire pressure-valve function is a single
  point of failure for the area's tone — if that figure doesn't land in
  play, the district has no warmth until a second figure gets authored,
  unlike Sector 9's pub, which doesn't depend on any one NPC being good.
- No principle-3 mechanism here has been playtested yet; permit-paperwork-
  as-surveillance is a lean, not a proven pattern, and might turn out to be
  too passive (a document check) compared to Sector 9's more visible
  Watch-sweep dread.

## Revisit when

- The settlement ships and gets played — check whether permit-paperwork-as-
  surveillance actually reads as dread (principle 3's test) or as inert
  paperwork with no felt stakes.
- The recurring NPC figure gets played — check whether one figure is
  actually enough to carry principle 10's pressure-valve obligation, or
  whether it needs company sooner than "later" implies.
- If a future citizen build wants access to this area without shadow
  standing (e.g., a Function-based route), that's a deliberate reopening of
  the entry-gate decision above, not an oversight to patch quietly.
