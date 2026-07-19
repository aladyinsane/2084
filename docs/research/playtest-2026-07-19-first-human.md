# First human playtest — Lauren, 2026-07-19

The gate the roadmap has been waiting on since v0.2: a playtester who isn't the
developer. This doc records the findings verbatim-in-spirit and what each one
implies. The headline is the last line of the risk register coming true in a
milder form than feared: not "punishment roulette," but **"it's currently...
a bit dull"** — and a set of legibility problems that compound into that
dullness. Confusion is a fun-tax; most of these findings are taxes.

## Findings and implications

1. **Command overwhelm.** "All these custom commands are a bit overwhelming —
   weigh the complexity against what players might be expecting from a MUD."
   → We shipped ~15 custom verbs across 5 versions with no in-game index
   beyond `help`'s flat list. Implication: better help organization, an
   audit of which verbs earn their place, and respect for MUD conventions
   where they exist. (Findings 2–3 and 5 are instances of this one.)
2. **No helpfiles for the core stats.** Vis and Exp are the game's two most
   important numbers and neither has a helpfile. → Write them.
3. **"Exp" reads as experience points.** Every MUD veteran's prior. → Spell
   out `Exposure` in the prompt; the prompt is read hundreds of times a
   session and must not require unlearning.
4. **NPC names uncapitalized in room listings and poses.** Cosmetic, seen
   constantly. → Fix display capitalization globally.
5. **`sound` is confusingly named.** (Sound the informant = probe loyalty.)
   → Rename; Lauren suggests `judge`, which also reads better against the
   observation skill it uses.
6. **"You see: a the chalk marks."** Article-stacking on objects whose names
   embed "the". → Fix display naming (affects the chalk and any future
   "the X" object).
7. **Detention is a dead end for a new player.** No `help` in the holding
   cell, no indication of what verbs exist; being detained the first time
   means staring at a wall. → `help` joins the detained command set, and the
   cell tells you your options the first time the door closes. (Detention
   must be interesting or it's a timeout — ADR 0006 said so itself.)
8. **"Cell" collides with "cell."** The player group (v0.5) and the room the
   Watch throws you in share a word. → Rename the player group; the holding
   cell keeps the word (it had it first, and every MUD player knows what a
   holding cell is). Candidate: **circle** — already in the fiction ("the
   kettle circle"), and `circle form <name>` reads naturally.

## The bigger finding: dull

Mechanics verified ≠ fun experienced. The systems chain correctly and the
prose lands, but the moment-to-moment loop lacks pull. Diagnosis deferred to a
dedicated research pass (game feel, addictiveness, intuitiveness — what the
genre calls "juice" and game theory calls incentive gradients), which should
land before the next content systems (quests, implants) so they inherit the
answers rather than the problem.

## Feature requests from the same session

- **ASCII map** — promoted from the parking lot after five versions of
  deliberate deferral; disorientation stopped being tonally useful and
  started being friction.
- **Quest system** — generalize the broker pattern so any NPC can hand out
  errands; the broker proved the shape works.
- **Equipment/implants** — 3M's implant catalog (see
  [third-millennium-mud.md](third-millennium-mud.md)) adapted to the Grid.
- **Circle benefits** — the pay side of trust, already owed by ADR 0008.

Sequencing decisions from all of this: [roadmap.md](../product/roadmap.md)
v0.7 through v0.11.
