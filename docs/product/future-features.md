# Future Features / Parking Lot

Ideas worth remembering, with the reasoning attached. **Being on this list is not a
commitment.** This document exists so ideas are *remembered* rather than *accreted*.
Killing something is a valid outcome; record it here when it happens.

Also see [Known risks in shipped features](#known-risks-in-shipped-features) at the
bottom — soft spots we shipped on purpose, recorded so we revisit them deliberately.

---

## Strong candidates

### ~~ASCII map (planned, deliberately not v1)~~ — LEFT THE LOT (v0.8, 2026-07-19)

*Shipped on request after the first human playtest, via door #1 below
(`ingame_map_display` subclass, `commands/map.py`) — the grid-consistency
bet paid exactly as designed. The "thematically interesting version"
(maps as in-fiction seizable objects, accuracy as gameplay) remains parked
below; visibility-digit rendering delivered a slice of it early.*

An in-game `map` command rendering the local area as ASCII. We built one before (the
Another World project); that experience informs this, but the design here is **fresh,
against Evennia's actual options** — not a port.

The three doors, per [evennia-capabilities.md](../research/evennia-capabilities.md):

1. **`ingame_map_display` contrib** — derives the map dynamically from the room/exit
   graph. No coordinates, no migration; needs only compass-consistent exits. **Default
   choice** when this feature comes up.
2. **`xyzgrid` contrib** — puts the world on a real coordinate grid with pathfinding
   and radius-limited map views. Strictly more powerful, but the world must *live* on
   the grid; adopting it late is a rebuild of the world files, not a toggle. Only worth
   it if we someday want pathfinding NPCs patrolling realistically — which, note, a
   surveillance game might.
3. **`mapbuilder` contrib** — draw-the-map-to-build-the-world. A building tool, not a
   display; compatible with either choice above, usable whenever building outgrows
   hand-written batch code.

**What we did now to keep all doors open:** [ADR 0007](../decisions/0007-room-graph-grid-consistent.md)
mandates grid-consistent geometry from the first room, so the cheap option stays cheap.

**Why not v1:** (a) a small starting district doesn't need one; (b) early disorientation
is tonally *useful* — you learn the Grid the way its residents do; (c) picking display
tech now would lock geometry decisions we don't need to make yet.

**The thematically interesting version, when we get there:** maps as in-fiction objects.
The Ministry's official map (idealized, missing the places you actually need) versus
your own annotations (contraband, shareable, seizable). Map *accuracy* as gameplay —
which turns a comfort feature back into principle 1's "the world is the antagonist."

### Propaganda engine
World news that reacts to aggregate player action: sabotage begets "foreign saboteurs"
headlines, paranoia, patrols. The brainstorm's best liveness idea and a strong
principle-8 machine (world feels inhabited at low population).
**Why not now:** needs enough player actions to react *to*; before v0.3 it would be a
random headline generator.

### Secret languages and coded speech
Ciphers, slang, hidden meanings on monitored channels (M9). Rich, unique territory.
**Why not now:** genuinely hard to mechanize without it collapsing into either a trivia
minigame or an unmoderatable free-text problem. Needs a real design pass; parked with
respect.

### Psychological state (fear / resolve)
The brainstorm's stress system. Emotional stakes made mechanical.
**Why not now:** high stat-soup risk — exposure, standing, influence, skills is already
a lot of numbers to teach (principle 9's test). Revisit only if playtests show the
existing stakes don't *feel* like anything.

### Identity erosion / the full unperson arc
Losing your name, your record, your access; rebuilding from nothing. The setting's
darkest promise, and mechanically adjacent to ADR 0005's audit trail.
**Why not now:** it's the *end* of the record-vs-truth tech tree, not the start.

### Deprogramming as re-education *(from 3M field research)*
3rd Millennium sells voluntary skill deletion (wired chairs, 150k credits — steep on
purpose). Invert the consent and it's ours: detainment outcomes that *remove recorded
aptitudes* — the regime deletes what it decided you shouldn't know. Slots into ADR
0005 (aptitudes are record entries) and gives ADR 0006's interrogation ladder its
sharpest rung short of unpersoning.
**Why not now:** needs skills (v0.3) and detainment (v0.2) to exist first. When it
lands, telegraphing rules apply double — losing a skill must never feel random.

### Services as places *(from 3M field research)*
3M puts every capability at an address: upgrade at the Lab, download at the Hall, heal
at the E.R. Errand-through-geography is made for 2084, where moving through watched
space is exactly what exposure taxes — getting your record amended *requires walking
past the scanners to the Records Annex*. Mostly a build discipline rather than a
feature; recorded here so v0.3+ services default to being rooms, not commands.

### ~~The Induction Wing: tutorial as architecture~~ — LEFT THE LOT
*Built 2026-07-18 as the Orientation Wing (roadmap v0.3.5), on request, once v0.3 gave
it enough mechanics to teach. Kept here per parking-lot discipline: being on the list
is not a commitment, and leaving it gets recorded.* The one part still parked: being
*told your function* by the regime — that's v0.4's work assignments.

### The Grind Shelf *(brainstormed 2026-07-18, from [grind-loops-without-killing.md](../research/grind-loops-without-killing.md))*

Lauren's ask: experienced mudders arrive wanting the mob-grind's *shape* —
repeatable verb, visible numbers, session-sized satisfaction — and ADR 0006 rules
out the usual implementation. These are candidate loops that keep the psychology
(measurable progress, small frequent pay, variable jackpots, opt-in risk) with the
Grid's own materials. **Options, not decisions** — an ADR happens when one is picked.

*(Update 2026-07-18: Lauren picked options 1+2; they LEFT THE LOT as v0.6 —
[ADR 0008](../decisions/0008-grind-loops-sabotage-and-couriering.md). Options
3–5 remain parked.)*

1. ~~**Sensor sabotage circuit ("the dark game").**~~ **Shipped, v0.6.** Devices become attackable-in-place:
   `jam`/`blind`/`cut` a sensor through a skill check; the Ministry repairs them on a
   timer, so the map itself respawns. Pay: sabotage skill, a growing personal dark
   zone, jackpot when a whole street goes dark. Risk: failure is an incident; repairs
   raise district alert. The closest 1:1 mob-grind analogue — the bestiary is the
   apparatus.
2. ~~**Courier runs ("the queue is the dungeon").**~~ **Shipped, v0.6.** Contraband parcels from gossip-spot
   NPCs: carry X from A to B without being scanned. Pay scales with route visibility
   (opt-in difficulty tiers = zones); random rare packages pay standing with the
   *underground*. Death-equivalent: being scanned mid-run (parcel seized, incident).
3. **Interrogation-resistance sparring.** PvE "combat" where the enemy is an
   interrogator and HP is composure: rounds of pressure vs. `deflect`/`stonewall`/
   `misdirect`. Trains a resistance skill that later matters in real detention
   (Section C under duress). Turn-based combat, no blood.
   *(Update 2026-07-19: promoted to active consideration as tier 3 of the
   learning-curve response — the combat-shaped answer if v0.12–v0.13 don't
   flatten the curve enough. Lauren decides after the retiled first hour is
   measured; see [the-first-hour.md](../research/the-first-hour.md) §4.)*
4. **Records archaeology.** Grinding the archive itself: `research` at the Annex
   surfaces fragments; assembling a story about an unperson pays influence jackpots.
   The rare-drop table is narrative.
5. **Watch-the-Watch bounties.** The underground pays for verified observation:
   patrol schedules, sensor sharpness reports (`observe` output becomes a sellable
   commodity). Turns the existing skill into an income loop with a market.

Common properties: all pass principle 9 (each verb is something a citizen of Sector 9
would actually do), all single-player-viable (principle 8), none mandatory.

### Endgame paths (escape / overthrow / inner circle)
Long-horizon goals matter for retention.
**Why not now:** endgames only mean something once the midgame exists. Sequencing, not
doubt.

### The trust-machine backlog *(from game-theory research, 2026-07-19)*
[game-theory-of-the-grid.md](../research/game-theory-of-the-grid.md) audited the
betrayal mechanics against the repeated-prisoner's-dilemma literature and named four
gaps, in leverage order:

1. **Reputation must travel.** A Section C signer can currently walk into a new circle
   whose members never read his file. Fix: `judge` works on citizens too, reading
   betrayal-shaped file entries at sufficient observation skill — earned, diegetic.
2. **Escalating circle projects.** Joint errand chains with growing pots, so continued
   membership is worth more than one defection pays. The stash starts this; projects
   finish it.
3. **Suspected, not proven.** Every future leak mechanic must preserve deniability
   (plant reports have no fingerprints; interceptions don't name the room). Provable
   betrayal generates kick-lists; suspectable betrayal generates the game.
4. **Vouching.** Staking a little standing on another citizen — small, capped,
   recoverable — as trust-game participation below circle stakes.

Design invariant across all of it: **betrayal profitable once, costly as a career.**
A risk-free betrayal loop or unbeatable informant build kills cooperation
population-wide, and the multiplayer thesis with it.

## Deliberately deferred (with reasons)

### Lethal PvP, in any form
**No.** Conflicts with [ADR 0006](../decisions/0006-conflict-is-non-lethal.md) at the
thesis level, not the tuning level. Social PvP — betrayal, denunciation, forged records
— is the intended player-vs-player surface and is sharper anyway (principle 6).

### Opt-in permadeath mode
The consent framing (research §4) makes it *defensible*, and "volunteering for the
front" fits the fiction. But it forks content and testing for a mode few would use.
Someone must ask for it twice, in writing.
*3M field note:* their version is 10 lives plus a Life Insurance Salesman — catastrophe
visible ten steps away, distance from it purchasable. If we ever do consented stakes,
that economic shape (see [third-millennium-mud.md §4](../research/third-millennium-mud.md))
beats a binary hardcore flag.

### Big-world expansion / more districts
Rooms are added when concurrent population supports them (principle 8, anti-principle
4). The trigger is a measured busy world, not builder enthusiasm.

### Crafting / economy simulation
Evennia contribs make it cheap to bolt on, which is exactly the accretion trap. Ration
books and queues are the setting's economy; a market simulator isn't (principle 1's
test fails).

### Web client visual theming (telescreen aesthetic)
Fun, cheap-looking, and pure polish. After the loops work, as a treat.

## Speculative

### NPC suspicion memory (deep model)
NPCs tracking speech patterns and affiliations per-player (brainstorm §4). The shallow
version ships in v0.2 (react to exposure); the deep version is an AI project. Watch
whether the shallow version already reads as smart — players anthropomorphize
generously.

### Cross-MUD / persistent world archive
Memory objects that outlive characters, an archaeology of past players. Haunting, very
principle-8. No design yet; a sentence to remember it by.

---

## Known risks in shipped features

Soft spots shipped on purpose, recorded so they're revisited deliberately rather than
rediscovered through a confused playtester.

### Exposure could read as punishment roulette
*From [ADR 0004](../decisions/0004-surveillance-is-event-driven.md); flagged in
[mud-design-landscape.md §3–4](../research/mud-design-landscape.md).*

Probabilistic consequences risk feeling random rather than dreadful if the telegraphing
fails. Principle 3 stakes our answer on trend-legibility (prompt, patrols, NPC chill).
**What tells us it's happening:** playtesters describing a detainment as "out of
nowhere." Any single such report outweighs our intuition.

### Classless convergence
*From [ADR 0002](../decisions/0002-no-race-no-class.md).*

The known failure mode: every veteran converges on one best build. Mitigations shipped
as requirements (skill-by-use breadth cost, world reacting to record, institutional
standing as identity anchor). **What tells us it's happening:** vet dossiers looking
interchangeable. Check at every playtest gate from v0.3 on.
