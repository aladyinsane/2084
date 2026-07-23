# ADR 0009 — The shadow ladder is a checkable whisper, not a file

- **Status:** Accepted
- **Date:** 2026-07-22

## Context

The [ten-persona playtest](../research/playtest-2026-07-20-ten-personas.md) (finding 4):
rutherford ended his session with underground standing, a completed courier run, and an
incident — real progress — with no way to see it. The only readout was one line the
broker recites mid-`carry`. "The v0.12 research applies verbatim to the shadow economy:
progress you can't see doesn't motivate." Ranked as the third next-step candidate,
explicitly deferred pending its own design pass; the [round-two playtest](../research/playtest-2026-07-22-round-2.md)
re-confirmed it as still open and unchanged.

Two hard constraints from prior decisions:

- **The dossier-leak lesson**, learned twice ([v0.12](../product/roadmap.md#v012--citizen-grades-the-familiar-ladder)):
  underground standing must never feed the sanctioned grade or appear in `dossier` —
  `tuning.UNSANCTIONED_FACTIONS` already excludes it, and that stays true.
- **The goal-gradient research** ([the-first-hour.md](../research/the-first-hour.md)),
  already proven out by Grade (v0.12): named tiers with a visible "X to go" motivate far
  more than a bare number. Grade's shape (`grades.py`: thresholds, `grade_for_merit`,
  `next_review`) is the template.

Three shapes were sketched and presented to Lauren:

1. Reword the existing NPC lines only (broker's carry menu, sabotage/deliver) to name a
   tier instead of a bare number. Cheapest, purest "whispered, never filed" — but still
   entirely passive; a player only learns their tier when those specific verbs happen to
   fire.
2. A new checkable command, gated by room visibility the same way `recruit` already is.
3. Option 2 plus an unprompted milestone whisper on tier-up, mirroring Grade's FORM 9-A
   fanfare — the single mechanism the v0.12 research found landed best, at the cost of a
   tracked "last acknowledged tier" flag and hooks into every underground payout site.

## Decision

**Option 2.** A tier table, purely derived (no new stored state) from
`caller.db.influence[tuning.UNDERGROUND]`:

| Standing | Tier |
|---|---|
| 0-4 | a face nobody's placed yet |
| 5-11 | a runner |
| 12-24 | reliable |
| 25-44 | trusted |
| 45+ | one of the old hands |

A new command, `word` (aliases: `rumor`, `reputation`), in `commands/underground.py`,
`help_category = "the underground"` — taught only in the chalk and `help all`'s
underground index, never the Wing, per the curriculum-audit rule. Gated by visibility
exactly like `recruit` (a new tuning constant, `SHADOW_LADDER_MAX_VISIBILITY`, even
though it starts equal to `RECRUIT_MAX_VISIBILITY` — tunable independently later):

- Asked somewhere too watched, the reply deflects ("Not here. Not where anyone's
  watching you ask.") — reputation is a dark-corners thing, same as recruiting.
- Asked somewhere dark enough, an NPC-voiced line names the current tier and the gap to
  the next one, Grade-style ("word on the street: you're reliable. A little more, and
  you're trusted.").

No fanfare, no milestone hook, no change to `dossier` or `grade`. Option 3's proactive
whisper is explicitly parked, not built now.

## Consequences

**Good**

- Answers the finding directly: a citizen with underground standing can now check it on
  demand, not just stumble across a mention of it.
- Zero new persistent state — the tier is a pure function of a number the game already
  tracks, same shape as `grades.merit`/`next_review`.
- Reuses an idiom the game already has (`recruit`'s visibility gate) instead of
  inventing a new one, and keeps the underground's "no ledger says so" fiction intact —
  the tier is spoken, never displayed in a file.
- Passes principle 9: asking around about your own reputation is something a citizen of
  Sector 9 would recognizably do.

**Bad / accepted costs**

- **Purely opt-in discovery.** Nothing points a player at `word` proactively.
  `nomatch.py`'s "stats" instinct line was a candidate place to mention it, but doing so
  for every citizen — including ones who have never touched the underground — would leak
  that the underground exists to precisely the newbie audience the chalk-only curriculum
  rule exists to protect. Discovery stays exactly as unsanctioned as the rest of the
  underground: found in the chalk, or not at all.
- **No milestone fanfare.** The moment a citizen actually crosses a tier is invisible
  unless they happen to ask. This is the single biggest piece of the v0.12 research's
  finding, deliberately left for a later phase (option 3) rather than built now — the
  tier table needs to prove its thresholds feel right in play before the more invasive
  hook-every-payout-site version is worth the surface area.
- **Tier prose can go stale.** If underground payout tuning changes materially, the tier
  names and thresholds need a deliberate revisit, same risk `GRADE_THRESHOLDS` already
  carries.

## Revisit when

- A playtest reports never discovering `word` exists, or discovering it only very late —
  candidate fix: a chalk line in Tunnel B naming it explicitly (chalk is the sanctioned
  place to teach unsanctioned verbs; a nomatch hint would not be).
- The tier table stops feeling like it's moving at a reasonable pace against real
  playtest sessions — revisit thresholds before reaching for option 3's fanfare.
- Lauren decides the milestone-whisper (option 3) is worth its added surface area after
  option 2 ships and settles.
