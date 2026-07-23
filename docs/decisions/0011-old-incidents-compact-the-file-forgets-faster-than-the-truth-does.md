# ADR 0011 — Old incidents compact; the file forgets faster than the truth does

- **Status:** Proposed
- **Date:** 2026-07-23

## Context

Lauren's ask: a long-term citizen's dossier grows without bound, because every
incident and every sensor-logged movement is a permanent, individually-numbered
Record object, and nothing ever removes one (ADR 0005's audit-trail promise).
Two fixes shipped alongside this ADR already reduce the *rate* of growth
(`fix/assembly-idler-policy`, `fix/papers-check-farming`), but rate isn't the
disease — a citizen who plays for months will still accumulate thousands of
routine records no matter how slow the drip.

The question this ADR answers: **why do we keep every prior incident at all,
and what would it mean to stop?** The answer is ADR 0005's whole thesis: the
record layer (what the file says) and the truth layer (what the audit trail
knows) are deliberately allowed to diverge, and that divergence — forge,
redact, launder — *is* the game. Deleting an old incident outright would
quietly repay the debt on the wrong side: it would erase truth, not just file
copy, which is backwards from every existing mechanic (amend/redact/forge all
touch the *file*, never the *truth*).

Lauren's proposed shape, which this ADR adopts: fold old, routine, untouched
incidents into a per-(citizen, incident type) **summary** carrying two
numbers — a **true count** (what really happened, never lowered by any game
action) and a **visible count** (what the file currently admits to, which
`petition`/`forge` can still lower, same as they lower any other entry today).
This keeps ADR 0005's promise at the *aggregate* level even though per-event
detail is lost once folded — a real, named cost (see Bad, below).

**Why the true count matters beyond bookkeeping:** Lauren's stated intent is a
future feature in the spirit of 1984's doublethink — a citizen with high
enough Underground standing should eventually be able to *see* the gap the
Ministry has edited into their own file, or another citizen's. That's out of
scope here, but it means the true count isn't a discardable implementation
detail; it has to be stored in a shape a future "acknowledge the gap" command
can actually read per citizen per incident type. Everything below is designed
with that reader in mind, even though it isn't built yet.

## Decision

### 0. Prerequisite: numbers get assigned at creation, not derived at display time

Today, `dossier.py` numbers incidents by `enumerate(records_for(...), 1)` —
position in a live-queried list. That's only stable because nothing is ever
deleted. Compaction deletes. So incident numbers move onto the record itself:
a new persistent per-citizen counter (`char.db.next_incident_number`) is
consulted and incremented every time a `kind="incident"` record is created;
the assigned value is stored as `record.db.number`. `incident_by_number()`
becomes a direct lookup instead of a positional one. This step is behavior-
preserving on its own — numbers come out identical to today's for any
citizen with nothing yet compacted — and can ship ahead of the rest of this
ADR as a low-risk, independently-verifiable step against the existing test
suite (`test_numbering_gap_survives_redaction` et al. shouldn't need to
change).

### 1. What compacts, and what never does

A new field, `type_key`, gets threaded through `records.add_record()`
(alongside the existing `tag` param from ADR 0010 — different field, same
"stop matching prose" lesson) and set at every call site: `"papers_check"`,
`"assembly_absence"`, `"assembly_attendance"`, `"sensor_movement"`,
`"detained"`, `"section_c_complete"`, `"section_c_clean"`, `"reclassified"`,
`"forge_fail"`, `"sabotage_fail"`, `"contraband_seized"`, and so on — one per
distinct thing the Grid records.

Only types on an explicit allowlist (`tuning.COMPACTABLE_INCIDENT_TYPES`) are
ever eligible, and it starts narrow: `papers_check` and `assembly_absence` —
the two confirmed high-volume, routine, narratively-weightless types found
while investigating this. Detainment, Section C (either outcome), sabotage
failures, courier seizures, and reclassifications never compact: they're rare
enough to never be a scaling problem, and they're exactly the entries with
outstanding narrative weight (ADR 0010 reads Section C off a live tag; a
reclassification is a named milestone). The allowlist is tuning data, not
code — widening it later is a one-line change, not a design decision.

A record is further only eligible once it's **untouched**: `len(record.db.audit)
== 1` (nothing but its own creation — never amended, redacted, or otherwise
interacted with). The moment a player engages with a specific entry, it's
pinned as an individual object forever. This is a simplifying rule, not a
loophole to close: routine entries are rarely worth the standing cost to
touch individually in the first place.

### 2. The summary record

A compaction pass (new script, `RecordCompactionScript`, interval
`tuning.RECORD_COMPACTION_INTERVAL`) finds, per citizen and per compactable
`type_key`, the **oldest contiguous run** of eligible records older than
`tuning.RECORD_COMPACTION_AGE` and folds them into one `kind="incident_summary"`
Record:

- `db.type_key` — which bucket this is
- `db.true_count` — how many really happened; only ever grows (each future
  routine incident of a compacted type, once it ages past the cutoff, adds to
  this instead of becoming a new individual object)
- `db.visible_count` — starts equal to `true_count` at fold time, *minus*
  however many of the folded originals were already individually redacted
  before compaction swept them up (their redaction work isn't lost)
- `db.range_start` / `db.range_end` — the incident numbers it now speaks for,
  frozen at fold time, so every number ever assigned stays meaningful forever
- `db.oldest_created` — for sort ordering, so it slots into `records_for()`
  where the oldest folded entry used to sit

Folding only ever eats from the *oldest* end and only ever grows forward
(this pass's own new arrivals extend the same bucket rather than minting a
second one), so a citizen ends up with at most one summary bucket per
compactable type, ever — not an accumulating pile of summaries.

### 3. Movement logs: simpler, because nothing reads them individually

`sensor_movement` records (`kind="observation"`) are not reachable by
`petition`/`forge` today — `incident_by_number()` only ever queried
`kind="incident"` — and the dossier already shows only the last 3. There's no
in-fiction manipulation surface to preserve, so these don't need the
true/visible summary machinery at all: past `tuning.MOVEMENT_LOG_RETENTION`
records for a citizen, the oldest are hard-deleted outright, no summary, no
audit-trail promise implicated (nothing was ever forgeable about them to
begin with). Assembly *attendance* (also `kind="observation"`, also currently
un-redactable) gets the same simple treatment.

### 4. `petition`/`forge` on a compacted bucket

`petition redact <N>` / `petition amend <N> = ...` / `forge <N> = ...`,
where `N` falls inside a bucket's `range_start`-`range_end`, decrement
`visible_count` by one at the existing `REDACT_COST`/`AMEND_COST`/
`FORGE_BASE_CHANCE` — no new pricing, no new player-facing syntax. `amend`
doesn't get to rewrite bespoke prose for a bucket (there's no single sentence
to rewrite); it's effectively identical to redact for a summary — one fewer
counted. Dossier rendering shows a bucket as `N-M. <type's display text> (V)`
using the *visible* count — the same shape the round-3 legibility rollup
already renders for consecutive live duplicates, just backed by real deletion
now instead of a display-only grouping. `true_count` is never shown anywhere
today; it's the hook the future doublethink feature reads.

## Consequences

**Good**

- Bounds per-citizen DB growth for the two confirmed worst offenders, for
  real (fewer live objects), not just a display trick.
- Preserves ADR 0005's promise at the level it actually matters: nothing a
  player *did* is ever erased from what the game knows happened, even though
  per-event timestamps within a compacted bucket are lost. The Ministry's
  file gets shorter; the truth doesn't shrink.
- Sets up Lauren's stated future feature (Underground-standing-gated truth
  visibility) with a real, per-citizen, per-type data shape to read from,
  rather than needing a second migration later to retrofit it.
- A pleasant side effect: `recent_incidents()`'s existing full-table
  `Record.objects.all()` gossip scan (a separate, already-flagged scaling
  concern, untouched by this ADR directly) shrinks over time as routine
  incidents age out of the live-object universe entirely.
- The allowlist and retention windows are tuning data — widening scope later
  never requires touching this ADR.

**Bad**

- **Real information loss.** Once folded, you cannot recover which specific
  day the 14th of 50 papers checks happened — only that there were 50, and
  visibly fewer if it's been petitioned down. This is a genuine narrowing of
  the audit trail's granularity, not just its display, and ADR 0005's exact
  wording ("nothing removes from it, ever") needs this ADR read alongside it
  as a qualification: the *count* never shrinks; the *event-level detail*
  inside a compacted bucket does, once.
- **New surface area, not a small patch.** A persisted numbering scheme, a
  new record kind, a new script, and a new tuning allowlist — this is
  comparable in size to ADR 0009/0010, not a bug fix.
- **The "untouched" pinning rule is permanent and a little arbitrary.** A
  citizen who once petitioned a single papers-check redaction years ago keeps
  that one specific object alive forever, while identical unredacted
  neighbors eventually compact. Harmless, but worth knowing it can happen.
- **The future truth-reveal feature is still undesigned.** This ADR commits
  to a storage shape that *can* support it, not to what it looks like, how
  standing gates it, or how it avoids leaking the whole game's secrets to
  anyone who grinds observation. That's real, separate design work later.
- **Compaction eligibility by type, not by content, means two different
  papers-check sentences can never both live in one bucket if the copy ever
  changes.** A future prose rewrite of "Papers checked in the street;
  cleared." would need to keep the same `type_key` to keep folding into the
  same bucket — another instance of the "don't match prose" lesson, this
  time self-inflicted if forgotten.

## Revisit when

- The doublethink/truth-reveal feature actually gets designed — this ADR's
  storage shape should be re-checked against whatever that feature turns out
  to need before assuming it's sufficient.
- The compactable allowlist needs widening (a playtest finds a third
  high-volume routine type) — should be a tuning change, not a new ADR.
- The "untouched only" pinning rule turns out to matter in practice (a
  playtest shows citizens routinely petitioning routine incidents specifically
  to keep them from ever compacting) — would need its own follow-up decision.
- `recent_incidents()`'s full-table gossip scan becomes a measured
  performance problem on its own — that's a separate fix this ADR only
  incidentally helps with, not a substitute for one.
