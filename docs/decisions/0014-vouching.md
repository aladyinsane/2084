# ADR 0014 — Vouching: a small, sanctioned stake on someone else's name

- **Status:** Proposed
- **Date:** 2026-07-24

## Context

[game-theory-of-the-grid.md](../research/game-theory-of-the-grid.md) names the
trust-machine backlog's fourth gap: our shallow-end players — new, cautious, not yet
ready to form or join a circle — have no trust-game participation at all below circle
stakes. The doc's own framing: "asymmetric stakes recruit the risk-averse... vouching
(staking a little standing on another citizen's clearance application) — small,
capped, recoverable — as the gateway drug to real conspiracy." Principle 10 ("oppression
is the fiction, not the UX") is the test this has to pass: a new player's first real
trust-game choice should be small and safe enough to actually take.

Read literally, the research doc's own example undercuts its own audience: Form C-1
(clearance) is a mid-game activity — a citizen needs a function, standing, and usually
a clean-ish file before it's worth pursuing. A brand-new player isn't near it. Tying
vouching *only* to C-1 would build a mechanic that never reaches the players it was
named for.

But the code already half-built the payoff. `functions.adjudicate_c1`'s rejection
reason, when a citizen has too many visible incidents, is literally `"character
references insufficient at this time"` — flavor text with nothing behind it today.
That's vouching's actual mechanical hook, sitting unused.

Three shapes were sketched and presented to Lauren:

1. **C-1-only.** Vouching only exists around a specific citizen's clearance
   application — stake returns plus a bonus on approval, forfeits on rejection or a
   later Section C. Most faithful to the literal research text, reuses the existing
   ceremony directly, but doesn't reach the stated audience (new players aren't near
   C-1 yet).
2. **General-purpose only.** `vouch <citizen>` works on anyone, anytime, for a small
   stake; forfeits if that citizen later completes a Section C confession. No C-1
   interaction, no baked-in payoff — pure trust-practice, whose only reward is the
   tutorializing value itself.
3. **Hybrid: general-purpose stake, C-1 payoff.** Same as option 2 for who can vouch
   and when — reachable from minute one — but an active vouch offsets one incident in
   `adjudicate_c1`'s threshold check, giving the existing "character references
   insufficient" text real teeth. The cheap, early trust-practice moment and the later
   payoff are decoupled in time: a new player vouches for someone they trust long
   before either of them is near clearance; it matters if and when the vouched citizen
   ever applies. **Chosen.**

## Decision

**The verb.** `vouch <citizen>` in `commands/civic.py`, help category `sector 9` (not
`the underground`) — this is a sanctioned act, not a covert one. No dead zone
required, no consent required from the target (the entire risk is borne by the
voucher). One active vouch per voucher at a time, same "one at a time" idiom
`char.db.errand`/`stash`/circle projects already use. `unvouch` (or `vouch withdraw`)
returns the stake in full at any time before forfeiture — that's the "recoverable"
half of the design.

**The stake.** `tuning.VOUCH_STAKE` (3) of **Ministry of Records** standing — sanctioned,
not underground. This is the load-bearing accessibility choice: underground standing
requires already having taken underground risks to earn, which would make a
"gateway drug for the risk-averse" require the exact risk-tolerance it's meant to
build. Ministry of Records standing is earned by `work`, the single safest action in
the game — reachable in a new player's first few minutes.

**State.** Plain `char.db` Attributes on both sides of the pair, no `ServerConfig`
registry needed (unlike `circles.py`/`circle_projects.py` — vouching is strictly
pairwise, not shared state across a group):
- Voucher: `char.db.vouch = {"target": <character>, "amount": N, "started": <time>}`
- Target: `char.db.vouched_by = [<voucher>, ...]` — a list, since more than one
  citizen can back the same person at once; each backer's own stake amount lives on
  their own `db.vouch`, not duplicated here.

**Forfeiture.** Hooked into `circles.betray()` (the confessor's own act, same site as
the stash and circle-project forfeiture from ADR 0011/0013): when a citizen completes
Section C as confessor, every backer in `confessor.db.vouched_by` forfeits their stake
outright (destroyed, not transferred — same idiom as the stash), and both sides'
Attributes clear. Being *named* in someone else's confession does **not** trigger
this — only the vouched citizen's own choice to name others does. A backer is being
asked to answer for the person's character, not for what happens to them.

**The C-1 payoff.** `adjudicate_c1` reads `bool(char.db.vouched_by)`: if the applicant
has at least one active backer, the incident threshold check tolerates one extra
visible incident (`tuning.CLEARANCE_MAX_INCIDENTS + 1` instead of the bare constant).
Flat +1 regardless of how many citizens are backing them — stacking multiple vouches
for a bigger offset is deliberately not a thing, keeping the bonus "small" the way the
research doc asked. Vouches don't otherwise interact with C-1's ceremony; they're not
consumed by an application either way (only Section C consumes them).

## Consequences

**Good**

- Directly answers the named gap with a mechanic actually shaped for its stated
  audience: cheap, immediate, sanctioned, no underground prerequisite.
- Reuses `functions.adjudicate_c1`'s existing (currently decorative) rejection text
  instead of inventing new flavor or a new ceremony.
- Reuses the exact forfeiture idiom `circles.betray()` already established twice
  (ADR 0011's stash, ADR 0013's circle project) — a third confirmation that "Section C
  costs the confessor's *other* relationships, not just their circle," is becoming a
  real, recognizable pattern rather than a one-off.
- Zero new persistent registries; plain Attributes on the two characters involved,
  simplest possible state shape for a pairwise relationship.

**Bad**

- **A player could vouch for a total stranger with no real information**, since there's
  no consent, no presence requirement beyond targeting, and no visible track record to
  judge from before backing someone (unlike `judge`, which reads real signal).
  Mechanically fine (the risk is the voucher's own to take badly), but worth watching
  whether it reads as a real trust decision in practice or just a free-standing-room
  action players spam without thinking, which would flatten the intended dilemma.
- **The C-1 payoff is invisible until it matters.** A citizen could carry an active
  backer for a long time with no in-fiction signal that it's doing anything, until the
  one moment (a C-1 application with 2 visible incidents instead of the usual 1) where
  it silently changes the outcome. No confirmation message at approval time currently
  distinguishes "you'd have passed anyway" from "the vouch is what saved you" —
  worth a follow-up if players report the mechanic feeling inert.
- **No signal to the target that they're backed**, or by whom, unless the voucher
  tells them directly (in-fiction: no notification is sent). Consistent with circles'
  "the Grid can't read this" secrecy elsewhere, but vouching isn't secret the way
  circles are, so this is a smaller, less examined design choice than it looks —
  revisit if it reads as a missing feature rather than a deliberate one.
- **Decoupled timing cuts both ways.** The payoff can land long after the trust
  decision, which is the whole point for reaching new players — but it also means a
  voucher's stake can sit at risk for a long time with no natural end besides
  `unvouch` or the target's own choices, unlike circle projects' bounded stages.

## Revisit when

- Real play shows vouching gets used reflexively (backing strangers with no
  information) rather than as a considered trust decision — candidate fix: require
  some minimum prior interaction, or surface more signal about the target first.
  Deferred rather than pre-solved as an unwarranted guess (`judge` already exists as
  the tool for reading someone before trusting them; whether vouching needs its own
  gate is a real playtest question).
- The C-1 payoff's invisibility gets a real complaint — candidate fix: a line in the
  approval message naming that a character reference helped, only when it was actually
  load-bearing (`adjudicate_c1` already knows the difference internally).
- Someone wants vouching to be visible to its target — that's a real design question,
  not obviously implied by "small, capped, recoverable," and shouldn't be added as a
  quiet amendment.
