# Round two: the ten personas continue, and a fresh citizen walks the Wing

Per Lauren's ask (2026-07-22): continue all ten personas from the 07-20
playtest, and create a genuinely fresh account to test v0.15's hands-on
Orientation Wing, which none of the ten had seen. All sessions on the live
dev server (telnet 4000), same raw-socket method as round one. Credentials
in the gitignored dev-notes.md; hopkins's are new this round.

| Citizen | Style | Arc played this round |
|---|---|---|
| **hopkins** | fresh account, genre-blind newbie (**new this round**) | created via `create hopkins <pw>`; full Orientation Wing start to finish; `report`, first `work` shift; the post-tutorial `next`-chain; full nomatch and helpfile audit |
| martin | genre-blind newbie (continuation) | walked out of the Demonstration Corridor, `report`ed (Steward, Commerce), a `work` attempt at the wrong post, `next` |
| syme | explorer | re-checked the Bolt-Hole's props (still unexaminable), `sneak`, nomatch |
| rutherford | underground-first | courier board (`carry`), `judge` on the broker, `papers` (priced out — standing 2 of 6 needed), `next` |
| ampleforth | roleplayer | `say`/`emote`/`pose` at the requisitions clerk, `ask`/`talk to` (still generic deflection) |
| katharine | cautious nobody | `hide`/`sneak` while genuinely inside a dead zone, resumed "The Rounds" errand |
| tillotson | min-max grinder | `work` loop (Commerce standing 3→6), confirmed the abridged `help` card never clears since orientation was skipped |
| wilsher | socializer/conspirator | `circle` status (still linked with claude from round one), `gridwide`, `signal` (no one reachable) |
| bumstead | idler/casual | brief check-in at Unity Plaza; no ambient events in the short window |
| parsons | compliant climber | `grade` (still Grade 3, 24 to Grade 2), `errands`, `work` |
| claude | MUD veteran | re-ran kill/attack/flee/cast/hide/steal/stats; surfaced a 35-entry dossier bloat in passing |

## What broke, in order of how much it matters

### 1. `help the grid` — the game's own most-repeated piece of advice — returns the wrong thing, for everyone
Typing exactly what the game tells you to type (`help the grid`, and its
aliases `help basics` / `help 2084` / `help sector 9`) does not show the
"the grid" file-based help entry. It shows a **command-category listing**
instead — because the help entry's `category` field and its `key` field are
both literally `"the grid"` (`game/world/help_entries.py:68-93`), and
Evennia's `CmdHelp` resolves an exact category-name match before it resolves
a topic key. Live output for `help the grid`:

```
-----------------------------------Commands-----------------------------------
-- The Grid --------------------------------------------------------------
apply      buy        dossier    errands    grade      list       listen
map        next       observe    petition   remove     report     wear
work
---------------------------------Game & World---------------------------------
-- The Grid --------------------------------------------------------------
exposure    the grid    visibility
```

No prose, no explanation — just a command index, twice. This is severe
specifically because the game keeps pointing here: `game/commands/nomatch.py:58`
tells anyone who types `kill` to run `help the grid`; the entry itself is
meant to be the one-paragraph "what is this game" explainer. Confirmed
unreachable by every alias, for hopkins and again for syme.

### 2. `help standing` confirmed dead, exactly as suspected
```
>>> help standing
No help found
There is no help topic matching 'standing'.
Other topic suggestions: buy  grade  papers  pose  work
```
"Standing" (the per-faction ledger — `caller.db.influence` internally,
shown in `dossier` as "Standing with institutions") has zero dedicated
coverage, unlike exposure and visibility. It's mentioned only in passing,
inside the now-unreachable "the grid" entry (`help_entries.py:86`) and
scattered across room placards and command flavor text. A player can't see
their current standing anywhere until they've *earned some* — the dossier
line only appears once `influence` is non-empty (`commands/dossier.py:82-86`)
— and nothing in the guided path ever states plainly "this is called
standing, here's where it comes from, here's where you spend it" in one
place a player would think to look.

### 3. `next`, confirmed: one funnel to the safe chain, never an explicit menu of playstyles
Traced and live-verified. `CmdNext._advice` (`game/commands/firsthour.py:117-175`)
checks, in order: active errand → unoriented → hot exposure → an
errand-giver in the current room → **the errands catalog in dict-insertion
order** — and the code says why, in its own comment:

> `# Catalog order on purpose: the clerk's safe chain leads it, so a` `# brand-new citizen is pointed at the shallow end first.` (`firsthour.py:163-164`)

Because the orientation clerk's three-step "nobody" chain (`rounds` →
`usefulness` → `countable`) is declared first in `world/errands.py`, and the
lamp-mender's underground-flavored chain (`look-closer` → `legs` →
`four-hands`, paying `tuning.UNDERGROUND` standing) has no prerequisite but
sits later in the dict, `next` will always surface the clerk's chain first
and keep surfacing it until all three links are done. Live-tested for
hopkins/martin/parsons: repeated `next` after `report`+`work` returned the
identical line — `"word is the orientation clerk has a use for a citizen's
legs. Find them and ask after errands."` — every time, with no variation
and no mention of circles, signals, or roleplay. The only place the design
gestures at alternatives is the final fallback, reached only once the whole
catalog is exhausted and no giver is present: *"other parties reward other
things, and chalk is cheap"* — prose, not a menu, and it never names the
underground by name. `help all`'s command index does visibly separate
"-- The Grid --" from "-- The Underground --", so a curious player who runs
it (available even pre-orientation) can infer a second curriculum exists —
but nothing in the guided experience (FORM 1-A, abridged help, `next`)
points there.

### 4. Skipping orientation locks a player out of real `help`, permanently
Confirmed live with tillotson — Grade 5, an assigned function, 11 merit,
6 standing with Commerce, who deliberately skipped the Wing (per round
one's persona table) — and is *still*, this round, shown the beginner
abridged card verbatim on bare `help`:
```
THE PERMITTED FORMS OF ASSISTANCE (ABRIDGED)
Issued to citizens not yet through orientation. ...
```
`db.oriented` is only ever set by walking the Demonstration Corridor
(`world/build.py:406`, the `"orients"` room tag) — nothing else sets it.
`CmdHelpStaged`'s own docstring promises "nothing is ever locked"
(`firsthour.py:79-82`), but a player who exercises the game's explicitly
stated freedom ("ATTENDANCE IS VOLUNTARY") is stuck with the wrong help
card indefinitely unless they know to type `help all` instead of `help`.

### 5. Described props still unexaminable (confirmed again, not new)
`look blankets` / `look cots` / `look kettle` / `look rations` in the
Bolt-Hole all still return `"Could not find 'X'."` — re-confirmed via syme
this round. Unfixed since round one's finding #3, per the brief.

### 6. NPC deflection lines still absent (confirmed again, not new)
ampleforth: `ask clerk about badges` and `talk to clerk` both land on
nomatch's generic "Citizens speak with say..." instinct line rather than a
clerk-specific brush-off. Unfixed since round one's finding #2, per the
brief.

### 7. The absence-incident farm is visibly compounding, and the dossier has no cap for it
claude's dossier this round listed **35 consecutive identical incidents**
("Absent from mandatory civic assembly"), then a 36th distinct one, before
anything else in the file. This is the known, parked idler/event-cadence
issue (round one finding #5) actively accumulating in real, unattended
time — worth noting as live evidence, not a new bug. One adjacent, smaller
observation: `dossier.py` caps "Movements on file" to the last 3 entries
(`movements[-3:]`, `dossier.py:109`) but places no such cap on "Incidents on
record", so a farmed file becomes a wall of repeated text with no
pagination once the cadence issue is eventually addressed.

### 8. Small frictions worth one line each
- `x <item>` — the near-universal MUD shorthand for examine — isn't
  recognized; nomatch's fuzzy-suggester matches it to something unrelated
  (`x kettle` → `"Perhaps: next."`). Harmless (no chalk/engine leak) but not
  useful.
- `help gridwide` returns nothing, though the channel itself works fine
  (`gridwide <msg>` correctly costs +2 exposure, "speaking into a
  microphone" per `tuning.py:121`). Minor, and outside this round's audit
  list.
- `create <name> <password>` at the connection screen only registers the
  account; it does not log you in. A genre-blind player following FORM 1-A's
  promise of an immediate world gets bounced back to the connection screen
  and must `connect` separately. Standard Evennia behavior, not a bug, but
  worth a documented beat given how much design care went into the first
  `at_post_puppet`.

## What worked

The v0.14 no-match overhaul fully holds up under a complete retest: every
one of kill/attack/flee/cast/hide/sneak/talk/ask/where/read/stats/steal,
wrong directions, and command typos (`grad`, `lsit`) was re-verified across
hopkins, syme, katharine, claude, and ampleforth. Every single one returned
an in-fiction, sanctioned-only response — zero leaks of chalk verbs
(`sabotage`, `stash`) or engine verbs (`charcreate`, `setdesc`) anywhere.
Round one's #1 finding is fully resolved.

v0.15's hands-on Wing is a genuine improvement, not just paint: hopkins's
walkthrough fired each room's "try it now" prompt in the right sequence
(map → observe → dossier → grade), and each first-ever use triggered its
`onboarding.py` acknowledgment exactly once, in voice, with everything the
player needed available at each step — no gaps. The Demonstration
Corridor's Grade 6→5 reclassification landed automatically and dramatically
mid-walk. All ten personas' state carried over perfectly across the
fortnight — rutherford's incident and underground standing, wilsher's
circle with claude, parsons's Grade 3 and gear, tillotson's function — zero
crashes, zero corruption across twelve live sessions this round. Helpfile
coverage for the actual command surface (circles, civic, dossier, errands,
gear, map, underground — ~30 commands) is strong: everything audited
resolved to complete, well-written text except standing (systemic, #2
above) and confess/wait/demand, which are correctly unreachable outside
detention by design (they only exist in the `DetainedCmdSet`,
`detention.py:190-215` — a deliberate consequence of the cmdset swap, not a
hole; `CmdHelp` is itself included in that cmdset so a detained player can
still ask).

## Next-step candidates, ranked

1. **Fix the "the grid" help-entry/category collision.** Smallest possible
   scope, highest-visibility payoff: right now the game's own most-quoted
   piece of advice returns the wrong output for every player who follows it.
2. **Give "standing" a real help entry**, mirroring exposure/visibility's
   format, and consider a more discoverable way to see a current total than
   "earn some, then run dossier."
3. **Let `next` name the alternatives once oriented-with-a-function**,
   without abandoning the safe-chain-first design — one line acknowledging
   circles/underground/social exist, matching what "the grid" entry already
   tries to say (once reachable per #1).
4. **Give orientation-skippers an escape from the abridged help card**
   some way other than walking five specific rooms — e.g., promote after N
   turns of play or after taking a function.
5. **NPC deflection lines** — unchanged from round one, still open.
6. **The shadow ladder** — unchanged from round one, still open.
7. **Prop coverage in signature rooms** — unchanged from round one, still open.
8. **Event cadence + idler policy** — unchanged from round one, still open;
   this round's dossier bloat (finding 7) is a concrete argument for
   prioritizing it.
