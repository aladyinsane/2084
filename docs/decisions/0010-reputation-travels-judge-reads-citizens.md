# ADR 0010 — Reputation travels: `judge` reads a citizen's Section C

- **Status:** Accepted
- **Date:** 2026-07-23

## Context

[game-theory-of-the-grid.md](../research/game-theory-of-the-grid.md) audited the
betrayal mechanics against the repeated-prisoner's-dilemma literature and named the
trust-machine backlog's first, highest-leverage gap: "a Section C signer can currently
walk into a new circle whose members never read his file." Axelrod's core result is
that cooperation only becomes rational in *repeated* play when a partner's history is
visible; ours currently isn't discoverable by other players at all — a defector's
confession lives in their own dossier and nowhere a prospective circle-mate would think
to look.

Two existing mechanics establish the idiom this should reuse rather than invent:

- `judge` (`commands/circles.py`) already reads an *informant's* hidden loyalty at
  sufficient `observation` skill — exactly the earned, diegetic shape the research doc
  asks for, just scoped to NPCs only.
- [ADR 0009](0009-shadow-ladder-is-a-checkable-whisper.md) (the shadow ladder)
  established the precedent for this class of reveal on this codebase: active, opt-in,
  no passive notification, no new persistent state where an existing number (or, here,
  an existing record) already answers the question.

Three shapes were sketched and presented to Lauren: extend `judge` to citizens (active
check, matches the existing idiom); an automatic hint fired on `circle invite`/`circle
join` (proactive, but breaks the earned-discovery pattern every other underground
mechanic follows and risks reading as an omniscient assistant rather than a trained
eye); or both. **Extend `judge`** was chosen.

## Decision

`judge <target>` now accepts a citizen present in the room, not only an `Informant`.
Gated on `caller.skill("observation") >= tuning.OBSERVE_TIER_REPUTATION` (40 — a new,
higher tier than `OBSERVE_TIER_DETAIL`'s 35, since reading a real citizen's actual
record is a bigger claim than reading an NPC's demeanor).

What it reads: whether the target's most recent Section C confession, if any and if
unredacted, was completed (named associates) or returned blank (kept faith). Detection
is by tag, not prose-matching: `detention.py`'s `confess names`/`confess alone`
branches now tag the record they create (`section_c_complete` / `section_c_clean`,
category `records.BETRAYAL_TAG_CATEGORY`) at creation time, via a new optional `tag`
param threaded through `records.add_record` → `watch.add_record_note`/`watch.release`.
`judge` then checks `records.records_for(target, kind="incident",
include_redacted=False)` for the most recent tagged entry, rather than parsing
`content` strings that prose rewrites could silently break.

Below the threshold: the same "you have learned nothing" line `judge` already gives
for an unreadable informant. No Section C record at all (never confessed, or every one
redacted): the same "can't tell" line too — a clean read and "never faced the choice"
are deliberately indistinguishable, so the underground can't prove a negative any
better than the Ministry can.

No fanfare, no auto-trigger on `circle invite`/`join`, no new command, no dossier or
grade interaction. Symmetric with the informant version: a citizen with a clean record
reads positively ("kept faith"), not just silence — matching `judge`'s own existing
good/bad symmetry and giving `confess alone` a legible payoff beyond the player's own
conscience.

## Consequences

**Good**

- Directly answers the named gap: reputation becomes actively discoverable by any
  citizen who's trained observation, not just gossip-dependent (`listen`'s queue
  chatter is still the passive channel; this is the active one).
- Reuses `judge`'s existing idiom exactly — no new verb, no new curriculum-audit burden
  beyond one chalk line noting citizens are now valid targets.
- Zero new persistent state beyond one tag per confession record; the read is a pure
  function of data the game already keeps, same shape `word`/Grade already established.
- Preserves the record-vs-truth thesis: a forged or redacted Section C reads clean,
  same as it already does in the subject's own dossier. No special-cased escape hatch,
  no new one either.

**Bad**

- **This is the first mechanic that lets one player surveil another's actual file, not
  just an NPC's.** Tonally correct for a surveillance-state game, but it's a real shift
  worth naming rather than waving through: a Section C mistake becomes a permanent,
  checkable stain (until redacted at the Annex) rather than something only the Ministry
  and the player's own conscience know. Combined with no expiry, "betrayal profitable
  once, costly as a career" (the design invariant the research doc names) has no
  natural floor here — worth watching for whether it reads as fair consequence or as
  griefing material once real players use it on each other.
- **Tag/prose can diverge.** The tag is set once at record creation and untouched by
  `amend()` (redaction correctly excludes the record from `records_for(...,
  include_redacted=False)`, so redaction works as intended) — but an amendment that
  rewrites `content` without redacting would leave the old tag in place, so a citizen
  who somehow got their confession's wording softened without a full redaction could
  still `judge` as tagged. Not currently reachable (nothing amends Section C entries
  specifically), but worth a guard if an amendment path ever targets them.
- **Purely opt-in, still.** Same limit as `word`: nothing prompts a player to `judge` a
  prospective circle-mate before inviting them. If reputation still doesn't travel *in
  practice* because nobody thinks to check, that's a habit failure, not a code one, and
  needs its own playtest gate rather than a code fix.
- **The observation threshold is picked, not measured** — same class of risk
  `SHADOW_TIERS` already carries; may need retuning once real play shows how often it
  actually fires.

## Revisit when

- A playtest shows nobody ever thinks to `judge` a prospective circle-mate before
  inviting them — candidate fix: a stronger chalk line, or `circle invite` itself
  suggesting the check (without auto-triggering the reveal — see the rejected shape
  above).
- Real play shows the permanent-stain read discourages ever choosing `confess names`
  even when it's the mechanically correct choice for the player, flattening the
  intended dilemma into a trap rather than a choice.
- An amendment path is ever added that targets Section C content directly — the
  tag/content divergence noted above needs closing before that ships.
