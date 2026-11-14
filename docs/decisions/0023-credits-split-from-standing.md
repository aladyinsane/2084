# ADR 0023 — Credits: splitting the spendable half out of Standing

- **Status:** Accepted
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
(2026-08-26), the shape it picked, and the four open questions the first draft raised,
answered by Lauren the same day (recorded verbatim under Decision, below).

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

### Standing (trust — earned only, never spent, per faction)

Per faction (Ministry of Records / Ministry of Order / Ministry of Commerce / the
Underground), rising only from being useful, never falling from spending. This is
functionally today's `db.influence_earned`, promoted from a side-cache to the real,
primary ledger. Feeds everything that currently reads trust:

- `grades.merit()` (sanctioned factions only, unchanged rule)
- `word` / `underground.shadow_standing()`
- the `clearance(N)` and `shadow_standing(N)` lockfuncs
- vouching eligibility and the dossier's "Standing with institutions" line

### Credits (money — one pool, earned alongside Standing, spent freely)

**Decided:** a single fungible pool, `db.credits` — no sanctioned/underground split.
Earnable through sanctioned or unsanctioned action alike; spendable on sanctioned or
unsanctioned goods alike. Lauren's call directly: *"one pool, no sanctioned/
unsanctioned credits split. One can spend credits on unsanctioned things, and one can
earn credits in unsanctioned ways, but there should only be one form of fungible
credits"* and *"let's not overcomplicate credits, at least for now."*

This resolves the first draft's dossier-leak worry (open question 4) more cleanly
than the two-wallet design it replaces: **fungibility itself is the privacy
mechanism.** A single pool of money carries no memory of which sale earned which
credit — exactly like cash. The dossier-leak rule ([ADR 0009](0009-shadow-ladder-is-a-checkable-whisper.md))
protects the Underground *Standing* ledger and everything gated on it (Grade,
`word`); it was never about money, and Credits never feed Grade in this design at
all. Showing a single `Credits: N` line in the dossier reveals a citizen has money —
never how they got it, because there is no "how" recorded once it's in the pool. No
special-case display logic needed; this is actually simpler than the first draft's
two-wallet version, not just different.

Spending Credits never touches Standing. Earning Standing (being useful) is what
generates Credits as a byproduct — not a separate grind.

**Follow-on simplification this enables:** `tuning.GEAR_PRICES` and the Form C-1/C-2
fee constants no longer need a faction component for pricing purposes — a price is
just a number of Credits now, full stop. `commands/gear.py`'s `buy` docstring and
rejection message ("the price is N standing with {faction}") simplify to "the price
is N credits," dropping the per-Ministry attribution the old model needed. Flavor
text can still *name* which service is selling something; it just no longer changes
which balance the game checks.

### Vouching's stake: voucher's choice

**Decided:** `vouch <citizen>` lets the voucher choose which resource to stake.
Lauren's framing: *"what if we let the voucher choose whether to spend influence or
credits?"* — read here as choosing between the two axes this ADR creates (Standing
or Credits), since "influence" was the old name for the thing now splitting in two.

The two choices have genuinely different shapes, not just different labels, because
Standing (per this ADR) is never spent under normal play:

- **Stake Credits** (`vouch <citizen> with credits`, or the bare default — see
  below): identical to today's mechanic, just relabeled. `spend_credits(VOUCH_STAKE)`
  at vouch time (the money is really gone from your spendable balance the moment you
  commit); `unvouch` fully refunds it (`gain_credits`); the confessor's Section C
  forfeits it outright, same as today — it was already out of your balance, so
  forfeiture just means it never comes back.
- **Stake Standing** (`vouch <citizen> with standing`): a genuinely new state, since
  Standing has no spendable balance to draw down from. Nothing is deducted at vouch
  time — Standing keeps counting fully toward Grade/`word`/gates the entire time a
  vouch is outstanding. `unvouch` is a pure no-op (nothing was ever removed). Only on
  the confessor's Section C forfeiture does anything happen: `char.db.standing[faction]
  -= VOUCH_STAKE` — a real, permanent trust loss, applied once, at the moment of
  betrayal.
  - **This is a deliberate exception to `grades.py`'s documented invariant** ("Merit
    is lifetime, not balance... spending standing must never demote you"). That
    invariant is about *spending* — a citizen choosing to buy something. Forfeiture
    from someone else's betrayal is a different category: a real, narratively
    earned loss of trust, and letting it demote Grade is the more honest read of
    "you vouched for a traitor, Records genuinely thinks less of you now." Call
    `grades.check_reclassification(char)` after the deduction, same as every other
    Standing-affecting choke point.
  - Staking Standing is the higher-stakes, more "real trust on the line" option —
    fitting for a player who wants vouching to cost something that matters beyond
    money, at the cost of a possible Grade hit later if the vouch goes bad.

Default, if no resource is named: **Credits.** This preserves ADR 0014's original
"gateway drug for the risk-averse" framing — Credits are earned via `work`, the
single safest action in the game, and losing them never touches a citizen's
permanent trust record. A new player's first vouch should stay exactly as low-stakes
as it is today; staking Standing is an opt-in, higher-conviction choice for a player
who wants it, not the default floor.

### Naming collision fix

`char.db.standing` (function/clearance dict) → renamed to `char.db.civic_status`.
Frees "Standing" to mean the trust ledger everywhere in code, docs, and player-facing
text, matching what players already call it.

### v1 earn rule: no new balance pass

**Decided, as proposed:** every current `gain_influence(faction, amount)` call
becomes one call that credits **the same amount** to both Standing and Credits. The
split is structural in this ADR, not a rebalance — no tuning constant changes value,
only which ledger(s) it writes. Lauren confirmed: ship equal-split now, revisit
per-action weighting later, once the split itself has been played.

## Mechanics: full call-site inventory

Every current mutation site, and what it becomes. (Line numbers from the codebase as
audited 2026-08-26; will drift — this table is a work list, not a permanent record.)

| Site | Today | Becomes |
|---|---|---|
| `commands/civic.py:212` (`work`) | `gain_influence(faction, pay)` | `gain_standing_and_credits(faction, pay)` |
| `world/errands.py:232` | `gain_influence(spec["reward_faction"], amount)` | same helper |
| `world/underground.py:88` (`deliver`) | `gain_influence(UNDERGROUND, total)` | same helper |
| `world/underground.py:213` (`do_sabotage`) | `gain_influence(UNDERGROUND, pay)` | same helper |
| `world/circle_projects.py:151` | `member.gain_influence(UNDERGROUND, share)` | same helper |
| `world/archaeology.py:156,215` | `gain_influence(UNDERGROUND, ...)` | same helper |
| `world/archaeology.py:235` | `gain_influence("Ministry of Records", ...)` | same helper |
| `world/vouching.py:65` (refund) | `gain_influence("Ministry of Records", amount)` | `gain_credits(amount)` **only if staked as Credits**; no-op if staked as Standing (nothing was removed) |
| `commands/circles.py:499` (`flip`) | `spend_influence("Ministry of Commerce", cost)` | `spend_credits(cost)` |
| `commands/gear.py:157` (`buy`) | `spend_influence(faction, price)` | `spend_credits(price)` — `GEAR_PRICES` drops its faction component |
| `commands/civic.py:430,482,531` (`amend`/`redact`/`petition`) | `spend_influence("Ministry of Records", cost)` | `spend_credits(cost)` |
| `world/form_c1.py:95` | `spend_influence("Ministry of Records", CLEARANCE_FEE)` | `spend_credits(CLEARANCE_FEE)` |
| `world/form_c2.py:96` | `spend_influence("Ministry of Records", CLEARANCE_FEE)` | `spend_credits(CLEARANCE_FEE)` |
| `world/vouching.py:44` (stake) | `spend_influence("Ministry of Records", VOUCH_STAKE)` | `spend_credits(VOUCH_STAKE)` **or** deferred `standing[faction] -= VOUCH_STAKE` on forfeiture only — branches on voucher's choice |
| `world/underground.py:154` (`buy papers`) | `spend_influence(UNDERGROUND, PAPERS_COST)` | `spend_credits(PAPERS_COST)` |

Reads that switch from `db.influence`/`db.influence_earned` to `db.standing`:

- `grades.py:45` (`merit()`) — reads `char.db.influence_earned`; becomes `char.db.standing`. Formula unchanged, only the source dict renamed.
- `grades.py:57` — reads `char.db.standing.get("function_key")`; **this is the collision** — becomes `char.db.civic_status.get("function_key")`.
- `underground.py:242,249` (`shadow_standing()`) — reads `char.db.influence`; becomes `char.db.standing`.
- `lockfuncs.py:37,61` (`clearance()`, `shadow_standing()`) — `clearance()` already goes through `functions.clearance_level()` (reads `db.civic_status` post-rename, no other change); `shadow_standing()` reads `db.influence` directly, becomes `db.standing`.
- `dossier.py:93-94` — `standing.get("function"/"clearance")` → `civic_status.get(...)`.
- `dossier.py:115-118` — "Standing with institutions" section reads `db.influence`; becomes `db.standing` (same label, same meaning, now accurate). One new line beneath it: `Credits: N` — always shown, since a single fungible pool carries no leak risk (see Decision above).
- `commands/firsthour.py:124` — `db.standing` reference; becomes `db.civic_status`.
- `world/functions.py:83-86,99-103,155-157,195-197` (`assign_function`, `suspend_function`, `grant_c1`, `grant_c2`) — all mutate `char.db.standing`; becomes `char.db.civic_status`.
- `game/world/tests.py` — 53 `influence`/`gain_influence`/`spend_influence` references and 13 `db.standing` references, per the earlier audit. All need updating; this is the largest single piece of the diff and should be budgeted as such.

## Data model

```python
# typeclasses/characters.py — at_object_creation
self.db.standing = {}      # trust, per faction — was db.influence_earned
self.db.credits = 0        # was the spendable slice of db.influence — one pool, no split
self.db.civic_status = {}  # was db.standing (function/clearance) — renamed only
```

`db.influence` is retired entirely. New Character methods on `characters.py`, same
shape as today's `gain_influence`/`spend_influence`:

```python
def gain_standing(self, faction, amount): ...              # trust only, no Credits
def gain_standing_and_credits(self, faction, amount): ...  # the v1 default earn path
def gain_credits(self, amount): ...                        # Credits only (vouch refund)
def spend_credits(self, amount): ...                       # single pool, no wallet arg
```

Vouching's own state (`world/vouching.py`) gains one field to record which resource a
stake used, so `unvouch` and forfeiture know which branch to take:

```python
char.db.vouch = {"target": <character>, "resource": "credits" | "standing",
                  "faction": "Ministry of Records", "amount": N, "started": <time>}
```

`gain_standing`/`gain_standing_and_credits` keep calling
`grades.check_reclassification(char)` exactly where `gain_influence` does today.
Standing's forfeiture path (vouching, staked-as-standing) also calls it, per the
deliberate exception noted above — the one case in the game where a citizen's
Grade can move down without them having spent anything.

### Migration

No prior migration precedent exists in this codebase (nothing in
`docs/engineering/architecture.md` or `contributing.md` describes one — this would be
the first). Needed: a one-time `evennia shell`-run script that for every existing
`Character`:

- copies `db.influence_earned[faction]` → `db.standing[faction]` for all factions
- sums remaining `db.influence[faction]` (the spendable leftover) across *all*
  factions, sanctioned and Underground alike, into the single `db.credits`
- copies `db.standing` (old shape) → `db.civic_status`, then deletes the old
  `db.influence`/`db.influence_earned`/old-shape `db.standing` attributes

This needs its own short design note under `docs/engineering/` once implementation
starts — out of scope to fully spec here, flagged so it isn't forgotten.

## Curriculum (contributing.md rule 9)

- **Orientation Wing** (`o_civic` placard, most likely): needs a new line introducing
  Credits alongside the existing Standing/Grade teaching. Sanctioned track only.
- **Tunnel B chalk**: needs a line distinguishing Underground Standing (what `word`
  reports) from Credits (what gear and papers actually cost, same pool as anywhere
  else) — currently the single word "standing" covers both, so this chalk update is
  where the split becomes teachable in-fiction, not just in code.
- **`help standing`** ([flagged in future-features.md](../product/future-features.md#help-standing-clarity-pass--needs-a-specific-complaint-first)
  as needing "a specific complaint first" before rewriting) — this ADR is that
  complaint. Rewrite to describe trust only; add a new `help credits` entry for the
  spendable half, same "how it's earned / how it's spent / where to see it"
  structure the existing entry already uses.
- **`help vouch`** (or the `vouch` command's own docstring): needs the new
  `with credits`/`with standing` syntax and the real consequence difference between
  them spelled out, since choosing wrong is now a real decision, not flavor.

## Presentation (contributing.md rule 10)

No new border style or color. Dossier's new Credits line uses the same field-list
formatting as the existing Standing section (`dossier.py`'s plain `form_box()`-width
lines); no new palette entry — a Credits amount is a plain value, same treatment as
an existing Standing number, not a "good/bad outcome" requiring `|g`/`|r`.

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
- The single-pool Credits design is *simpler* than the first draft's two-wallet
  version, not just a different flavor of it — fungibility itself satisfies the
  dossier-leak concern with zero new display logic, and `GEAR_PRICES`/fee constants
  drop their per-faction component entirely.
- Vouching's resource choice gives players a real, legible decision (money now vs.
  trust later) instead of a single fixed cost, while keeping the safe default
  (Credits) exactly as low-stakes as vouching is today.

**Bad**

- **Broad diff.** ~14 mutation call sites, ~7 read sites, plus `tests.py`'s ~53
  influence references and 13 `db.standing` references. Every site is mechanical,
  but there are a lot of them, and the migration script is new infrastructure this
  codebase hasn't needed before.
- **Vouching now has two behaviorally different modes** instead of one fixed cost —
  more surface area to explain in help text and more branches to test
  (`vouch`/`unvouch`/forfeiture × {credits, standing}), where before there was one.
- **A new, narrow exception to "spending never demotes Grade"** exists now (Standing
  forfeiture from a backed citizen's Section C). It's deliberately scoped to exactly
  one trigger, but it's a real carve-out in a previously absolute rule, and worth
  watching in case it reads as confusing ("I didn't spend anything, why did my grade
  drop?") rather than as the intended "your trust was on the line and it broke."
- **No new balance work is done here on purpose** (the v1 equal-split rule), which
  means this ADR alone doesn't answer "is the economy well-tuned" — only "is the
  shape of the ledger honest." A follow-up balance pass is implied, not included.

## Revisit when

- Implementation surfaces a call site this audit missed (the inventory above was
  built from a codebase read, not exhaustive static analysis).
- Playtesting shows the equal-split v1 rule makes Credits feel meaningless relative
  to Standing (e.g., "I have plenty of money but nothing to spend it on faster than
  Standing accrues") or vice versa — candidate fix: per-action weighting.
- A playtester stakes Standing on a vouch, gets forfeited, and reports the Grade
  drop as confusing rather than earned — candidate fix: a more explicit message at
  forfeiture time naming that the trust-stake (not a purchase) is why Grade moved.
- Real play shows the Credits/Standing choice at `vouch` time gets ignored (everyone
  always takes the default) — worth checking whether the Standing option is worth
  its added complexity if nobody actually picks it.
