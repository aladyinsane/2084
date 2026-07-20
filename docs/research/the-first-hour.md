# The first hour: familiarity, learning curves, and who we chase away

Prompted by Lauren's concern (2026-07-19): the world is right, but there is
too much to learn, and the curve may chase players away before the game gets
to be itself. This doc checks that concern against the onboarding and
retention literature, then names what to build. Companion to
[fun-and-game-feel.md](fun-and-game-feel.md) (which asked "is it fun once you
understand it?") — this one asks "does anyone survive long enough to
understand it?"

## 1. The concern is well-founded, and quantified

- Retention research across genres puts the brutal number early:
  [roughly 70% of new users abandon within the first three days](https://www.xtremepush.com/blog/new-player-churn),
  and the first session decides most of it. For a niche genre with a small
  funnel (a MUD in 2026), losing the curious at hour one is existential —
  there is no marketing budget refilling the top.
- [Cognitive overload is the named killer](https://gdevelop.io/blog/improve-game-tutorials):
  too many systems, terms, and decisions at once. Players quit not because a
  game is deep but because it is deep *immediately*.
- Our own evidence agrees: the
  [first human playtest](playtest-2026-07-19-first-human.md) hit command
  overwhelm and unexplained stats before it hit anything fun. v0.7 fixed the
  sharpest edges (naming, helpfiles, `score`), but organization is not the
  same as sequencing — the full surface still arrives at once.

## 2. What the literature actually prescribes

**Progressive disclosure, one mechanic at a time.**
[Tutorial-design consensus](https://www.gamedeveloper.com/design/how-onboarding-should-be-applied-to-tutorials)
is unusually uniform here: show only the controls relevant to the current
task; introduce mechanics singly and let each settle before the next;
[teach by doing, never by wall of text](https://adriancrook.com/best-practices-for-mobile-game-onboarding/).
The Orientation Wing already teaches by doing (the Demonstration Corridor
raises your Exposure to explain Exposure) — what it doesn't do is *withhold*.
A new citizen who types `help` sees the whole verb surface on day one.

**A visible ladder, because progress you can't see doesn't motivate.**
The [goal-gradient effect](https://home.uchicago.edu/ourminsky/Goal-Gradient_Illusionary_Goal_Progress.pdf)
(Hull 1932; resurrected by Kivetz et al.) is one of the most replicated
findings in motivation research: effort rises as perceived distance to a goal
shrinks, and *invisible* progress reads as no progress. Its corollary, the
[endowed progress effect](https://medium.com/@davidteodorescu/design-perfect-ux-tasks-the-endowed-progress-effect-7461ca20076c),
shows that granting some progress up front measurably raises completion.
Levels work not because numbers are fun but because they are the most legible
progress bar ever designed. 2084 has real progression (influence, skills,
clearance, standing) and displays none of it as a ladder. A veteran mudder's
first question — "am I leveling?" — currently has no answer on screen.

**Genre literacy is a resource; spend it.**
The roguelike → roguelite story is the cleanest case study: traditional
roguelikes' [steep curve kept them unsellable to a broad audience](https://en.wikipedia.org/wiki/Roguelike),
and the games that broke out did it by wrapping the same identity in
*familiar meta-progression*, not by abandoning the genre. The lesson cuts
precisely for us: keep the strange world, present it through shapes the
player already knows. We partly do this (courier tiers read as dungeon
difficulty; `score` exists) — the gap is the top-level frame.

**The best-in-class MUD does all of the above.**
[Achaea](https://www.achaea.com/newbie-guide), the standard recommendation
for first-time mudders, opens with a guided intro adventure that teaches
basic commands *inside* a short story at the player's own pace, then layers
newbie-only benefits (a dedicated question channel, guide NPCs, rescue
mechanics) and is [still actively reworking early progression for retention
in 2026](https://www.ironrealms.com/2026/03/17/achaea-and-aetolia-make-it-easier-to-max-class-skills/).
One warning from their forums worth keeping: veterans recall that a fully
*automated* newbie pipeline made the newcomer's life
["incredibly quiet and lonely"](https://forums.achaea.com/index.php?p=%2Fdiscussion%2F5333%2Fgetting-the-newbie-experience-back)
— systems can sequence the curve, but a human saying hello retains harder
than any tutorial. (Alter Epoch literally
[colors new players cyan](https://writing-games.org/building-a-better-mud) so
veterans spot and welcome them.)

## 3. The diagnosis for 2084

The familiar shapes already exist — the grind is mob-grinding, errands are
quests, gear is equipment, exposure is a threat meter, influence is XP. Two
things make the curve feel steep anyway:

1. **No top-level ladder.** The player has five progression currencies and
   no single number that says "you are getting somewhere." Familiarity
   problem, not depth problem.
2. **Everything at once.** The verb surface, the stats, and the vocabulary
   all arrive in the first ten minutes. Sequencing problem, not size
   problem.

Neither diagnosis calls for new systems. Adding combat + XP as *additional*
systems would lengthen the syllabus it's meant to shorten. What the
literature supports is: (a) surface the existing progression as one familiar
ladder, (b) sequence the existing surface so it arrives in learnable order,
and only then (c) consider whether a combat-shaped activity (the parked
composure-sparring loop) is still missing.

## 4. Assignments (the tiered plan)

- **Tier 1 → v0.12, Citizen Grades.** A single visible grade derived from
  numbers we already track, in the prompt and the dossier, with a
  reclassification fanfare and progress toward the next review. Diegetic for
  free: no institution on earth loves ranking citizens more than this one.
  Endowed progress: orientation itself credits the first progress a citizen
  sees. The unsanctioned ledger must not feed it — the Grid ranks what the
  Grid can see.
- **Tier 2 → v0.13, The First Hour.** Progressive disclosure of the command
  surface keyed to orientation progress (shown, never locked); a `next`
  hint that reads game state and names one sensible thing to do; the
  remaining familiar aliases (`quests`, `level`). Timed first-session
  playtest as the gate.
- **Tier 3 → parked, pending Lauren.** Composure sparring (grind-shelf
  option 3) is the combat-shaped answer if tiers 1–2 aren't enough. Decide
  *after* measuring the retiled first hour, not before.

## Sources

- https://www.xtremepush.com/blog/new-player-churn (first-days churn)
- https://gdevelop.io/blog/improve-game-tutorials (cognitive overload, tutorial failure)
- https://www.gamedeveloper.com/design/how-onboarding-should-be-applied-to-tutorials
- https://adriancrook.com/best-practices-for-mobile-game-onboarding/ (progressive disclosure)
- https://home.uchicago.edu/ourminsky/Goal-Gradient_Illusionary_Goal_Progress.pdf (goal gradient)
- https://medium.com/@davidteodorescu/design-perfect-ux-tasks-the-endowed-progress-effect-7461ca20076c
- https://en.wikipedia.org/wiki/Roguelike (the roguelite accessibility lesson)
- https://www.achaea.com/newbie-guide + https://www.ironrealms.com/2026/03/17/achaea-and-aetolia-make-it-easier-to-max-class-skills/ (best-in-class MUD onboarding)
- https://forums.achaea.com/index.php?p=%2Fdiscussion%2F5333%2Fgetting-the-newbie-experience-back (automation-loneliness warning)
- https://writing-games.org/building-a-better-mud (new-player visibility)
