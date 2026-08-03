# In-Universe Artifacts: Forms & Official Notices

> *"A form is not paper. A form is the shape the regime gives to a citizen's choices."*  
> — Archive Annex Archival Guide, Form 0-A

In Sector 9, bureaucratic forms are the primary medium through which the state measures, directs, restricts, and processes citizen existence. Below is the detailed analysis of the official forms and notices built into the game.

---

## Form 1-A: Notice of Arrival
* **Context**: Displayed to a fresh account upon first puppet login (`commands/firsthour.py`).
* **Tone**: Crisp, mandatory, welcoming without warmth.
* **In-Game Text / Meaning**:
  > `NOTICE OF ARRIVAL (FORM 1-A)`  
  > Informs the arriving citizen that Sector 9 has recorded their registration. Directs them to complete orientation, consult `next` whenever uncertain, and use `help` to inspect permitted actions.

---

## Form 2-B: Citizen Advisory (`next`)
* **Context**: Generated dynamically by the `next` command (`commands/firsthour.py`) based on live character state.
* **Tone**: Instructive, priority-ordered administrative guidance.
* **Functionality**:
  * Prioritizes active errands first.
  * Recommends completing orientation if incomplete.
  * Directs high-exposure citizens to cool down in low-visibility zones.
  * Suggests sanctioned errand givers in catalog order before subterranean leads.

---

## Form 9-A: Notice of Civic Reclassification
* **Context**: Issued upon dynamic adjustment of a citizen's Civic Grade (`world/grades.py`).
* **Tone**: Formal, celebratory or punitive, filed into the dossier.
* **Functionality**:
  * Accompanies promotion (e.g. Grade 6 to Grade 5 upon completing the Demonstration Corridor) or demotion (e.g. upon detention or loss of function).
  * Recorded directly into the citizen's audit trail at the Ministry of Records.

---

## Form 12-D: Notice of Remaining Entitlements
* **Context**: Screwed to the four white walls of the Ministry of Order Holding Cell (`commands/detention.py`).
* **Tone**: Bureaucratic mock-reassurance.
* **In-Game Text**:
  > `NOTICE OF REMAINING ENTITLEMENTS (FORM 12-D)`  
  > *The detainee may: `wait`.*  
  > *The detainee may: `confess`.*  
  > *The detainee may: `demand` (see reverse).*  
  > *The detainee retains the rights of speech (`say`), of reviewing their file (`dossier`), and of `help`, within reason.*  
  > *(Note: There is no reverse. The card is screwed flat to the wall.)*

---

## Form C-1: Application for Elevated Clearance
* **Context**: Accessible via `apply` at the Archive Annex (`world/form_c1.py`). Gates access to the Central Spire Lobby (Clearance C-1).
* **Tone**: Circular, demanding, self-incriminating.
* **Key Provisions**:
  * Requires a fee paid in Ministry of Records standing.
  * Demands affirmation: *"My file is accurate; it has always been accurate."*
  * Requires prerequisite Form 77 (Employment Verification).
  * Dirty dossiers fail the reference check, forcing citizens to undergo record laundering or forgery first — unless a fellow citizen has staked their own standing on the applicant's name (`vouch`, [ADR 0014](../../decisions/0014-vouching.md)), which the Ministry quietly tolerates as one extra incident's worth of character reference. No form exists for this; it isn't paper, which is exactly why it works below the level Section C operates at.

---

## Form C-2: Application for Further Elevation
* **Context**: Accessible via `apply` at the Archive Annex once Grade C-1 is already held (`world/form_c2.py`, [ADR 0021](../../decisions/0021-upper-spire-clearance-c2-through-c5.md)). Gates access past the Central Spire Lobby to Floor C-2.
* **Tone**: The same ceremony as Form C-1, read back with less patience — the Ministry notes the declaration section is "read more closely the second time."
* **Key Provisions**:
  * Requires the same filing fee as Form C-1, paid again in full; no discount for a returning applicant.
  * Cannot be filed without Grade C-1 already held — there is no shortcut past the first ascent to the second.
  * The reference check is stricter than Form C-1's: a single visible incident, tolerated at C-1, is enough to reject at C-2 (vouching still offsets it by one, same as Form C-1).
  * Approval is marked with a colorless stamp — an impression, not an ink — rather than the brass stamp Form C-1 uses; the Ministry does not repeat its ceremonies exactly at every tier.

---

## Form 77: Employment Verification
* **Context**: Required component of Form C-1 application (`world/form_c1.py`).
* **Tone**: Restrictive, function-locking.
* **Functionality**:
  * Verifies that the citizen holds an active, unsuspended Function (Clerk, Auditor, Steward).
  * If a citizen was recently detained, their function is suspended, causing Form 77 to reject until re-verification occurs.

---

## Section C: Confession & Betrayal Document
* **Context**: Presented to detained circle members during holding cell processing (`commands/circles.py`).
* **Tone**: Coldly transactional, social destruction.
* **Choices & Mechanical Impact**:
  * **`confess alone`**: Detainee absorbs full interrogation penalties, maintaining loyalty to their underground circle.
  * **`confess names`**: Detainee lists circle comrades. The detainee is released immediately; named comrades receive +25 Exposure each and a permanent betrayal incident in their dossier.
  * **Reputation Mechanics**: Signed Section C confessions leave an indelible stain. Through `judge`, other citizens can observe a character's history of Section C betrayals.

---

## Land Survey & Water Allotment Records
* **Context**: Filed against a `Parcel` object, not a citizen — the same Ministry of Records ledger that keeps citizen incidents, pointed at land instead of a person (`typeclasses/land.py`, `world/records.py`, [ADR 0022](../../decisions/0022-outside-the-grid-shadow-standing-gate.md)). Petitioned at the Archive Annex like any other record (`petition amend survey = ...`, `petition redact allotment`); forged only out past the wire, where nothing watches (`forge survey = ...`, `forge allotment = ...`).
* **Tone**: The same bureaucratic finality as a citizen's file, aimed at a field and a cistern instead of a person.
* **Key Provisions**:
  * A survey record states a yield figure and a boundary; an allotment record states a draw rate. Both start on file reading "within Ministry projection" — a number the Ministry considers final, whether or not the land agrees.
  * Standing to petition or forge a parcel's record belongs to whoever holds it (`db.owner`), not to the citizen the record happens to name — there is no such citizen. A landholder amends or forges records about *their* land, the same authorization shape as a citizen amending their own incidents, aimed at a different kind of subject.
  * Falsifying a survey carries the same risk forging a citizen incident does: caught, it becomes "Suspected document tampering" on the forger's own file, the same entry a failed citizen forgery leaves.
