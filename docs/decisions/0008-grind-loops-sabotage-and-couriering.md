# ADR 0008 — The grind is sabotage and couriering, paid by the underground

- **Status:** Accepted
- **Date:** 2026-07-18

## Context

Lauren's requirement after v0.5: experienced mudders arrive wanting the mob-grind's
*shape* — a repeatable verb against a respawning target, numbers that move every
session, opt-in risk tiers, occasional jackpots — and ADR 0006 forbids the standard
implementation. Research ([grind-loops-without-killing.md](../research/grind-loops-without-killing.md))
extracted what the kill loop actually provides psychologically and confirmed that
none of it is the killing; dystopian peers (Sindome, Armageddon) thrive without the
corpse. Five candidate loops went to the parking lot; Lauren picked two.

## Decision

Two grind loops ship together as v0.6, both unsanctioned, both paying a new
**underground** standing ledger (the first non-Ministry faction):

1. **The sensor sabotage circuit.** Live devices are attackable-in-place:
   `sabotage <device>` is a skill check; success kills the device and pays
   underground standing (more when the room goes fully dark), failure is an
   incident and exposure. A **maintenance crew** (global script) repairs the
   oldest sabotage on a timer — the map itself respawns, which is what makes it
   a circuit rather than a heist. Concealed devices can only be targeted by an
   eye practiced enough to find them (`OBSERVE_TIER_CONCEALED`).
2. **Courier runs.** A broker in the ration queue hands out contraband parcels;
   destinations tier by visibility (tenement → alley → plaza → checkpoint), pay
   scales with the tier, and a cut of deliveries jackpot. The parcel is a real
   object in inventory. Seizure — the run's "death" — happens through the systems
   that already exist: a papers check finds it, a detainment inventories it, a
   scanner gate rolls for it. Seizure is an incident plus the lost job, never more.
3. **The underground pays, and sells.** Both loops pay standing with the
   underground; the first sink ships with the faucet — the broker sells **clean
   papers** (standing → exposure relief), so the loop closes inside one session.

Both loops are optional (principle: meaningful, never mandatory), single-player
viable (principle 8), and pass principle 9 — every verb is something a citizen of
Sector 9 would recognizably do, and nothing awards "experience points."

## Consequences

**Good**

- The DIKU muscle-memory session — log in, farm a circuit, watch numbers rise,
  log out — now exists without violating ADR 0006. The bestiary is the apparatus.
- Both loops *feed the existing systems* instead of sitting beside them: sabotage
  interacts with dead zones, `observe`, the honeypot, and alert; couriering runs
  on exposure, sweeps, patrols, and scanner gates. Risk tiers come free from the
  visibility map we already have.
- The underground ledger gives the unsanctioned economy a spine that cells
  (v0.5) and future cell benefits can hang from.

**Bad / accepted costs**

- **Farming dread.** Making the surveillance apparatus a renewable resource risks
  making it *comfortable* — the exact opposite of principle 1. Mitigation: failure
  stakes stay real (incidents are permanent until laundered; exposure feeds the
  same sweep that detains). If playtests show sabotage feels like mining, the
  repair crew gets teeth (investigations, stakeouts) before the loop gets nerfed.
- **The underground ledger has one sink.** Clean papers close the loop but a
  one-sink economy inflates; cell-level sinks are explicitly v0.7 material and
  this ADR is incomplete until they exist.
- **A skilled saboteur can kill the honeypot.** Cutting the Bolt-Hole's concealed
  seam (at high observation skill) disables the trap until maintenance finds it.
  Accepted deliberately: it's the single best payoff the observation grind can
  offer, and the repair crew makes it temporary.
- **Two more skills** (sabotage, couriering) widen the skill list; the ADR 0002
  convergence risk (every vet farms the same circuit) now has a concrete shape.
  Watch for it at every playtest gate.

## Revisit when

- Playtests show the circuit displacing the social game rather than funding it —
  the grind is meant to be the *between-sessions* activity, not the point.
- The underground ledger inflates (players hoarding standing with nothing to
  want): accelerate cell-benefit sinks rather than nerfing pay.
