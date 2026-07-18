# ADR 0004 — Surveillance is event-driven world state, never an omniscient log

- **Status:** Accepted
- **Date:** 2026-07-17

## Context

The telescreen's terror is intermittency — you can't know *when* you're watched, only
that you might be (M1); and scrutiny is unevenly distributed by place and standing (M2).
Meanwhile Evennia's architecture punishes per-tick global simulation and rewards
event-driven checks ([evennia-capabilities.md](../research/evennia-capabilities.md)).
The fiction and the engine want the same design.

## Decision

- **Rooms have a visibility level (0–5)**, static per room, varying by district: the
  checkpoint plaza is a 5, the tunnels a 0.
- **Watching happens at events**: when you move, act, or speak somewhere visible, an
  exposure change is computed *then* — movement through a Vis-4 room costs more than a
  Vis-1 alley; exits can carry their own modifiers (scanners).
- **Sensors are objects, not ambience** (from v0.2): discoverable, spoofable,
  eventually sabotage-able things in rooms. The surveillance apparatus is *in* the
  world, per principle 1.
- **Consequences are sampled, not triggered**: a periodic Watch sweep samples players
  with probability scaled by exposure. High exposure makes trouble *likely and soon*,
  never a scripted certainty at a threshold.
- **Nothing keeps a total log.** The state's knowledge is its (fallible, editable)
  records — which is what makes ADR 0005's record-editing meaningful. An engine-level
  omniscient log would make forgery gameplay a lie.

## Consequences

**Good**

- Dread with fairness: direction certain, timing uncertain, trend always legible
  (prompt, patrol density). Exactly principle 3.
- Scales fine at MUD populations; no hot loops. The engine constraint (ADR 0001) is
  satisfied by design rather than by optimization.
- Sensors-as-objects turns the surveillance system itself into content: mapping dead
  zones is gameplay, and sabotage has an obvious implementation (the object stops
  contributing).

**Bad / accepted costs**

- **Tuning burden is permanent.** Visibility levels, modifiers, decay rate, sweep
  probability — all numbers with no principled first values. We will get them wrong
  first; playtest gates exist for this.
- **Randomness will occasionally look unfair** even when trend-telegraphed. One
  "that came out of nowhere" report outweighs our intuition (registered risk in
  [future-features.md](../product/future-features.md#known-risks-in-shipped-features)).
- **Sampled ≠ dramatic.** A hand-authored "the Watch kicks the door at the worst
  moment" beat is better drama than any dice roll; the sampler can't author irony.
  Scripted story events remain allowed on top of, not instead of, the sampler.
- **No omniscient log also means no perfect audit trail for *us*.** Debugging "why did
  I get swept" needs a dev-facing event trace that the fiction says doesn't exist.
  We'll build the trace and keep it out of the game's truth.

## Revisit when

- Playtests show the shallow end isn't (new players swept in low-vis districts), or
  the deep end doesn't scare (veterans ignore exposure entirely).
