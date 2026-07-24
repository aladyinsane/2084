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

### World-building tooling: adding areas without a full rebuild *(from Lauren's cleanup notes, 2026-07-25)*
Lauren's question: `world/build.py` is one-shot, invoked only at initial setup
(`contributing.md` rule 8 — the world is code, not hand-`dig`ged). Two related but
distinct asks: (a) can a *new* district be added later without re-running, or
risking corrupting, the districts already built? (b) could an area ever be built
from inside the running game, rather than only in a batch file?
**Current state:** neither is possible cleanly today. `build()` is one monolithic
function; every `create_object` call runs unconditionally, so re-running it against
a live DB duplicates or errors on everything already there — the same shape as the
"one-shot, not idempotent" snag already hit twice needing manual backfill scripts
for post-launch additions to *existing* rooms (CLAUDE.md), just bigger: a new
district is a whole extra unconditional pass over the old ones. In-game building is
deliberately unsupported at all — rule 8 exists specifically so the world stays
reviewable and rebuildable from the repo, not scattered across live-server `dig`
commands.
**Candidate shapes, not yet decided:**
1. Split `build()` into one function per district, each idempotent
   (`get_or_create`-style guards keyed on room name/tag) — a new district becomes a
   new function and a new call, without touching the guarded existing ones.
2. Adopt the `mapbuilder` contrib (above) for new districts once hand-written batch
   code stops scaling, while old districts stay frozen in their current batch files.
3. Some combination: batch code stays the source of truth (rule 8's discipline is
   worth keeping), but the tooling around it becomes safe to re-run incrementally.
**Why not now:** no district has been added since v0.1's starting slice — real
tooling debt, but only worth paying down when the "Big-world expansion" trigger
below actually fires (a measured busy world asking for more space), per principle 8
and anti-principle 4.

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

### Doublethink: seeing the Ministry's edits *(from ADR 0011, 2026-07-23)*
Lauren's framing: a citizen with high enough Underground standing should eventually be
able to *see* the gap between what their file says and what actually happened — the
Ministry's redactions and edits made visible, in the spirit of 1984's doublethink
(holding the official record and the acknowledged truth at once). [ADR
0011](../decisions/0011-old-incidents-compact-the-file-forgets-faster-than-the-truth-does.md)
(record compaction) was deliberately built with this in mind: a compacted incident
summary keeps a `true_count` that no game action ever lowers, alongside the
`visible_count` that `petition`/`forge` can, specifically so this feature has real
per-citizen, per-incident-type data to read from once it exists — not because it's
being built now.
**Undesigned:** what the reveal actually looks like (a command? gated behind `word`/the
shadow ladder tiers, or its own threshold? passive or something you have to ask for?),
what stops it from just handing a high-standing citizen the whole game's secrets
cheaply, and whether it should apply to your own file only or to others' too — the
latter would make it a second, sharper edge on ADR 0010's reputation-travels idiom.
**Why not now:** ADR 0011 needs to ship and settle first; this is real design work in
its own right once it does, likely its own ADR.

### Date-range batch petitions *(from ADR 0011 follow-up, 2026-07-23)*
Lauren's follow-up while reviewing ADR 0011: once routine incidents compact into a
flat per-type lifetime count (`{"true": T, "visible": V}`), let a citizen redact/amend
a *chunk* of a type at once — "everything from around Day 200" — rather than only
"one fewer, whichever." Needs sub-bucketing a compacted type by rough time window
(weekly? monthly?) instead of one flat count, which is real added complexity over the
ADR 0011 baseline. The natural building block, if it happens: a **derived in-fiction
day number** (`(time.time() - EPOCH) // tuning.SECONDS_PER_DAY`, computed on demand,
no new script or stored tick counter) rather than a ticking calendar system — matches
how Grade and the shadow ladder are already pure functions of existing data, never
incremented state.
**Why not now:** ADR 0011's flat-count version needs to ship and prove the shape
works before adding a second axis (time) to the bucketing.

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
   *(Update 2026-07-23: Lauren's call — **stays parked**. The gate was met
   without it: v0.13's own measurement (parsons, Grade 4 in ~3 driven minutes,
   zero dead ends) and the round-two playtest's twelve live sessions across ten
   personas plus two fresh accounts surfaced zero "wants combat" or "feels
   dull" findings — every remaining round-two finding was legibility polish,
   not a missing system. Revisit only if a real playtest explicitly names
   wanting a combat-shaped loop.)*
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

1. ~~**Reputation must travel.**~~ **Shipped 2026-07-23** —
   [ADR 0010](../decisions/0010-reputation-travels-judge-reads-citizens.md). `judge`
   now works on citizens too, reading a Section C tag at `tuning.OBSERVE_TIER_REPUTATION`
   observation — earned, diegetic, same idiom as the informant version. Revisit
   triggers named in the ADR: nobody thinking to check before inviting, or the
   permanent-stain read discouraging `confess names` even when it's the right call.
2. **Escalating circle projects.** Joint errand chains with growing pots, so continued
   membership is worth more than one defection pays. The stash starts this; projects
   finish it. *(The [gamification audit](game-theory-and-fun.md)'s "Escalating Circle
   Heists" sketches a concrete three-stage version — sabotage two screens, intercept a
   patrol while a comrade hits the Annex, then the payoff — additional design material
   for whenever this gets picked up, not yet checked against the invariant below.)*
3. **Suspected, not proven.** Every future leak mechanic must preserve deniability
   (plant reports have no fingerprints; interceptions don't name the room). Provable
   betrayal generates kick-lists; suspectable betrayal generates the game. *(The
   [gamification audit](game-theory-and-fun.md)'s "Paranoia Engine" sketches diegetic
   clue-planting for this — same caveat as above: unvetted design material, not a plan.)*
4. **Vouching.** Staking a little standing on another citizen — small, capped,
   recoverable — as trust-game participation below circle stakes.

Design invariant across all of it: **betrayal profitable once, costly as a career.**
A risk-free betrayal loop or unbeatable informant build kills cooperation
population-wide, and the multiplayer thesis with it.

### From the gamification audit *([game-theory-and-fun.md](game-theory-and-fun.md), 2026-07-24)*

An unreviewed proposals doc landed with five gamification mechanics and its own
implementation-sequencing table. Two of the five (escalating circle heists, the
paranoia engine) duplicate trust-machine backlog items 2 and 3 above and are
cross-referenced there instead of listed twice. The remaining three are recorded here
as candidates, each with a real conflict against an accepted decision — the audit
itself didn't go through contributing.md's research → principles → ADR chain, so none
of this is vetted the way the rest of the parking lot is.

**Push-your-luck streak multipliers.** Consecutive actions in watched space (Vis 3–5)
build a multiplier on standing/credits/underground reputation, at the cost of doubling
exposure accrual and sweep odds per tier.
**Why not now:** runs directly against [ADR 0003](../decisions/0003-exposure-influence-not-xp.md)'s
thesis — exposure is "the rare inversion: the number you watch most is best when it
goes *down*." Making climbing exposure *pay* risks the "exposure could read as
punishment roulette" risk named below. Would need its own case for why this exception
to the exposure-is-dread rule earns its place.

**Contextual action prompts / a universal `interact` verb.** Dynamic per-room lists of
valid actions in the prompt, plus a catch-all verb routing to menus.
**Why not now:** conflicts with two settled choices, not just untested territory.
[ADR 0009](../decisions/0009-shadow-ladder-is-a-checkable-whisper.md) chose "purely
opt-in discovery, no hinting" as an accepted cost, and ADR 0010 followed the same
idiom — both deliberately never prompt a player to check. Principle 9's "no
magic-missile moments" is exactly what v0.14's whitelist-only nomatch overhaul was
built to enforce; a generic `interact` opening engine-style menus risks the same genre
bleed that overhaul stopped.

**Skill-based timing/sequence minigames.** Replace flat skill-check RNG (`sabotage`,
`forge`) with a timing or sequence mini-mechanic.
**Why not now:** the "Psychological state" entry above already named the stat-soup
risk of mechanical surface for its own sake; a reflex-timing layer adds a different
*kind* of skill (dexterity, not knowledge/observation) than anything else in the game,
on top of that same risk. Needs evidence flat skill checks are actually the dull part
before assuming a minigame fixes it.

## Cleanup backlog

Small, mechanical fixes with no real design tension — recorded so they don't get
lost, not because they need a design pass.

### ~~Em-dashes in player-facing text~~ — FIXED (`fix/em-dashes-in-game-text`)
*(from Lauren's cleanup notes, 2026-07-25)* Game text should read without em-dashes.
Swept every player-facing string (room descriptions, NPC lines, messages, help
entries, forms, and — since Evennia surfaces them via `help <command>` — every
`Command` subclass's docstring) across `world/`, `commands/`, and `typeclasses/`,
replaced with whatever reads most naturally in context (colon, comma, semicolon, or
a full stop), verified against a script confirming zero `Command` docstrings still
contain one. Code comments and non-Command docstrings were left alone, since they're
never shown to a player. The one deliberate stylistic use (`build.py`'s
overheard-conversation line, using the dash to show a sentence caught
mid-interruption) was rewritten with ellipses instead of a plain substitution, to
keep the "caught mid-conversation" effect. One test assertion
(`test_petition_redact_by_keyword`) depended on the exact dossier compaction-summary
format and was updated to match.

### ~~Consistent bordered presentation for in-game "forms"~~ — FIXED (`feat/form-borders`)
*(from Lauren's cleanup notes, 2026-07-25)* Every form-like presentation should
share one bordered look. Three different styles had coexisted — `form_c1.py`'s
Unicode box-drawing border, `grades.py`'s ASCII `====` rule, and no border at all
on Form 1-A/2-B/12-D. A new `world/forms.py::form_box()` helper (plain ASCII, left-
aligned only — Evennia color tags don't count toward visible width, so a right-
closed box would need width-aware stripping) is now used by Forms 1-A, 2-B, 9-A,
12-D, and C-1. Section C's confession and Form 77 deliberately excluded — neither
is ever rendered as a title card today (Section C is narrated as scene; Form 77 is
only a rejection-reason phrase inside Form C-1's own text), so boxing either would
mean inventing a header that doesn't exist rather than making an existing one
consistent. Judgment call worth watching: Form 2-B (the `next` advisory) now
renders as a 4-line box on every call, including the frequent no-argument case —
consistency was the explicit ask, so applied uniformly rather than special-cased,
but it's the one form whose call frequency makes the box's footprint worth
revisiting if it reads as noisy in practice.

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

### ~~Idlers are farmed for incidents~~ — FIXED (2026-07-22, `fix/assembly-idler-policy`)

*Found in the v0.12 playtest; fixed after round-two evidence (claude's dossier hit 35
consecutive duplicate absence incidents, still compounding live).* All three
previously-parked candidate fixes shipped together, per Lauren's call: (1) a citizen
whose session has gone quiet longer than `tuning.ASSEMBLY_ACTIVE_WINDOW` (10 min) is
skipped from the roll entirely; (2) consecutive unexcused absences stop generating new
incidents past `tuning.ASSEMBLY_ABSENCE_CAP` (5) in a row, resetting on next
attendance; (3) a citizen who registered after an assembly was announced (tracked via
`announced_at`) is excused from that roll. Absence-as-data (M8) stays intact for
present, active players — this only stops penalizing the away-from-keyboard case.
Not yet re-verified against a live roll call end-to-end (a real player was connected
during the fix and forcing a roll would have paged them mid-session) — worth a
targeted live check next time an assembly fires with an idle test account nearby.

### ~~The papers-check sweep had the same farming shape~~ — FIXED (2026-07-23)

*Found while investigating dossier scaling (Lauren's ask, 2026-07-23), same bug class
as the idler-farming entry above.* `WatchSweepScript.papers_check` filed a new
identical "Papers checked in the street; cleared." incident every time the sweep
(`WATCH_SWEEP_INTERVAL`, 90 seconds) selected a citizen sitting in the 20-50 exposure
band — no cooldown, no cap, unlike the assembly roll after its fix. A citizen parked
in that band for a long session could accumulate the same incident many times over,
same shape as the 35-entry assembly farm, just never surfaced in a playtest because
nobody stayed in that exact exposure band long enough to notice. Fixed by throttling
the *file entry* only (`tuning.PAPERS_CHECK_RECORD_COOLDOWN`, 30 minutes) — the
exposure relief, the actual point of the interaction, still applies every time it
fires.

### Classless convergence
*From [ADR 0002](../decisions/0002-no-race-no-class.md).*

The known failure mode: every veteran converges on one best build. Mitigations shipped
as requirements (skill-by-use breadth cost, world reacting to record, institutional
standing as identity anchor). **What tells us it's happening:** vet dossiers looking
interchangeable. Check at every playtest gate from v0.3 on.
