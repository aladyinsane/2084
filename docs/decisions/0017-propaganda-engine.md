# ADR 0017 — The propaganda engine: giving the alert system a voice

- **Status:** Accepted
- **Date:** 2026-07-27

## Context

[future-features.md](../product/future-features.md#propaganda-engine) has parked the
propaganda engine since the very first brainstorm: "world news that reacts to aggregate
player action... the brainstorm's best liveness idea and a strong principle-8 machine
(world feels inhabited at low population)." It stayed parked because, before the grind
loops existed, there was nothing real to react to — "before v0.3 it would be a random
headline generator." That blocker has been dead since v0.6; the game now has sabotage,
couriering, circle projects, vouching, and archaeology all generating real signal.
Lauren picked this as the next solo-fun-adjacent pick after records archaeology (ADR
0016), favoring atmosphere and world-reactivity over a fourth near-identical grind loop.

Auditing what already exists first (the same move ADR 0015 made before building
anything): `watch.get_alert()` is already a real, live, aggregate signal — it rises on
detainment and decays on quiet sweep ticks, and `PatrolScript`
(`typeclasses/scripts.py`) already reads it to set patrol density
(`PATROL_BASELINE + alert`). That reactivity is **already real and already shipped** —
it's just silent. A player who notices more patrols on the street has to infer why;
nothing in the game ever tells them "the district is hotter than it was." This is
[fun-and-game-feel.md](../research/fun-and-game-feel.md) dullness #2 ("the machine is
invisible when it matters most... dread we already compute and then throw away"),
except at the world level instead of the individual sweep-roll level that near-miss
telegraphy (v0.8.5) already fixed there.

One real fork, presented to Lauren: should headline bulletins purely *narrate* existing
state, or should heavy sabotage/courier activity *also* push district alert up a little
beyond what detentions already cause — making the propaganda engine a genuine
difficulty-scaling mechanic, not just a narrator. **Pure narration chosen.** Real
feedback would mean a solo player's own grinding (sabotage for underground standing,
`research` for archaeology) could raise their own session's difficulty as a side effect
of playing the loops the game just built — a real risk for exactly the solo audience
this version is for. Pure narration gets the full "world reacts to you" payoff at zero
balance risk, since the thing being narrated (alert-driven patrol density) is already a
real, tested mechanic.

## Decision

New `world/propaganda.py`, following the same "cheap dispatch, shared hook points"
idiom as `circle_projects.py` and `errands.py`. A ServerConfig-backed counter
(`{"sabotage": N, "courier": M}`, reset each time a bulletin fires) tracks activity
*since the last bulletin*, not lifetime totals — this is a rolling tally, not another
leaderboard.

**Recording events:** one new line at each of the two hook points ADR 0013 already
established for `circle_projects.check()`:
- `commands/underground.py`'s `CmdSabotage` success path (next to
  `circle_projects.check(caller, "sabotage")`): `propaganda.record("sabotage")`.
- `world/underground.py`'s `deliver()` success path (next to
  `circle_projects.check(char, "deliver")`): `propaganda.record("courier")`.

No new event type for detentions — `watch.get_alert()` already *is* that signal, read
directly rather than duplicated.

**The script:** `PropagandaScript` (`typeclasses/scripts.py`), same shape as
`AssemblyScript`/`AmbienceScript`, registered at `server/conf/at_initial_setup.py`
alongside the other persistent scripts (install-time-only, same live-DB backfill
caveat as every other script added this way). On a slow tick
(`tuning.PROPAGANDA_TICK`, proposed: 240s), calls `propaganda.pick_bulletin()`:

- Reads the rolling sabotage/courier counts and `watch.get_alert()`.
- Picks a tier: **quiet** (near-zero activity, near-zero alert — usually no bulletin at
  all, occasionally a bland reassurance line, same "silence is a chosen beat" idiom
  `AmbienceScript` already uses); **low** (some activity, alert 0); **elevated** (real
  activity or alert ≥ 1); **high** (alert at `ALERT_MAX` or a heavy tally) — this tier
  is allowed to *truthfully* mention patrols being up, since `PatrolScript` already
  makes that true.
- Resets the rolling counters (alert is untouched — it's `watch.py`'s own state,
  decaying on its own schedule regardless of propaganda).
- Broadcasts the chosen line to every currently-connected citizen, same idiom
  `AssemblyScript._citizens()` already uses (`char.msg(...)` direct to sessions, not the
  `gridwide` channel object — this is the regime's own broadcast layer, not a citizen
  speaking, so none of `CHANNEL_EXPOSURE`'s cost applies).

**Content:** aggregate and anonymous only, by design — never names a citizen. The
one-liner that named this feature said "aggregate player action," and staying aggregate
keeps it consistent with the deniability idiom the rest of the underground-adjacent
systems already protect (ADR 0015 especially). A solo player, alone, still hears their
own sabotage reflected back as a "foreign saboteurs" headline nobody else is online to
share — principle 8's test, met by construction, since the broadcast list is just
whoever's currently connected.

## Consequences

**Good**

- Directly answers the parking lot's original pitch, and the blocker that kept it
  parked (nothing to react to) has been true to build against since v0.6.
- Gives an existing, real, already-tested mechanic (alert-driven patrol density) a
  voice for the first time, rather than inventing a new one — same fix shape as
  near-miss telegraphy, one level up.
- Zero new persistent lifecycle risk: the rolling counter is a since-last-bulletin
  tally, reset on every fire, with no lifetime accumulation to manage or compact.
- Solo-viable by construction: a lone player's own actions generate their own
  bulletins, no population threshold required.
- Zero balance change: chose pure narration explicitly, so this ships without touching
  difficulty, risk, or payout math anywhere in the game.

**Bad**

- **Two more direct broadcast messages to every connected citizen, on top of what
  `AssemblyScript` already sends.** At real population this could start to feel noisy
  if the tick is too aggressive; the quiet-tier's "usually say nothing" behavior is
  the guard against that, but the exact tick interval and quiet-tier threshold are
  picked, not measured, same caveat every other tuning number in this file carries.
- **Bulletins can go stale relative to reality if the tick is long and a session is
  short.** A citizen who logs in, sabotages once, and logs off before the next tick
  fires never hears their own headline — asymmetric with how `word`/the shadow ladder
  are always available on demand. Accepted: this is deliberately a broadcast/ambient
  mechanic, not a checkable one: `word` already covers "what's my standing," and this
  isn't trying to duplicate it.
- **Pure-narration was the safer of two real options, not the only defensible one.**
  The rejected "real feedback" shape is genuinely more thematically total (the state
  really does watch and react to everything you do) and isn't ruled out forever — see
  Revisit when.
- **Single-district scope, currently invisible.** Bulletins are Sector-9-wide because
  there's only one district; the design doesn't yet say what happens once
  [ADR 0012](0012-world-building-tooling-incremental-areas.md)'s per-district tooling
  ships a second one (per-district counters? Sector-wide only? undecided, not blocking
  this version).

## Revisit when

- A playtest shows bulletins landing as noise rather than texture — retune
  `PROPAGANDA_TICK` or the quiet-tier's silence threshold; tuning-only, no ADR needed.
- Someone wants the "real feedback" shape after all — that's a real balance change and
  needs its own explicit decision, not a quiet amendment to this one.
- A second district ships (ADR 0012's trigger) — decide then whether bulletins split
  per-district or stay Sector-wide.
