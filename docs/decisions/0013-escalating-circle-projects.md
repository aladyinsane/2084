# ADR 0013 — Escalating circle projects: a growing pot only finishing pays out

- **Status:** Accepted
- **Date:** 2026-07-24

## Context

[game-theory-of-the-grid.md](../research/game-theory-of-the-grid.md) names the
trust-machine backlog's second gap: circles currently die after one betrayal payout,
because nothing makes continued membership worth more than Section C's immediate,
one-shot payoff. Axelrod's repeated-PD result the doc cites is specific about the fix —
cooperation stabilizes when the *shadow of the future* (the value of tomorrow's
continued play) exceeds today's defection payout. The stash (ADR 0011's confiscation
hook) started this by giving circles something to lose; this ADR is what finishes it: a
joint project whose reward grows as the circle invests in it, and which a completed
Section C confession forfeits entirely for everyone.

An unreviewed proposals doc
([game-theory-and-fun.md](../product/game-theory-and-fun.md), triaged into
[future-features.md](../product/future-features.md)) sketched a concrete three-stage
heist: sabotage two watchscreens, intercept a patrol while a comrade hits the Archive
Annex, then a payoff. Useful shape, but as written every stage requires multiple
circle members standing in position at once — checked against
[principle 8](../product/principles.md) ("alive at three players": every core loop
should still work "alone, at 1 a.m."), a fully synchronous multi-stage heist risks
going dormant for any circle that doesn't reliably get 2+ members online together,
which real circles (2-3 people, MUD population) often won't.

Three shapes were sketched and presented to Lauren:

1. **Fully synchronous, every stage** — matches the proposals doc as written. Highest
   drama, most faithful to the original sketch, but the principle-8 risk above is real
   and unmitigated.
2. **Fully solo-stackable, no synchronous requirement** — any member advances any
   stage alone; escalation comes purely from stage count. Safest against principle 8,
   but the coordination/trust angle — the actual point of a *circle* project instead of
   a solo errand chain — disappears; it would just be errands.py with a shared counter.
3. **Mostly solo, climax synchronous** — early/mid stages are solo-completable by any
   one online member at their own pace, cumulative across the whole circle; only the
   final stage requires two circle-mates present together at once, reusing the
   precedent `errands.py`'s "Four Hands" errand (`joint_visit` type) already
   established. **Chosen.**

Option 3 keeps the project alive through a circle's normal, staggered online pattern
while still demanding real coordination for the payoff — the moment that should feel
like a heist is the one moment that requires it.

## Decision

A new `world/circle_projects.py`, following `circles.py`'s existing shape (state in
the `ServerConfig` registry, keyed by circle slug — a project is circle property, not
character property, so it must survive any single member logging off, the same reason
the stash isn't `char.db`-scoped). One active project per circle, same "one at a time"
idiom as `char.db.errand` and `stash`.

Three stages, each reusing an existing verb rather than adding a new one (command-
surface-audit's standing rule: new features ride existing verb patterns):

1. **Casing** (solo, cumulative across all members): the circle's combined sabotage
   count reaches a threshold. Hooked into `CmdSabotage`'s existing success path in
   `commands/underground.py` — a new `circle_projects.check(char, "sabotage")` call
   alongside the existing payout, exactly the dispatch idiom `errands.check` already
   uses.
2. **The Run** (solo, cumulative): the circle's combined courier deliveries reach a
   threshold. Hooked into `underground.deliver()` the same way.
3. **The Split** (synchronous): two circle members physically present together in a
   dead zone at once, checked the same way `errands.py`'s `joint_visit` type already
   checks "Four Hands" — a member walks into a dead zone, the check fires, and if
   another circle member is already there, the project completes and pays out.

Management surface: `circle project start` / `circle project` (status), new
subactions on the existing `CmdCircle`, not a new command — matching `circle
form/invite/join/leave`'s existing pattern. Any current member can start a project;
starting requires no active project already running for that circle.

**Forfeiture:** a completed Section C confession (`circles.betray()`) wipes the
circle's active project the same way it already wipes the stash — no partial credit,
no salvage. This is the mechanic doing its actual job: the closer a project is to
paying out, the more a confession costs the confessor's own circle, which is exactly
"cooperation worth more than one defection" made concrete rather than asserted.
Leaving a circle (`circle leave`, not a betrayal) does **not** forfeit the project —
that stays a low-stakes exit, distinct from Section C, matching the distinction the
game already draws between the two.

**Payout:** underground standing, split evenly across every current member
(online or not, same as `circles.betray()`'s own member iteration) at completion.
Sized to matter — noticeably more than a single courier or sabotage payout, enough to
move the shadow ladder (`tuning.SHADOW_TIERS`) a full tier or close to one, so
finishing a project reads as a real jump, not a rounding error on the existing grind.
Exact numbers live in `tuning.py` at implementation time, following the file's own
convention.

## Consequences

**Good**

- Directly answers the named gap with the mechanism the research doc actually asked
  for: a pot that's worth more finished than confessed away.
- Zero new grind verbs — sabotage and couriering do double duty, so there's nothing new
  to teach in Tunnel B's chalk beyond the project's own management subcommand.
- The synchronous requirement is scoped to exactly one moment (the climax), which
  keeps every other stage compatible with principle 8's solo-viability test while still
  giving circles a reason to coordinate a login.
- Reuses established architecture wholesale: registry-keyed circle state (`circles.py`
  precedent), event-dispatch checking (`errands.py` precedent), forfeiture-on-betrayal
  (the stash-confiscation precedent from ADR 0011).

**Bad**

- **A circle that never gets two members online together at once cannot finish a
  project at all**, even though stages 1-2 might be long done. This is the accepted
  cost of choosing option 3 over option 2 — worth watching in playtest: if circles
  regularly stall at "The Split," the climax may need a fallback (a longer solo-only
  path, a lower bar than "present in the same room right now") rather than staying a
  hard requirement forever.
- **Cumulative solo stages can be dominated by one industrious member.** Unlike Section
  C's confession, which is a single citizen's choice, "the circle's sabotage count" is
  a shared pool anyone can fill — a circle of three where one person does all the
  casing still finishes the project and splits the payout evenly. Diegetically fine
  (division of labor is realistic); mechanically, it means the "trust" being tested
  really only shows up at the synchronous climax, not across the whole project.
- **No mid-project visibility into who's contributing what.** `circle project` (status)
  will show stage progress, but not a per-member breakdown — matching the "no roster
  the Grid can read" ethos of circles generally, but it also means free-riding (or
  suspected free-riding) has no in-game evidence trail, which could become its own
  source of (undesigned) circle friction.
- **Escalation is currently a fixed three-stage shape, not literally "escalating."**
  The name promises growing stakes; what's actually built is a fixed multi-stage chain
  with one payout at the end. A literal escalation (the pot growing with each
  *repeated* project a circle completes, e.g. a circle's second project pays more than
  its first) is not part of this decision and would need its own persistent counter and
  its own design pass.

## Revisit when

- A playtest shows circles regularly finishing stages 1-2 but never "The Split" —
  candidate fix: a time-boxed solo fallback for the climax stage, or lowering the
  "present at the same time" bar (e.g., within N minutes of each other rather than
  simultaneously).
- The free-rider question above gets a real complaint attached to it, rather than
  staying theoretical.
- Someone wants the literal "each successive project pays more" escalation named in
  the title — that's a superseding ADR, not an amendment to this one.
- Implementation reveals the sabotage/courier threshold numbers don't feel earned at
  circle scale (too fast, too slow) — a tuning-only fix, no ADR needed for that alone.
