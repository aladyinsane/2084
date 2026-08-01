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

### World-building tooling: adding areas without a full rebuild — DECIDED, not yet built ([ADR 0012](../decisions/0012-world-building-tooling-incremental-areas.md))
*(from Lauren's cleanup notes, 2026-07-25)* `world/build.py`'s one-shot nature
(`contributing.md` rule 8) blocks adding a district without risking the ones
already built, and blocks in-game building entirely (unchanged by this
decision — rule 8 still rules that out on purpose). ADR 0012 picked the shape
— split `build()` into one idempotent function per district — over adopting
the `mapbuilder` contrib or a single-entry-point hybrid. Implementation is
deliberately deferred to whenever the "Big-world expansion" trigger below
actually fires, so the idempotency guards get designed against a real new
district rather than a hypothetical one.

### ~~Propaganda engine~~ — SHIPPED (v0.25, 2026-07-28, [ADR 0017](../decisions/0017-propaganda-engine.md))
World news that reacts to aggregate player action: sabotage begets "foreign saboteurs"
headlines, paranoia, patrols. The brainstorm's best liveness idea and a strong
principle-8 machine (world feels inhabited at low population).
Picked by Lauren, from the solo-player fun thread, as the follow-up to records
archaeology — atmosphere/world-reactivity rather than a fourth grind loop. The original
blocker died with v0.6; the actual design found district alert already silently drives
patrol density, so the engine narrates that existing mechanic rather than inventing a
new one. Pure narration shipped, not real feedback into alert, so solo players can't
raise their own difficulty by grinding.

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
**Why not now:** originally, needed skills (v0.3) and detainment (v0.2) to exist first —
both have existed since v0.4, and this entry sat unrevisited through everything built on
top of them since. Caught 2026-07-27 during a docs audit: not blocked on anything
anymore, just never re-surfaced. Not a commitment to build it next, just a correction —
it's genuinely available to pick up whenever it's wanted, and the redesign-`wait`/`demand`
item directly below is a natural companion pass if either gets picked up.

### Detainment: `wait`/`demand` need more of a "game" feel *(from Lauren, 2026-07-24)*
Lauren's read after using it: `wait` (`game/commands/detention.py`) is just typing
`wait` up to `tuning.WAIT_RELEASE_TURNS` (5) times with flavor text cycling
underneath, no skill or decision in it. `demand` is worse than a no-op: it never
releases you, always logs an "unruly" dossier note, and **resets** the wait counter
back to 0 — so it isn't really a third option so much as a trap for anyone trying to
`wait` out a release. Lauren wants to think through a real redesign later, something
with more shape than a turn counter.
**Why not now:** flagged for a longer design pass, not started yet. Distinct from (but
adjacent to) the Grind Shelf's parked **interrogation-resistance sparring** option
below — that's a PvE loop that trains a resistance skill for use *during* detention;
this is about the base wait/demand loop every detained citizen faces regardless of
skill. Worth designing together if both get picked up.

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
4. ~~**Records archaeology.**~~ **Shipped 2026-07-27** ([ADR 0016](../decisions/0016-records-archaeology.md),
   `feat/records-archaeology`). Picked by Lauren, from the solo-player fun audit, as the
   first Grind Shelf option actually built. `research` at the Annex draws atomic
   fragment sentences (no grammar-stitching) toward a randomly-named generic case,
   infinite by construction; a rare draw instead surfaces a piece of one of three
   hand-authored named cases
   ([catalogued in lore](../lore/artifacts/unperson-case-files.md)). Hybrid payout, same
   shape ADR 0014 chose: small Records standing per fragment, underground standing on
   completion. Checked against `grind-loops-without-killing.md`'s 5-point extraction
   checklist explicitly — every item satisfied.
5. **Watch-the-Watch bounties.** The underground pays for verified observation:
   patrol schedules, sensor sharpness reports (`observe` output becomes a sellable
   commodity). Turns the existing skill into an income loop with a market.

Common properties: all pass principle 9 (each verb is something a citizen of Sector 9
would actually do), all single-player-viable (principle 8), none mandatory.

### Endgame paths (escape / overthrow / inner circle)
Long-horizon goals matter for retention.
*(Update 2026-07-28: Lauren asked what the endgame actually is, and whether "why not
now" still holds — the midgame this was waiting on is now substantially built. First
pass at an answer: [endgame-and-long-term-goals.md](../research/endgame-and-long-term-goals.md).
Three non-exclusive candidate long-horizon peaks sketched — inner-party co-option
[played straight, not subverted into a clean win, per the source material's own
logic], doublethink [the natural capstone for the still-parked doublethink feature
below], and a relational "what outlasts you" peak drawing on the trust machine's
existing "profitable once, costly as a career" invariant. Not decided; genuinely
still thinking about it, per Lauren's ask.)*
**Why not now:** the original blocker (nothing to build toward yet) is largely
resolved; what's actually undecided now is design, not sequencing.

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
2. ~~**Escalating circle projects.**~~ **Shipped 2026-07-24**
   ([ADR 0013](../decisions/0013-escalating-circle-projects.md), `feat/circle-projects`).
   Three-stage circle project (cumulative solo sabotage, cumulative solo couriering,
   then a synchronous two-member climax), paying out underground standing only on
   completion and forfeiting the whole pot on a completed Section C confession — the
   mechanism the invariant below actually asked for. Chose "mostly solo, climax
   synchronous" over the gamification audit's fully-synchronous three-stage heist
   sketch, to keep principle 8's solo-viability test honest for circles that rarely
   get 2+ members online at once. Revisit triggers named in the ADR: circles stalling
   at the Split with casing/the run long done, or the free-rider question (any one
   member can fill the whole shared tally alone) getting a real complaint attached.
3. ~~**Suspected, not proven.**~~ **Shipped 2026-07-26**
   ([ADR 0015](../decisions/0015-suspected-not-proven-circumstantial-informant-clues.md),
   `docs/adr-0015-suspected-not-proven`). Audited against the research doc's framing
   first: deniability already held (no fingerprints, no named rooms, in either existing
   leak mechanic) — the actual gap was that the informant-report message was static
   flavor text with nothing circumstantial in it, so circles had nothing real to reason
   about. Now, when a circle has an active project running (ADR 0013), a report
   references the room of the project's most recent qualifying sabotage/delivery —
   never a member, never an informant, and structurally can't narrow to one name since
   Casing/the Run are already a shared tally. No active project: unchanged generic
   text, same as before. The literal "hidden role between players" the research
   diagnosis names as missing ([parked below](#the-mole-a-player-facing-double-agent))
   is not addressed by this — recorded separately rather than folded in.
4. ~~**Vouching.**~~ **Shipped 2026-07-24** ([ADR 0014](../decisions/0014-vouching.md),
   `feat/vouching`). `vouch <citizen>` stakes a small, sanctioned Ministry of Records
   stake on someone — reachable from a new player's first few minutes, unlike
   underground standing. Forfeits whole on that citizen's own Section C confession
   (same forfeiture idiom as the stash and circle projects); offsets one incident in
   Form C-1's adjudication while active, giving the existing "character references
   insufficient" rejection text a real mechanism behind it. Chose the hybrid shape
   over a literal C-1-only reading, since C-1 alone wouldn't reach the new/risk-averse
   audience the mechanic was named for. Revisit triggers named in the ADR: vouching
   used reflexively with no real information about the target, or the C-1 payoff's
   invisibility (no message distinguishes "you'd have passed anyway" from "the vouch
   saved you") drawing a real complaint.

Design invariant across all of it: **betrayal profitable once, costly as a career.**
A risk-free betrayal loop or unbeatable informant build kills cooperation
population-wide, and the multiplayer thesis with it.

### The mole: a player-facing double agent *(parked from ADR 0015, 2026-07-26)*
[game-theory-of-the-grid.md](../research/game-theory-of-the-grid.md)'s diagnosis names
hidden roles between *players* as the one structurally missing piece — informants have
hidden loyalty (`street`/`ministry`), circle-mates don't. A new Section C option: a
detained citizen stays in their circle but starts reporting on it from the inside,
deniable the same way an NPC plant is. Presented as a real alternative to item 3 above
and explicitly not chosen for that version — it's a new hidden-role mechanic, not an
extension of one that already exists, and deserves its own research/design pass rather
than riding in as "finishing item 3."
**Undesigned:** how a citizen gets turned (an offer during detention? Only after a
first Section C? Coerced or bought?), whether it's opt-in or something the Ministry can
force, what tells (if any) a circle gets that one of its own might be compromised
beyond what item 3's circumstantial clues already give them, and the fairness question
underneath all of it — a circle-mate secretly working against you is a sharper edge
than an NPC informant, since NPCs are recruited by choice and this wouldn't be.
**Why not now:** genuinely bigger scope than sharpening an existing mechanic; wants its
own ADR once someone's ready to think through consent and detection properly.

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

### Clickable commands inline in room text (web client)
*(Lauren's journal, 2026-07-27)* Idea: when a command name appears in a room
description or other text (e.g. "type |cobserve|n"), make it clickable in the web
client — click it, it runs.
**Why worth a look:** the purpose-built mobile client
([mobile-web-client.md](../research/mobile-web-client.md)) already reuses Evennia's
own protocol layer rather than the stock GoldenLayout client, and its phase 2 (real
on-device testing) is still open — this could plausibly ride along with that work
rather than need a separate client pass. Evennia's webclient protocol already carries
color-tagged text (`|c...|n` etc. survive to the client); whether it exposes a clean
existing hook for command-as-hyperlink versus needing custom JS in the mobile
client's own template hasn't been researched.
**Why not now:** no research pass has been run against what Evennia's webclient
contrib actually offers here — default answer until checked, not a design objection.

### Too many separate advancement trackers — fold clearance into grade, or something else
*(Lauren's journal, 2026-08-01)* Lauren's read: there are currently too many separate
numbers a citizen tracks as "am I advancing" — Grade, Clearance, standing (per
institution), skills (per skill), exposure, influence. Idea: combine grade and
clearance specifically into one measurement, or find some other consolidation.
**Auditing what's actually there first:** they're not fully independent today —
`CmdGrade`'s own docstring already lists "clearance granted" as one of several inputs
to merit, alongside standing paid, errands seen through, a function held, and
orientation completed. But Clearance also remains its own separately-gated system: a
`clearance(N)` lockfunc, its own EvMenu form (C-1), its own Spire-access consequence —
a citizen experiences it as a second, independent ladder, not merely one input among
several to Grade. So the "too many trackers" read holds even though the two aren't
wholly siloed today.
**Why this is a real question, not a quick fix:** Grade (v0.12) was chosen
specifically as *the* familiar, single legible ladder players already know from
other MUDs; folding Clearance into it outright would need to preserve Clearance's
actual gating function (it locks real exits/content; Grade doesn't gate anything by
itself) without the merge just becoming a second name for the same number. This
touches ADR 0002 (skills/standing as the identity model) and ADR 0003
(exposure/influence replacing XP/levels) at the foundation, not just v0.12 — worth a
real research pass on what's actually redundant versus what only *looks* redundant,
the same weight as the endgame research question, before an ADR picks a shape.

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

### ~~`work`'s off-cooldown dead air~~ — FIXED (`fix/work-cooldown-texture`)
*(from the ten-persona playtest, 2026-07-20; never triaged here until the solo-player
fun audit caught it, 2026-07-26)* `work`'s 45 dead cooldown seconds had one static
rejection line and gave no sense of when the next shift opens. Now the rejection reads
from one of two prose tiers (`OFF_COOLDOWN_FAR` / `OFF_COOLDOWN_NEAR`) depending on how
close the cooldown is to elapsing, same idiom as the sweep's near-miss telegraphy
(`scripts.py`'s `NEAR_MISSES`) — proximity read through prose, never a raw countdown.
New tuning constant `WORK_NEAR_COOLDOWN_FRACTION`, reused as-is by `research`'s own
cooldown texture ([ADR 0016](../decisions/0016-records-archaeology.md)).

### `help standing` clarity pass — needs a specific complaint first
*(Lauren's journal, 2026-07-25)* Ask: make sure the `standing` helpfile is clear.
Reviewed the current entry (`game/world/help_entries.py`) while filing this — it
already follows the "How it's earned / How it's spent / Where to see it" structure
used elsewhere, and cross-references `exposure` and `grade` by name to distinguish
standing from both. Nothing jumped out as obviously wrong or missing on a cold read.
**Not actioned:** what specifically prompted the note isn't clear without Lauren's
own read on what's confusing — rewriting a helpfile without a concrete complaint
risks polishing prose that was never the actual problem. Flagged here rather than
silently closed; needs a specific example (a confused playtester, a moment that
didn't land) before it's actionable.

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

### Subterranean infrastructure, needs a new name
*(From [worldbuilding-ideas.md](worldbuilding-ideas.md#iv-pipeline-to-future-features),
orphaned 2026-07-24, recovered 2026-07-27.)*

That doc's narrative-concept pipeline had a "Circle Projects" row — safehouse radio,
stash networks, subterranean infrastructure a circle builds up over time — that lost
its name to [ADR 0013](../decisions/0013-escalating-circle-projects.md)'s unrelated
mechanic (pooled sabotage/courier stages ending in a synchronous payout). The
collision was flagged in `worldbuilding-ideas.md` itself at the time, but the concept
never got an actual entry here — it's been sitting unreferenced in the feeder doc for
three versions. Recording it properly now, not endorsing it: a genuinely different
idea from ADR 0013, un-designed, and unbuildable under its old name.
**Why not now:** needs a new name before anyone can even discuss it without ambiguity,
and no research/principles pass has been run against it yet — this is a bookmark, not
a plan.

### The world outside the Grid: farmers vs. the Ministry, over land and water
*(Lauren's journal, 2026-07-25)* An idea for what exists beyond Sector 9 itself: a
resource conflict between farmers/rural landholders and whichever Ministry wants
their land and water for AI data centers. A different axis on principle 1's
antagonist — the regime's hunger for resources, not only its hunger for legible
citizens.
**Why not now:** genuinely new territory, not a Sector 9 feature — closer in kind to
"Big-world expansion / more districts" above, which is explicitly gated on a measured
busy world, not builder enthusiasm. No research pass has been run against it, and a
real open question sits underneath: does this stay backstory/lore texture citizens
hear about secondhand, or does it become an actual playable area? Those are very
different commitments, and this idea doesn't yet say which. Worth keeping regardless
because it's a fresh expression of an existing principle rather than a new subsystem
— the antagonist wanting your land is the same shape as the antagonist wanting your
file, just aimed at a different target.

### A "credits" currency, earned and spent
*(Lauren's journal, 2026-07-26)* Idea: a currency citizens earn and spend.
**Worth flagging before this goes anywhere:** the game already has one earned/spent
economy — Influence ([ADR 0003](../decisions/0003-exposure-influence-not-xp.md)),
per-faction standing with sinks built in from day one, chosen explicitly over
anything XP/score-shaped. "Crafting / economy simulation" above is already
deliberately deferred for an adjacent reason ("ration books and queues are the
setting's economy; a market simulator isn't — principle 1's test fails"). A second,
parallel "credits" currency would need a real answer for why it's not just Influence
under a new name, or what gap Influence genuinely leaves open — a currency spendable
*across* factions, unlike Influence's per-institution ledgers, is the most obvious
candidate gap, but that's a guess at Lauren's intent, not a confirmed one — before
it's worth a research pass rather than a rename.

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

### `flip`'s retention was never actually checked
*From [command-surface-audit.md](../research/command-surface-audit.md), v0.7. Caught
2026-07-27 during a docs audit.*

The audit considered dropping `flip` (the narrowest verb in the underground set — buy
out a Ministry-loyal informant) and explicitly deferred the decision: *"retained: it is
the observation grind's best payoff. Watch it; if nobody flips anyone by the next
playtest gate, it folds into `recruit`."* At least one playtest gate has passed since
(the [ten-persona playtest](../research/playtest-2026-07-20-ten-personas.md),
2026-07-20) with no record anywhere of anyone checking whether `flip` actually got
used, and the watch clause itself was never carried forward past v0.7 — this document
had no memory of it until now. **What tells us it's happening:** nobody's dossier or
session log ever mentions `flip`. Check at the next real playtest, and either confirm
it earns its place or fold it into `recruit` as originally proposed.
