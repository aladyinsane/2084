# In-Universe Artifacts: The Unperson Case Files

> *"The file is accurate, and has always been accurate. It does not follow that the file
> is complete."*
> — attributed to no one in particular, Archive Annex, marginalia

The Archive Annex's public terminals hold decades of what the Ministry of Records
decided was worth keeping. Most of a shift spent `research`-ing them is exactly as dull
as it looks: requisitions, transfers, ledger corrections. Occasionally, a citizen with
patience — and a reason to keep looking — notices that a handful of records don't quite
agree with each other, and that the disagreement has a shape.

Three such shapes are catalogued below. Code implementation:
`game/world/archaeology.py`'s `NAMED_CASES`.

---

## The Signalman
* **Context**: A rare `research` draw at the Archive Annex, gated behind the same
  fragment-collection loop as the generic (unnamed) cases, but hand-authored rather than
  drawn from the atomic fragment pool.
* **Fragments** (collected in any order, one per qualifying draw):
  1. A maintenance log for a lamp fixed the same night its keeper was reassigned.
  2. A transfer order for "the signalman, Tenement Row," destination field left blank.
  3. A line in an old sweep report: *"lamp restored; keeper's file closed; matter
     concluded."*
* **The Reveal**: The lamp that used to flicker outside Tenement Row was fixed the same
  week its keeper stopped answering to his own name. The transfer order that should have
  sent him somewhere was never completed — the destination field is blank, and stays
  blank, in every copy the Annex holds. The sweep report's three words do the work of an
  explanation the file never gives. The lamp has not flickered since.
* **Thematic Note**: The tidiest of the three — a single administrative loose end (an
  incomplete transfer) standing in for a person. Companion piece to the Tunnel B chalk's
  own "ask yourself who keeps the bolt-hole nice."

## The Second Desk
* **Context**: As above.
* **Fragments**:
  1. A staffing chart for the Assignment Hall showing two names at one desk and one
     chair.
  2. A payroll entry paying a second clerk at that counter, for a citizen the current
     roster has no record of.
  3. A note clipped to an old chart: *"desk reassigned; duplicate entry corrected."*
* **The Reveal**: For eleven months, two names drew pay from one counter, and the chart
  shows one chair. The Ministry's own correction calls it a duplicate entry — an error in
  the ledger, the kind that gets fixed and forgotten. The correction is dated a full year
  after the second name stops appearing anywhere else at all.
* **Thematic Note**: The only case set inside the Assignment Hall itself — the
  Ministry's own bureaucracy erasing one of its own clerks, filed as a rounding error in
  its own paperwork.

## The Uncounted Census
* **Context**: As above.
* **Fragments**:
  1. A census page listing a household of three, and a ration allocation for two.
  2. A school attendance record with a child's name crossed through, re-entered, crossed
     through again.
  3. A closing note: *"household corrected; census stands."*
* **The Reveal**: The census said three. The ration book said two, and had said two for
  longer than the census had said three. A child's name goes in and out of a school
  register like a held breath, and the closing note doesn't say which number was wrong —
  only that the household is "corrected."
* **Thematic Note**: The only case centered on a child, and the only one where the
  contradiction is never resolved even by the file's own closing note — the ambiguity is
  the point, and is left standing on purpose.

---

## Design Notes (for maintainers)

- These three are deliberately **not** the whole catalog. `archaeology.py`'s own module
  docstring expects this table to grow the way `errands.py`'s catalog did — this file
  should grow with it. Add a matching entry here whenever `NAMED_CASES` gains a new key.
- Unlike the generic (unnamed) cases — recombined at random from an atomic fragment pool,
  and not otherwise catalogued anywhere — a named case is authored, finite, and
  discoverable independently by every citizen who finds it (solved once *per citizen*,
  not once for the server; see ADR 0016's Consequences section for why).
- None of the three currently cross-reference a *specific* event already documented in
  [historical-background.md](../historical-background.md) — they're standalone, in the
  same voice, rather than retconned onto existing lore. A future entry that deliberately
  ties into something already documented there is a natural way to grow the catalog.
