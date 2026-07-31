# Research: opposed checks and dice-style resolution for existing verbs

Lauren's ask, 2026-07-30: most MUDs resolve contests with a D&D-style die roll
compared against a skill (or an opposing skill); she'd like to modify some of the
game's existing features — she named `observe` as a candidate — to resolve the
same way. Scoped in conversation before any writing started: **PvE checks only**
(no player-vs-player rolls), and **the roll itself stays hidden** — the player sees
an outcome, never the underlying numbers. This doc is first-pass research, same
shape as [endgame-and-long-term-goals.md](endgame-and-long-term-goals.md) — it
surveys the space and names the real tension, it does not decide anything.

## What's actually there today

Auditing before designing, same move as every ADR since 0015. The game already has
a use-based skill system (`caller.skill(name)` / `caller.improve_skill(name)`,
0–50 per `tuning.SKILL_CAP`, ADR 0002/0003) tracking `observation`, `forgery`,
`clerking`, `sabotage`, and `couriering`. But it resolves in **two** shapes today,
neither of which is a D&D-style opposed check:

1. **Deterministic tier-gate.** `observe` (`commands/civic.py` `CmdObserve`) checks
   `skill >= tuning.OBSERVE_TIER_*` — three fixed thresholds (15/35/45) that unlock
   progressively more detail. No randomness anywhere. `archaeology.py`'s clerking
   bonus works the same way, additively.
2. **Flat skill-scaled probability.** `forge` (`civic.py`) and `sabotage`
   (`world/underground.py`) both do `random.random() < BASE_CHANCE + skill *
   SKILL_BONUS` — forging: 25% base, +0.5%/skill point, 50% at cap; sabotage: 30%
   base, +1%/skill point, 80% at cap. This *is* randomness, and it already exists
   in two shipped features. But the chance is a pure function of the actor's own
   skill against a **flat tuning constant** — no opposing entity's stat enters the
   formula at all. A citizen with cap forgery skill has exactly a 50% chance
   editing *any* record, whether it's a routine note or something under active
   review.

**The piece that's genuinely missing** is the actual D&D shape: a check whose
difficulty is a property of the *obstacle*, not just a tuning constant — an
opposed roll, or a single roll against a DC set by something the obstacle itself
carries (a sensor's own concealment quality, a record's audit-sensitivity, a
patrol's current alertness). That's the real gap between what's shipped and what
Lauren's describing, and it's worth naming precisely because "add randomness" is
already partially done — the new part is *contest*, not *chance*.

## Precedent already on record — read this before designing further

This project has weighed something adjacent to this twice already, worth knowing
going in:

- **`third-millennium-mud.md`'s "What we don't take"** lists, first item after the
  lore: *"Rolled stats, XP-per-damage, and the combat-centric core loop — replaced
  wholesale by ADR 0003's exposure/influence model."* ADR 0003 itself is more
  specific: *"There are no levels. Access is gated by standing and clearance...
  never by a character-level check."*
- **"Interrogation-resistance sparring"** (`future-features.md` §3) is a fully
  sketched, still-parked combat-shaped PvE loop — composure as HP, rounds of
  pressure vs. `deflect`/`stonewall`/`misdirect`, turn-based. Promoted to active
  consideration 2026-07-19, then explicitly re-parked by Lauren 2026-07-23: *"the
  gate was met without it... every remaining finding was legibility polish, not a
  missing system. Revisit only if a real playtest explicitly names wanting a
  combat-shaped loop."*

**This ask is not that**, and the difference matters enough to say plainly:
Lauren's ask here isn't a new combat subsystem or reviving the parked sparring
loop — it's
borrowing dice-vs-difficulty as a *resolution primitive* for verbs that already
exist and already have skills attached (`observe` chief among them). Nothing
about scope, PvE-only + hidden-roll, resembles "rounds of combat." But the two
precedents above are exactly the kind of thing worth having in view before
building this, since a careless version of "opposed checks everywhere" could
drift toward the thing that got cut twice.

## Why PvE-only + hidden-roll actually fits, not just avoids a fight

Principle 3 (*surveillance is dread, not damage*) already commits to this exact
shape: *"probabilistic, unevenly distributed, and opaque in the moment — but
always legible in trend."* A hidden per-instance roll sitting on top of a fully
visible, deterministically-growing skill number **is** that sentence, mechanically
— the individual check is opaque, the trend (your skill number, shown in
`dossier`/`grade` any time you ask) is never hidden. That's a materially better
match for principle 3 than either of today's two shapes: tier-gates are legible
but not remotely probabilistic, and forge/sabotage's flat-chance rolls are
probabilistic but the chance is invisible *and* unrelated to anything in the
world reacting to you.

Principle 9 (*no magic-missile moments*) is the one worth actively guarding
against during implementation, not design: the fiction has to carry the roll.
"You rolled a 14" is the wrong genre entirely; "the sensor's angle catches the
light wrong and you nearly miss it" is the right one. This is a wording
discipline, not a design blocker — same discipline already applied to forge's
and sabotage's failure messages today.

## Candidate mechanism shapes

Three ways to give an obstacle its own difficulty, from smallest to largest change:

**A. Roll-under a computed threshold, obstacle raises the bar.**
`success = random.random() < base_chance + actor_skill*bonus - obstacle_difficulty`
Cheapest change — literally forge/sabotage's existing formula with one more term.
No new roll concept, just a difficulty input that currently doesn't exist per-object.

**B. Single roll vs. a DC derived from the obstacle's own stat.**
`roll = random.randint(1, 20) + actor_skill_mod; success = roll >= obstacle_dc`
Closest to the literal D&D shape Lauren named. Needs a skill→modifier mapping
(skill 0–50 doesn't map 1:1 onto a d20 the way a D&D ability score does) and a
per-obstacle DC field.

**C. True opposed roll, both sides roll.**
`actor_roll = d20 + actor_skill; obstacle_roll = d20 + obstacle_skill; success =
actor_roll > obstacle_roll` The obstacle needs to be more than a static number —
something that can itself vary run to run (a patrol's alertness already does,
tied to `watch.get_alert()` from the propaganda engine, ADR 0017). This is the
only shape where "skills comparison" is literal in both directions, and the only
one that would read as a genuine two-sided contest rather than a harder lock.

None of these need to be *the* shared mechanic — feature-specific formulas (today's
pattern) versus one shared `opposed_check()` helper is itself an open question
below, not resolved by picking a shape.

## Worked examples, using what's already in the world

**`observe` vs. a sensor's own concealment.** Today `concealed` is a boolean gated
by a flat skill threshold (45). Give concealed sensors a `concealment` rating
instead (say 1–10) and roll shape B or C against it: a barely-hidden device stays
easy to spot even at low skill, a well-hidden one stays genuinely uncertain even
near skill cap. This is the most natural first target — it's the feature Lauren
named, and `observe` already has the exact skill/tier scaffolding to extend rather
than replace.

**`forge` vs. a record's audit-sensitivity.** Today every record is equally easy
to edit at a given skill level. Records already carry a `kind` (ADR 0005) and
recent review state could plausibly derive a per-record difficulty — a record with
an open incident or recent `judge` lookup on it resists forgery harder than one
nobody's looked at in months. Reuses shape A cheaply on top of the existing
formula.

**`sabotage` vs. current district alert.** `watch.get_alert()` already exists
(ADR 0017, the propaganda engine) and already varies over time from real player
activity — it's sitting right there as a ready-made obstacle-difficulty input that
nothing currently reads for sabotage's own success chance, only for what NPCs say
about it. Wiring `sabotage`'s difficulty to current alert would make a genuinely
opposed-feeling check (the underground vs. how hot the sector currently is) out of
two systems that already exist and currently don't talk to each other.

## Open questions for Lauren

1. **Which existing verbs, concretely?** `observe` was named as an example, not
   necessarily the only target. Candidates from the audit above: `observe`
   (concealment), `forge` (audit-sensitivity), `sabotage` (district alert). Worth
   confirming the actual target list before an ADR gets written around it.
2. **Shared helper or feature-specific formulas?** A generic `opposed_check(actor,
   skill_name, obstacle_difficulty)` in a new module (parallel to how
   `onboarding.py` centralized first-use acknowledgments) versus keeping each
   verb's formula local, matching today's pattern. Shared is more consistent and
   easier to balance in one place; local is smaller-diff and matches how forge and
   sabotage already do it independently.
3. **Do existing flat-chance systems (forge, sabotage) get migrated too, or is
   this additive** — new obstacle-driven checks on top of what's already there,
   leaving forge/sabotage's current flat formulas alone unless a specific reason
   to touch them shows up? Migrating both is a bigger, riskier diff than adding
   the pattern fresh to `observe` first and letting a playtest judge it before
   touching what's already shipped and stable.
4. **Shape A, B, or C** (or a mix per-verb) — B is closest to "D&D-style" literally,
   but needs a skill→modifier mapping since the game's 0–50 skill scale doesn't
   map onto D&D's ability-score conventions. A is the least invasive. C is the
   only one where the obstacle itself can meaningfully vary run-to-run using data
   the game already tracks (alert level).

## Not a decision

This is a survey, not a proposal to build. If a direction here looks right, the
next step is an ADR — same shape as every mechanical decision since 0009 — naming
the actual chosen shape, the actual verb list, and (per the Bad-section habit)
what a hidden, obstacle-driven roll costs: mainly, that failure now sometimes
means "you were unlucky" instead of "you weren't skilled enough yet," which is a
different feeling than everything else in the game currently produces and is
worth a playtest read, not just a design guess.
