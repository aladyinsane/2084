# ADR 0023 — Credits: splitting the spendable half out of Standing

- **Status:** Proposed (draft — not yet reviewed or accepted)
- **Date:** 2026-08-26

## Context

Two entries already sit in [future-features.md](../product/future-features.md) naming
this exact gap, unresolved:

- **["A 'credits' currency, earned and spent"](../product/future-features.md#a-credits-currency-earned-and-spent)**
  (Lauren's journal, 2026-07-26): flagged that a second currency needs "a real answer
  for why it's not just Influence under a new name" — and guessed the most likely real
  gap is "a currency spendable *across* factions, unlike Influence's per-institution
  ledgers" — explicitly marked as a guess, not confirmed.
- **["Too many separate advancement trackers"](../product/future-features.md#too-many-separate-advancement-trackers--fold-clearance-into-grade-or-something-else)**
  (Lauren's journal, 2026-08-01): named Grade, Clearance, standing, skills, and
  exposure as too many "am I advancing" numbers, and asked for "a real research pass
  on what's actually redundant versus what only *looks* redundant... before an ADR
  picks a shape."

This ADR is that research pass, done at Lauren's request in conversation
(2026-08-26), and the shape it picked.

**What an audit of the current code actually found** (per rule 4 — this has to trace
to something checkable, not vibes):

1. **Exposure and Visibility are not part of the confusion.** They're a clean pair
   (per-character heat / per-room static heat-cost), heavily used, well-telegraphed
   per principle 3, and nobody's complaint names them. Out of scope for this ADR.
2. **"Word" is not a fourth thing.** [ADR 0009](0009-shadow-ladder-is-a-checkable-whisper.md)
   built `word` as a pure, zero-state read over `db.influence[UNDERGROUND]` — the same
   number `shadow_standing()`'s lockfunc reads. There is no separate ledger to
   consolidate here; `word` is a presentation layer, already correctly designed as one.
3. **Grade is not a fourth thing either.** [`grades.py`](../../game/world/grades.py)'s
   own docstring says it plainly: it was built in v0.12 to solve "five progression
   currencies, no single number that says you're getting somewhere" — as a *derived,
   cached, display-only* view over `db.influence_earned` + errands + function +
   clearance. It stores nothing new and gates nothing. Grade is prior art for this
   exact problem, solved the right way once already.
4. **There is a real naming collision, unrelated to the "too many numbers" complaint.**
   `char.db.standing` (a dict holding `function`/`function_key`/`clearance`,
   `characters.py:35`, mutated in `world/functions.py`) and the thing players and the
   dossier actually call "standing" (`char.db.influence`, per-faction, labeled
   "Standing with institutions" in `dossier.py:116`) are two unrelated data
   structures that happen to share a name. Nothing in gameplay confuses them — only
   the name does.
5. **The one real mechanical conflation: `db.influence` does two jobs that fight each
   other.** Per faction, it is simultaneously *trust* (what Grade, `word`,
   `shadow_standing()`/`clearance()` lockfuncs, and vouching eligibility all read) and
   *purchasing power* (what `buy`, `petition`/`redact`/`amend`, Form C-1/C-2 fees, and
   `buy papers` all drain). [ADR 0003](0003-exposure-influence-not-xp.md) called this
   "a currency with sinks, not a score" on purpose — but a citizen who buys a piece of
   gear or pays a Records fee loses exactly as much standing as a citizen who did
   something wrong, an outcome the game never intends and never signals as equivalent.
   Tellingly, `commands/gear.py`'s own `buy` docstring already says the quiet part:
   *"Prices are in standing, the only currency Sector 9 has ever printed."* The
   fiction has already called this a currency; the mechanics haven't caught up.

**The actual finding:** the "too many trackers" complaint is real, but its cause isn't
five independent numbers — it's one number (`influence`) doing two jobs, plus a
naming collision that makes a second, unrelated number look like part of the same
mess. Grade and Word are not the problem; they're the template for the fix.

## Decision

**Split each faction's `influence` into two axes**, and rename the unrelated
civic-status dict out of the way.

### Standing (trust — earned only, never spent)

Per faction (Ministry of Records / Ministry of Order / Ministry of Commerce / the
Underground), rising only from being useful, never falling from spending. This is
functionally today's `db.influence_earned`, promoted from a side-cache to the real,
primary ledger. Feeds everything that currently reads trust:

- `grades.merit()` (sanctioned factions only, unchanged rule)
- `word` / `underground.shadow_standing()`
- the `clearance(N)` and `shadow_standing(N)` lockfuncs
- vouching eligibility and the dossier's "Standing with institutions" line

### Credits (money — earned alongside Standing, spent freely)

A new, genuinely spendable pool. Two wallets, not one, preserving the
dossier-leak rule ([ADR 0009](0009-shadow-ladder-is-a-checkable-whisper.md),
`tuning.UNSANCTIONED_FACTIONS`) with zero new logic:

- **Sanctioned Credits** — one fungible wallet, pooled across Records/Order/Commerce.
  This is the one real behavior change worth flagging on its own: today a `dampener`
  costs Underground standing specifically, and a Records fee costs Records standing
  specifically; after this change, sanctioned purchases draw from one pool regardless
  of which Ministry is selling. **Open question for Lauren**, not decided here — see
  below.
- **Underground Credits** — a separate wallet, never summed with or shown alongside
  sanctioned Credits, same partition `db.influence_earned` already enforces for Grade.

Spending Credits never touches Standing. Earning Standing (being useful) is what
generates Credits as a byproduct — not a separate grind.

### Naming collision fix

`char.db.standing` (function/clearance dict) → renamed to `char.db.civic_status`.
Frees "Standing" to mean the trust ledger everywhere in code, docs, and player-facing
text, matching what players already call it.

### v1 earn rule: no new balance pass

Every current `gain_influence(faction, amount)` call becomes one call that credits
**the same amount** to both Standing and Credits. The split is structural in this
ADR, not a rebalance — no tuning constant changes value, only which ledger(s) it
writes. This matters for the user's stated goal ("well-balanced... levers," not a
fresh balancing project): shipping the split alone, then separately deciding whether
some actions should weight one axis over the other, keeps this change reviewable in
isolation.

## Mechanics: full call-site inventory

Every current mutation site, and what it becomes. (Line numbers from the codebase as
audited 2026-08-26; will drift — this table is a work list, not a permanent record.)

| Site | Today | Becomes |
|---|---|---|
| `commands/civic.py:212` (`work`) | `gain_influence(faction, pay)` | `gain_standing_and_credits(faction, pay)` |
| `world/errands.py:232` | `gain_influence(spec["reward_faction"], amount)` | same helper |
| `world/underground.py:88` (`deliver`) | `gain_influence(UNDERGROUND, total)` | same helper, underground wallet |
| `world/underground.py:213` (`do_sabotage`) | `gain_influence(UNDERGROUND, pay)` | same helper |
| `world/circle_projects.py:151` | `member.gain_influence(UNDERGROUND, share)` | same helper |
| `world/archaeology.py:156,215` | `gain_influence(UNDERGROUND, ...)` | same helper |
| `world/archaeology.py:235` | `gain_influence("Ministry of Records", ...)` | same helper |
| `world/vouching.py:65` (refund) | `gain_influence("Ministry of Records", amount)` | **Standing only** — see open question below; a refund of a stake shouldn't mint new Credits |
| `commands/circles.py:499` (`flip`) | `spend_influence("Ministry of Commerce", cost)` | `spend_credits(sanctioned, cost)` |
| `commands/gear.py:157` (`buy`) | `spend_influence(faction, price)` | `spend_credits(sanctioned_or_underground, price)` |
| `commands/civic.py:430,482,531` (`amend`/`redact`/`petition`) | `spend_influence("Ministry of Records", cost)` | `spend_credits(sanctioned, cost)` |
| `world/form_c1.py:95` | `spend_influence("Ministry of Records", CLEARANCE_FEE)` | `spend_credits(sanctioned, ...)` |
| `world/form_c2.py:96` | `spend_influence("Ministry of Records", CLEARANCE_FEE)` | `spend_credits(sanctioned, ...)` |
| `world/vouching.py:44` (stake) | `spend_influence("Ministry of Records", VOUCH_STAKE)` | **Standing, locked** — not spent, not Credits; see open question below |
| `world/underground.py:154` (`buy papers`) | `spend_influence(UNDERGROUND, PAPERS_COST)` | `spend_credits(underground, PAPERS_COST)` |

Reads that switch from `db.influence`/`db.influence_earned` to `db.standing`:

- `grades.py:45` (`merit()`) — reads `char.db.influence_earned`; becomes `char.db.standing`. Formula unchanged, only the source dict renamed.
- `grades.py:57` — reads `char.db.standing.get("function_key")`; **this is the collision** — becomes `char.db.civic_status.get("function_key")`.
- `underground.py:242,249` (`shadow_standing()`) — reads `char.db.influence`; becomes `char.db.standing`.
- `lockfuncs.py:37,61` (`clearance()`, `shadow_standing()`) — `clearance()` already goes through `functions.clearance_level()` (reads `db.civic_status` post-rename, no other change); `shadow_standing()` reads `db.influence` directly, becomes `db.standing`.
- `dossier.py:93-94` — `standing.get("function"/"clearance")` → `civic_status.get(...)`.
- `dossier.py:115-118` — "Standing with institutions" section reads `db.influence`; becomes `db.standing` (same label, same meaning, now accurate). New line beneath it for Credits: sanctioned balance, and underground balance only if nonzero (keeps the leak rule: a citizen with zero underground activity never sees the concept surfaced).
- `commands/firsthour.py:124` — `db.standing` reference; becomes `db.civic_status`.
- `world/functions.py:83-86,99-103,155-157,195-197` (`assign_function`, `suspend_function`, `grant_c1`, `grant_c2`) — all mutate `char.db.standing`; becomes `char.db.civic_status`.
- `game/world/tests.py` — 53 `influence`/`gain_influence`/`spend_influence` references and 13 `db.standing` references, per the earlier audit. All need updating; this is the largest single piece of the diff and should be budgeted as such.

## Data model

```python
# typeclasses/characters.py — at_object_creation
self.db.standing = {}            # trust, per faction — was db.influence_earned
self.db.credits_sanctioned = 0   # was the spendable slice of db.influence, pooled
self.db.credits_underground = 0  # was db.influence[UNDERGROUND]'s spendable slice
self.db.civic_status = {}        # was db.standing (function/clearance) — renamed only
```

`db.influence` is retired entirely. New Character methods on `characters.py`, same
shape as today's `gain_influence`/`spend_influence`:

```python
def gain_standing(self, faction, amount): ...       # trust only, no Credits
def gain_standing_and_credits(self, faction, amount): ...  # the v1 default earn path
def spend_credits(self, wallet, amount): ...         # wallet = "sanctioned" | "underground"
def lock_standing(self, faction, amount): ...        # vouching's stake — see open Q below
```

`gain_standing`/`gain_standing_and_credits` keep calling
`grades.check_reclassification(char)` exactly where `gain_influence` does today —
Grade's choke-point contract doesn't change.

### Migration

No prior migration precedent exists in this codebase (nothing in
`docs/engineering/architecture.md` or `contributing.md` describes one — this would be
the first). Needed: a one-time `evennia shell`-run script, not a Django migration
(Evennia Attributes aren't schema-backed), that for every existing `Character`:

- copies `db.influence_earned[faction]` → `db.standing[faction]` for all factions
- splits remaining `db.influence[faction]` (the spendable leftover) into
  `db.credits_sanctioned` (summed across Records/Order/Commerce) and
  `db.credits_underground` (from the Underground entry)
- copies `db.standing` (old shape) → `db.civic_status`, then deletes the old
  `db.influence`/`db.influence_earned`/old-shape `db.standing` attributes

This needs its own short design note under `docs/engineering/` once the shape above
is confirmed — out of scope to fully spec here, flagged so it isn't forgotten.

## Curriculum (contributing.md rule 9)

- **Orientation Wing** (`o_civic` placard, most likely): needs a new line introducing
  Credits alongside the existing Standing/Grade teaching. Sanctioned track only.
- **Tunnel B chalk**: needs a line distinguishing Underground Standing (what `word`
  reports) from Underground Credits (what gear and papers actually cost) — currently
  the single word "standing" covers both, so this chalk update is where the split
  becomes teachable in-fiction, not just in code.
- **`help standing`** ([flagged in future-features.md](../product/future-features.md#help-standing-clarity-pass--needs-a-specific-complaint-first)
  as needing "a specific complaint first" before rewriting) — this ADR is that
  complaint. Rewrite to describe trust only; add a new `help credits` entry for the
  spendable half, same "how it's earned / how it's spent / where to see it"
  structure the existing entry already uses.

## Presentation (contributing.md rule 10)

No new border style or color. Dossier's new Credits line uses the same field-list
formatting as the existing Standing section (`dossier.py`'s plain `form_box()`-width
lines); no new palette entry — a Credits amount is a plain value, same treatment as
an existing Standing number, not a "good/bad outcome" requiring `|g`/`|r`.

## Open questions for Lauren (not decided by this draft)

1. **Sanctioned Credits: one pool, or still per-Ministry?** Pooling is what actually
   delivers "consolidate and simplify" for the spend side. The cost: `GEAR_PRICES`
   and fee constants currently differentiate *which Ministry* a price draws from;
   pooling collapses that distinction to just sanctioned-vs-underground. If
   institution-specific pricing is meant to stay meaningful (e.g., "expensive because
   Commerce specifically doesn't like you"), Credits should stay faction-scoped
   instead, and this ADR's biggest simplification claim shrinks accordingly.
2. **Vouching's stake:** today it spends 3 Records influence. Under the split, is
   that a Credits spend (money at risk) or a Standing lock (trust at risk, staying
   earned but temporarily unusable/unshowable until returned or forfeited)? The ADR
   0014 fiction — "staking a little standing on another citizen's name" — reads as
   trust, not money, which argues for a new locked-Standing state rather than
   reusing `spend_credits`. That's a real new state (earned / spendable / locked)
   this draft has not fully worked out; flagged rather than guessed.
3. **Earn-split weighting:** should every earn action really grant equal Standing and
   Credits forever, or are there actions that should read as pure-trust (assembly
   attendance) or pure-money (a courier's flat pay) once the split exists? Recommend
   shipping equal-split first and revisiting with real numbers, per the v1 rule
   above — but Lauren should confirm that sequencing is wanted rather than assumed.
4. **Does anything actually need two Credit wallets**, or would a single Credits pool
   (sanctioned and underground combined) still honor the dossier-leak rule if the
   *display* simply never shows underground-sourced credits in the dossier, even
   though they're fungible under the hood? Kept as two wallets in this draft because
   it's the more conservative reading of "the underground ledger... does not exist"
   (`grades.py`'s own docstring) — a citizen's underground money literally can't leak
   into a sanctioned purchase — but worth confirming that fungibility isn't wanted.

## Consequences

**Good**

- Directly answers both open parking-lot entries with a concrete, checkable design
  rather than leaving them as unresolved journal notes.
- Fixes the one real conflation found: spending no longer erodes trust. A citizen who
  buys gear or pays a fee no longer reads, mechanically, as equivalent to one who did
  something wrong.
- Does not add a fourth or fifth number to teach — Grade and Word are untouched in
  shape (they just rename their data source), and the total count of *player-facing
  concepts* goes from "Exposure, Visibility, Standing (two unrelated things secretly
  sharing a name), Grade, Word" to "Exposure, Visibility, Standing, Credits, Grade,
  Word" with Standing now meaning one clear thing everywhere.
- Matches player-facing fiction that already exists (`buy`'s own docstring) instead
  of inventing a new one.
- Zero new logic needed to preserve the dossier-leak rule — the two-wallet split
  reuses the exact `UNSANCTIONED_FACTIONS` partition already enforced for Grade.

**Bad**

- **Broad diff.** ~14 mutation call sites, ~7 read sites, plus `tests.py`'s ~53
  influence references and 13 `db.standing` references. Every site is mechanical,
  but there are a lot of them, and the migration script is new infrastructure this
  codebase hasn't needed before.
- **Three real open questions are not decided here** (pooling, vouching's stake
  shape, earn-split weighting) — shipping this ADR as-is without resolving them
  first would mean guessing at Lauren's intent on points that materially change what
  "simpler" means in practice.
- **Sanctioned pooling (if chosen) is a real behavior change**, not just a rename:
  institution-specific spending power goes away. Worth stating plainly since it's
  the biggest single simplification this ADR can deliver, and also the biggest
  thing it could get wrong if institution-specific pricing turns out to matter.
- **No new balance work is done here on purpose** (the v1 equal-split rule), which
  means this ADR alone doesn't answer "is the economy well-tuned" — only "is the
  shape of the ledger honest." A follow-up balance pass is implied, not included.

## Revisit when

- Lauren answers the three open questions above — this ADR should not move to
  Accepted until they're resolved, since the mutation-site table and data model
  both depend on the answers.
- Implementation surfaces a call site this audit missed (the inventory above was
  built from a codebase read, not exhaustive static analysis).
- Playtesting shows the equal-split v1 rule makes Credits feel meaningless relative
  to Standing (e.g., "I have plenty of money but nothing to spend it on faster than
  Standing accrues") or vice versa — candidate fix: per-action weighting, per open
  question 3.
