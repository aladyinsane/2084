# ADR 0019 — Opposed checks: `observe`, `forge`, and `sabotage` roll against an obstacle, not a flat constant

- **Status:** Proposed
- **Date:** 2026-07-31

## Context

[opposed-checks-for-existing-verbs.md](../research/opposed-checks-for-existing-verbs.md)
surveyed the space Lauren asked about (2026-07-30): resolving existing verbs with a
D&D-style roll compared against a skill, PvE only, roll hidden from the player. That
doc found the game already rolls dice in two places (`forge`, `sabotage` — flat
`chance = base + skill*bonus`, no opponent) but never lets an *obstacle* push back;
`observe`'s concealment check is a pure deterministic tier-gate. Lauren reviewed and
answered the doc's four open questions directly (2026-07-30):

1. Verbs: `observe` (concealment), `forge` (audit-sensitivity), `sabotage` (district
   alert) — the three the research doc worked examples for.
2. A shared, generic helper: `opposed_check(actor, skill_name, obstacle_difficulty)`
   in a new module, to keep balancing in one place.
3. Migrate `forge` and `sabotage`'s existing flat-chance formulas onto the new
   mechanic too, not just add it fresh to `observe`.
4. Prefers shape C (true opposed roll, both sides roll) from the research doc's three
   candidates, open to a mix.

This ADR specifies the actual mechanism and where each verb's `obstacle_difficulty`
comes from. Auditing what's actually available before inventing anything new, same
habit as every ADR since 0015: **`forge` has no existing per-record sensitivity
signal to key off of** — records (ADR 0005) carry `kind`, `type_key`, `redacted`, but
nothing numeric resembling "how audited is this." Rather than build a new scoring
subsystem records don't have today, `forge`'s obstacle uses the citizen's own
**exposure** (ADR 0003, 0–100, already tracked, already means "how closely the state
is currently watching you") — a hot citizen's paperwork draws more scrutiny than a
cold one's, which is closer to what "audit-sensitivity" was gesturing at than a new
per-record field would have been. This is a deviation from the research doc's literal
phrasing, made here, named explicitly rather than silently substituted.

## Decision

**New module, `world/checks.py`:**

```
def opposed_check(actor, skill_name, obstacle_difficulty):
    actor_roll = d20() + actor.skill(skill_name) // tuning.CHECK_SKILL_DIVISOR
    obstacle_roll = d20() + obstacle_difficulty
    return actor_roll > obstacle_roll   # ties favor the obstacle
```

`tuning.CHECK_SKILL_DIVISOR = 5` — skill is 0–50 (`tuning.SKILL_CAP`), so this gives
a **0–10 skill modifier**, matched deliberately to keep `obstacle_difficulty` in the
same rough 0–10 band across all three verbs below. That symmetry is the actual
"easier to balance in one place" Lauren asked for: one shared scale, not three
uncoordinated ones. **Ties favor the obstacle** — the state has home-field advantage,
consistent with principle 1 (the world is the antagonist, not a fair fight).

Skill still improves on every *attempt*, win or lose — unchanged from today's
`forge`/`sabotage`/`observe`, all of which already call `improve_skill` regardless of
outcome. This ADR only changes how the outcome is decided, not how skill is earned.

**Per-verb `obstacle_difficulty`:**

- **`observe` vs. concealment.** Concealed sensors (`typeclasses/gear.py`) gain a
  numeric `db.concealment` (replacing the boolean `db.concealed` — `concealment > 0`
  *is* concealed, `0` is the old `False`). `observe` only rolls `opposed_check`
  against sensors with `concealment > 0`; everything else is visible exactly as
  today, no check at all. Only the **concealment** gate changes — `OBSERVE_TIER_STATUS`,
  `OBSERVE_TIER_DETAIL`, and `OBSERVE_TIER_REPUTATION` stay deterministic tier-gates,
  untouched. Those are permanent capability unlocks ("you have learned to read device
  status"), a genuinely different kind of thing than "did you spot the hidden one
  today" — collapsing both into one mechanism would blur a real distinction, not
  simplify it.
  The game currently has exactly one concealed device (the honeypot's `seam`,
  `world/build.py`). Its `db.concealed = True` becomes `db.concealment = 9` — high
  enough that even a skill-cap citizen (modifier 10) is in a close, uncertain fight
  against it, not a guaranteed win the way skill ≥ 45 used to be.

- **`forge` vs. exposure.** `obstacle_difficulty = tuning.FORGE_BASE_DIFFICULTY +
  actor.db.exposure // tuning.FORGE_EXPOSURE_DIFFICULTY_DIVISOR`.
  `FORGE_BASE_DIFFICULTY = 2`, `FORGE_EXPOSURE_DIFFICULTY_DIVISOR = 10` — a cold
  citizen (0 exposure) faces difficulty 2; a maxed-out citizen (100 exposure) faces
  12. Applies identically whether editing an incident or striking a compactable
  tally — same call site, same formula, no per-record type distinction (none exists
  to distinguish on).

- **`sabotage` vs. district alert, plus the target's own sensitivity.**
  `obstacle_difficulty = tuning.SABOTAGE_BASE_DIFFICULTY + sensor.db.sensitivity +
  watch.get_alert() * tuning.SABOTAGE_ALERT_DIFFICULTY_SCALE`.
  `SABOTAGE_BASE_DIFFICULTY = 2`, `SABOTAGE_ALERT_DIFFICULTY_SCALE = 3` (alert is
  0–2, `tuning.ALERT_MAX` — contributes 0, 3, or 6). **The `sensor.db.sensitivity`
  term is an addition beyond what Lauren specified** (she named district alert only)
  — added here because `sabotage` already targets one specific sensor object that
  already carries a `sensitivity` value nothing currently reads for sabotage's own
  odds, and folding it in means a sharper device is a harder one to kill without
  inventing new data. Easy to cut back to alert-only if that's not wanted.

**Removed:** `FORGE_BASE_CHANCE`, `FORGE_SKILL_BONUS`, `SABOTAGE_BASE_CHANCE`,
`SABOTAGE_SKILL_BONUS`, `OBSERVE_TIER_CONCEALED` — superseded, not kept alongside the
new mechanism. `tuning.py` gains `CHECK_SKILL_DIVISOR`, `FORGE_BASE_DIFFICULTY`,
`FORGE_EXPOSURE_DIFFICULTY_DIVISOR`, `SABOTAGE_BASE_DIFFICULTY`,
`SABOTAGE_ALERT_DIFFICULTY_SCALE` (contributing.md rule 7 — gameplay numbers live in
`tuning.py` only).

**Roll stays hidden**, per the scoping decision made before this ADR: the player sees
an outcome (in-fiction, per principle 9 — never "you rolled a 14"), never the two
numbers that produced it. The skill number itself stays fully visible, same as
today — only the per-attempt roll is opaque, which is exactly principle 3's "opaque
in the moment, legible in trend" shape, not a new opacity the game didn't already
commit to.

## Consequences

**Good**

- One shared, shared-scale mechanism instead of three independent formulas —
  `forge`, `sabotage`, and `observe`'s concealment check are now the same nine-line
  function called three ways, which is what "easier to balance in one place"
  actually buys: change `CHECK_SKILL_DIVISOR` once, every verb using it moves
  together.
- Obstacles now genuinely push back using data the game already tracks (exposure,
  district alert, per-sensor sensitivity) instead of a flat tuning constant blind to
  world state — a hot citizen's forgeries get harder *because* they're hot, a
  sabotage attempt gets harder *because* the sector's already alert. That's new
  texture out of systems that already existed and previously didn't talk to each
  other.
- The honeypot's `seam` goes from "impossible below skill 45, guaranteed at or
  above it" to "always somewhat uncertain, increasingly favored with skill" — closer
  to what "a very practiced skill" was originally reaching for than a hard threshold
  ever was.

**Bad**

- **This is a real behavior change for `observe`, not just a new coat of paint.** A
  citizen who ground to skill 45+ specifically to permanently unlock concealed-device
  detection previously got exactly that: permanent, guaranteed. After this ADR,
  detection is never guaranteed, even at skill cap. That is a genuine downgrade of a
  specific promise the old system made, worth stating plainly rather than only
  describing the upside.
- **`forge` and `sabotage`'s actual success curves change at every skill level** —
  this is not a refactor that preserves old odds under a new formula, the odds
  themselves move. Old `forge` capped at 50% success regardless of anything else; new
  `forge` depends on the actor's exposure at the moment, and there's no guarantee the
  new curve lands anywhere near the old one at comparable skill. Unverified until a
  playtest, same as the `o_civic`-narrowing bet in ADR 0018.
- **Hidden rolls mean failure sometimes reads as "unlucky" rather than "not skilled
  enough yet"** — a different feeling than anything else currently in the game
  produces (skill-gated content in `observe`'s other tiers, `next`'s advice, grade
  thresholds — all of it currently either works or names exactly what's missing).
  This is the cost of the scoping decision (hidden roll) made before this ADR, not
  something this ADR can design around; it's inherent to the shape chosen.
- **The honeypot's `seam` needs a live-DB backfill** — `world/build.py` is
  install-time-only (standing project caveat); `db.concealed = True` on the already-
  built object needs to become `db.concealment = 9` by hand via `evennia shell`,
  same as every other build.py content change to an already-built world.

## Revisit when

- A playtest shows `forge` or `sabotage`'s new success rates feel meaningfully worse
  (or better, in a way that trivializes the risk) than the old flat-chance formulas
  did at comparable skill — the constants named above (`FORGE_BASE_DIFFICULTY`,
  `SABOTAGE_ALERT_DIFFICULTY_SCALE`, etc.) are first-pass estimates, not measured.
- Someone wants `sabotage`'s difficulty to drop the `sensor.db.sensitivity` term and
  go alert-only, matching Lauren's original answer exactly rather than this ADR's
  addition.
- A future verb wants the same shared `opposed_check` and its obstacle doesn't
  cleanly map onto an existing 0–100 or small-integer game value — the 0–10
  normalization convention this ADR establishes should hold, but the "what feeds
  `obstacle_difficulty`" question will need its own case-by-case answer each time,
  same as it did for these three.
