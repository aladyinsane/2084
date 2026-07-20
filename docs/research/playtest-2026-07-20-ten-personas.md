# Ten personas, one evening: a play-style sweep of Sector 9

Per Lauren's ask (2026-07-20): ten test characters with different play
styles, played as human-like as an automation-driven telnet session can
manage — including the wrong commands humans actually type. All sessions on
the live server, same build as main (post v0.13). Credentials in the
gitignored dev-notes.md.

| Citizen | Style | Arc played |
|---|---|---|
| martin | genre-blind newbie | natural-language commands, then followed FORM 1-A to Grade 5 |
| syme | explorer | examined everything, walked the whole graph, pushed the Spire gate, found the Bolt-Hole |
| rutherford | underground-first | chalk → failed sabotage (incident) → courier run delivered → papers ambitions |
| ampleforth | roleplayer | say/emote/pose, addressed NPCs, spoke on gridwide |
| katharine | cautious nobody | helpfiles first, orientation, The Rounds, tried to hide, retreated to the tunnels |
| tillotson | min-max grinder | skipped orientation, report → work loop, priced the shop |
| wilsher | socializer | who, gridwide, recruited into a circle in Tunnel B, signal, stash |
| bumstead | idler/casual | logged in, walked to the plaza, idled 18 minutes |
| parsons | compliant climber | Visible Usefulness ×3 shifts → Grade 3, bought the wellness monitor |
| claude | MUD veteran | kill/attack/flee/cast, circle invite, started Form C-1 |

## What broke, in order of how much it matters

### 1. The failed-command suggester is actively hostile (systemic; 6 of 10 personas hit it)
Evennia's default "Maybe you meant..." fuzzy matcher answers wrong input by
suggesting, variously: |csabotage|n (to martin typing `go east`, to
ampleforth typing `ask clerk about badges`), |cstash|n (to martin typing
`stats`), and the OOC account verbs |ccharcreate|n/|cchardelete|n/|csetdesc|n
(to claude typing `attack`/`flee`). Three distinct failures in one
mechanism: it **leaks the unsanctioned curriculum** the whole design keeps
in chalk, it **breaks the fiction** with engine verbs no citizen should see,
and it is **useless as help**. The commonest newbie error of all — typing a
direction with no exit — returns "Command 'west' is not available. Maybe you
meant 'setdesc'" instead of the one useful fact (what ways actually lead out).

### 2. The world is deaf to the player's instincts
- `kill`, `attack`, `flee`, `cast` — the four most predictable veteran
  inputs in a game whose whole thesis is what replaces them — get generic
  boilerplate. This is the best tone moment in the game, unwritten.
- `talk to clerk`, `ask clerk about badges`, `say good morning` in a room
  with two NPCs: silence. The roleplayer's entire verb set lands on nothing;
  not even a deflection ("The clerk does not look up").
- `hide`, `sneak` (the cautious player's instinct in a surveillance game!),
  `where am i`, `read placard`, `go east`, `stats`: all dead, some with
  leaky suggestions per finding 1.

### 3. Described props aren't examinable — including a designed tell
`look blankets` in the Bolt-Hole: "Could not find 'blankets'." The too-neat
blankets are one of the honeypot's fair-warning layers, and they cannot be
looked at. Same for the cots, rations, kettle. The explorer persona reads
rooms closely — exactly the player the honeypot's warnings were written for.

### 4. The underground has no ladder
rutherford ended his session with underground standing 2, couriering 1, an
incident, and a dossier reading "Merit on record: 0." Correct — the Grid
ranks what the Grid can see — but his *only* progress readout is one line
the broker recites mid-`carry`. The v0.12 research applies verbatim to the
shadow economy: progress you can't see doesn't motivate. (Kept out of the
dossier by construction; it wants its own diegetic surface, not a file.)

### 5. The casual middle is dead air; the long idle is a farm
bumstead's 18 idle minutes at the plaza contained zero world events — the
assembly cadence (~16 min) can miss an entire casual session. Meanwhile the
known risk from v0.12 stands: leave the client open long enough and the same
system farms you for absence incidents. The event cadence is wrong at both
ends, and fixing it needs the design decision already parked in
future-features.md.

### 6. Small frictions worth one line each
- `work` off-cooldown gives no sense of when the next shift opens; the 45
  dead seconds at a post have nothing in them (this is where "a bit dull"
  still lives).
- Player names render lowercase in emotes/says ("ampleforth straightens...").
- Errand `take` far from the giver fails softly; a returning player who
  misremembers where the clerk stands gets no pointer to them (this
  playtest's driver made exactly this mistake unprompted).
- Account creation throttles at 2 per 10 min per host (Evennia default) —
  fine in production, surprising in a group-of-friends launch night.

## What worked (deliberately brief, genuinely felt)

The v0.12/v0.13 spine held up under every style: martin (who had never seen
a MUD) reached Grade 5 by following the forms; parsons rode "3 to go" to
Grade 3 exactly as the goal-gradient research predicted; tillotson skipped
orientation entirely and the ladder met him anyway; `next` was correct at
every stage it was asked. The circle flow (invite → join → signal → stash)
read like fiction and worked like machinery, the courier loop closed clean
for a day-one criminal, and the gate palm, the chalk, and the errand risk
labels all landed. Ten styles, zero crashes, zero dead ends.

## Next-step candidates, ranked

1. **"The Grid hears you": a command-not-found overhaul** — fixes findings
   1 and 2 in one scoped feature. A custom no-match handler: unknown
   directions answer with what actually leads out; the instinct verbs
   (kill/attack/flee/cast/hide/sneak/talk/ask/where/read/stats/go) each get
   a bespoke line in the Ministry's voice, with a mechanical pointer where
   one exists; suggestions come only from the sanctioned surface, never
   from the chalk, never from the engine. Touches every persona's first
   ten minutes; no new systems; pure intuitive-and-tone. **The next best
   next step.**
2. **NPC deflection lines** — one canned, personality-true response per NPC
   to being spoken at. Cheap, transforms the roleplayer's first hour.
3. **The shadow ladder** — an underground reputation surface (whispered,
   never filed). Design fits finding 4 and the v0.12 research; medium size.
4. **Prop coverage in signature rooms** — make described tells examinable,
   extend the ADR 0007/principle 9 lint to cover them.
5. **Event cadence + idler policy** — needs Lauren's parked design decision
   on what idling means; not started unilaterally.
