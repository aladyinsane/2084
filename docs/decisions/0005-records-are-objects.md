# ADR 0005 — Records are first-class objects, and the record is not the truth

- **Status:** Accepted
- **Date:** 2026-07-17

## Context

The novel's central machine is the editable past: the regime's records *are* reality
because nothing else persists (M4). The prior drafts proposed "memory objects" with
edit/erase/fabricate operations. The trap in that proposal: if editing a record simply
*changes the data*, then the game itself forgets the truth — and gameplay about lies
needs somewhere the truth still lives.

## Decision

- **Records are game objects** (Evennia typeclass), not fields: an observation, a
  dossier entry, a work evaluation, a denunciation. Each carries origin, timestamp,
  author, subject, and content.
- **Two layers, permanently distinct:**
  - the **record layer** — what the state's files say. Fully mutable in play: clerks
    amend, forgers fabricate, purges redact.
  - the **truth layer** — an append-only audit trail beneath every record: what it said
    before, who changed it, when. Invisible in-fiction except through high-clearance or
    investigative gameplay; never editable by anyone, including admins-in-fiction.
- **Editing the record is the gameplay; the audit trail is the ground truth** that
  makes investigation, blackmail, and vindication possible later.
- A character's **dossier** is a view over the record layer (ADR 0002: identity as
  record) — so record-editing services literally edit who the state thinks you are.

## Consequences

**Good**

- "The record is not the truth" (principle 4) becomes a data model instead of a slogan.
  Every forgery creates evidence-of-forgery *somewhere*, which is future content.
- Unpersoning, rehabilitation, and frame-jobs all reduce to record operations — one
  mechanic, many stories.
- Append-only audit mirrors the immutability rule this repo already applies to its own
  ADRs. The methodology and the game agree.

**Bad / accepted costs**

- **Unbounded growth.** Append-only + every observation an object = a database that
  only gets bigger. Accepted for MUD scale (thousands, not billions, of rows);
  archival/pruning of *audit* entries would need its own ADR because it violates the
  layer's promise.
- **Abuse surface.** Player-reachable fabrication invites griefing-by-paperwork —
  framing a newbie for fun. Mitigations owed by v0.3: fabrication costs (influence,
  exposure), and the audit trail itself as the appeal mechanism. Social PvP is intended
  (principle 6); *unanswerable* social PvP is not.
- **Complexity tax on every future feature.** Anything that "happens" must decide what
  gets recorded, by what observer, into which file. This is the price of the game's
  central mechanic being epistemology.
- **Deferred implementation risk.** This ADR is accepted now but lands in v0.3; the
  v0.1 dossier is a stub over plain attributes. The risk of "temporary" stubs
  calcifying is known — the roadmap names the replacement explicitly.

## Revisit when

- Object counts or query times make the object-per-observation grain untenable —
  fallback is coarser records (per-day summaries), not abandoning the two layers.
