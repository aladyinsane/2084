# Endgame and long-term goals: what is a citizen playing *toward*?

Lauren's question, 2026-07-28: what is the endgame? Reaching the top of a ministry
and enacting your own rules? "Freeing your mind" from the Grid? This doc is the start
of that thinking, not a decision — she asked to keep thinking about it, and it's
relevant to the tutorial rework (docs/decisions, TBD) since a good tutorial ending
needs at least a near-term answer to "what do I do next," and ideally gestures at
a longer horizon too.

## 1. Why this is answerable now, and wasn't before

[future-features.md](../product/future-features.md) already named this gap on
2026-07-19: **"Endgame paths (escape / overthrow / inner circle)... Why not now:
endgames only mean something once the midgame exists."** That's worth checking
rather than assuming still true. As of this writing the midgame is substantially
built: three institutional ladders (Records/Order/Commerce standing, Clearance,
Citizen Grade), a full trust machine (circles, vouching, reputation-travel,
suspected-not-proven leaks), two solo grind loops plus a third narrative one
(sabotage/courier/archaeology), and a shadow ladder giving underground standing its
own legible progression. The three candidate directions that 2026-07-19 entry
already named map almost exactly onto what got built since — which is either a good
sign the instinct was right, or just a sign the game's systems were always going to
converge on these three shapes. Worth naming as read, not certainty.

## 2. What's already decided, and constrains the answer

Four things from [principles.md](../product/principles.md) and
[orwell-1984-source-material.md](orwell-1984-source-material.md) rule out entire
categories of "ending" before any brainstorming starts:

- **No death, ever** (principle 5, [ADR 0006](../decisions/0006-conflict-is-non-lethal.md)).
  Whatever "winning" looks like, it isn't surviving to a finish line — there's no
  finish line shape that death-as-failure normally provides.
- **Alive at three players, forever** (principle 8). 2084 is a persistent MUD, not a
  campaign with credits. Nothing can be a single canonical "you have completed 2084"
  event that stops mattering the moment it fires — that's a single-player-game
  shape, not a MUD shape. Whatever this is, it has to work as a *status* other
  players can still see and react to, not a curtain call.
- **Resistance is dangerous and costly, not pointless — but not clean either**
  (principle 10, the source doc's "deliberate infidelity" section). We explicitly
  reject the novel's total-defeat ending. We have not said the opposite extreme (a
  clean, total, bloodless revolutionary win) is right either — principle 10's own
  text only promises players can "carve out space," which is a narrower, harder-won
  thing than "overthrow the government."
- **Hierarchy is functional and co-optive** (mechanism 3, from Goldstein's book
  within the novel itself: the Party absorbs able proles specifically *so that*
  talent never accumulates as a threat outside it). If a "climb to the top" ending
  exists, the source material's own logic says it should NOT read as escaping the
  system — reaching real institutional power inside a surveillance state is being
  handed a longer leash, not a key. `judge`ADR 0010, the reputation-travel work) and
  every clearance mechanic already model "rising costs you scrutiny" honestly
  (`judge`, [ADR 0010](../decisions/0010-reputation-travels-judge-reads-citizens.md),
  is the sharpest example: the further you rise, the more of your history other
  players can read back); an endgame that suddenly let power feel free at the top
  would contradict everything built so far.

Those four constraints alone already answer the "clean revolutionary victory" and
"beat the game" shapes: neither fits. What's left is genuinely open.

## 3. Three candidate long-horizon peaks

Not mutually exclusive. Not a single canonical ending — three different long-term
things a citizen could be understood (by themselves, and by other players) to be
*becoming*, each mapping onto a ledger the game already tracks separately and keeps
deliberately walled off from the others (`UNSANCTIONED_SKILLS`/`_FACTIONS` in
tuning.py is the wall). None require inventing a "game over" state; all are framed
as a status worth reaching, visible the way Grade or the shadow ladder already are.

### A. Inner Party — the sanctioned peak
Climb the existing ladder (standing, Clearance, Grade) all the way, honestly, to
real institutional authority — a ministry post with actual levers, not just a
title. Per §2's fourth constraint, this should not read as winning free of the
Grid; it should read as becoming the most-watched, most-legible person in the
building, who has *earned*, at commensurate personal risk, the ability to pull a
small number of real levers other citizens can't (protect a name, bury a specific
incident, look the other way once). The "win" is genuinely ambivalent — you have
power, and the Grid has more of you than it has of anyone. This is the closest
match to Lauren's "reach the top post and enact your own rules" framing, played
straight rather than subverted, but the source material argues hard for keeping
the ambivalence rather than resolving it into triumph.

### B. Doublethink — the underground peak
Build a life so thoroughly off the books that the recorded self stops being the
real story. This is "free your mind" made mechanical rather than literal: the
still-undesigned doublethink feature ([parked from ADR 0011](../product/future-features.md#doublethink-seeing-the-ministrys-edits-from-adr-0011-2026-07-23))
— seeing the gap between what your file says and what actually happened — is the
natural capstone reward for this path, not a separate feature. The shadow ladder,
circle projects, vouching, and archaeology already build the *approach*; doublethink
would be the moment the approach pays off as a genuinely different way of seeing
the game's own records. Whether this should also functionally reduce how much the
sweep can touch you (a real mechanical escape, not just narrative flavor) is a real
open question — see §5.

### C. What outlasts you — the relational peak
Not personal at all: how much of the underground's durable infrastructure exists
because of you. Circles you helped build that outlived your own membership, backers
you vouched for who made it, projects completed, an informant network that's still
running. This is the closest thing to "overthrow" that doesn't require the game to
depict an actual, one-time, world-changing revolution (which principle 8 rules out
structurally) — it reframes overthrow from an event to an accumulating property of
the world, which is exactly the shape ADR 0013's "profitable once, costly as a
career" invariant was already built to reward. The novel's own Brotherhood
ambiguity (mechanism 6: it may be entirely a Thought Police fabrication) is worth
keeping as a design option here too — nothing says a citizen's downstream network
is ever *provably* real to them; it might read entirely through gossip, the way
`listen` already works.

## 4. What doesn't fit, and why

- **A single "you win 2084" state.** Contradicts principle 8 outright. Whatever
  ships, multiple players need to be able to reach it independently, repeatedly,
  without it stopping mattering for the world.
- **A clean, bloodless, total revolution.** Contradicts principle 10's own
  "dangerous and costly" language, and would need the game to depict a world-state
  change every player experiences, which no persistent MUD can really do without
  effectively ending itself for everyone at once.
- **"Escape" read as leaving Sector 9 geographically.** Nothing in the current
  world model has an "outside" with any content in it (the Perimeter/Industrial
  Fringe is pure worldbuilding-ideas.md speculation, itself gated behind the
  "Big-world expansion" trigger that hasn't fired). Escape-as-geography is a
  different, much bigger commitment than escape-as-psychological-state (peak B
  above), and isn't ruled in or out here — just flagged as a separate, larger
  question if it's ever wanted literally.

## 5. Open questions, for whenever this picks back up

- **One capstone reward each, or a genuinely branching endgame?** The three peaks
  above could each just be a title/status (cheap, low-risk, matches how Grade
  already works) or could each unlock real, distinct mechanical capability (bigger
  commitment, more interesting, more to balance). Doesn't need deciding before the
  tutorial ships — "climb toward Grade 1 / build real underground standing" is
  already a suf­ficient near-term answer regardless of how this resolves.
- **Does doublethink (peak B) grant real escape from the sweep, or only insight?**
  A citizen who's built enough of a hidden life *seeing* the gap between record and
  truth is one thing; actually becoming harder to detain because of it is a real
  balance change, the same category of question ADR 0011's own doublethink note
  already flagged as undesigned.
- **Are the three peaks meant to be roughly parallel in reachability**, or is one
  deliberately the "true" long-term aspiration and the other two are earlier
  way-stations? The novel itself doesn't resolve this cleanly (Winston never
  actually reaches any of these) — the answer here is closer to "what kind of story
  does 2084 want returning players to be telling about their own citizen" than
  anything strictly game-theoretic.
- **How much of this needs to be legible to a brand-new player at all?** The
  tutorial rework's ending needs *something* to gesture at beyond "grade up," but a
  five-minute-old citizen probably shouldn't be handed all three long-horizon peaks
  at once — that's exactly the kind of front-loaded information the-first-hour.md
  already warned against. Likely answer: the tutorial names the near-term ladder
  concretely and the existence of "further" without spelling out all three, and a
  dedicated feature (maybe tied to `word`, maybe its own reveal) is what actually
  teaches a returning player about the longer horizon. Not decided here.

## Sources

- [principles.md](../product/principles.md), principles 5, 6, 8, 10
- [orwell-1984-source-material.md](orwell-1984-source-material.md), mechanisms 3
  and 6, and "What we deliberately do not take"
- [future-features.md](../product/future-features.md)'s "Endgame paths" entry
  (2026-07-19) and "Doublethink" entry (2026-07-23)
- [game-theory-of-the-grid.md](game-theory-of-the-grid.md)'s design invariant,
  "betrayal profitable once, costly as a career" — the shape peak C borrows
