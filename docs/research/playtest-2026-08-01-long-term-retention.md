# Ten personas, a different question: will anyone still be here in a year?

The first round ([2026-07-20](playtest-2026-07-20-ten-personas.md)) asked whether a new
player's first evening goes smoothly. It mostly does now, and this round doesn't
re-litigate it. This round asks Lauren's actual question: **play as someone who wants
to keep playing for years, and judge everything from that seat.** Does the world hold
up past the first session? Is there a reason to log in *today* specifically? What's
unbalanced? Where does content visibly run out?

Same ten accounts, same credentials source (`dev-notes.md`), same live dev server
(post-ADR-0019, v0.27 — records archaeology, vouching, suspected-not-proven, the
propaganda engine, the interactive Orientation Wing, and opposed-check resolution are
all live and postdate the last round). Per Lauren's brief, none of the ten were near
endgame going in — the most-advanced (`syme`, `claude`) sat around sabotage/observation
7-8 of 50. Rather than shallow-touch all ten again, this round pushed two personas
(`syme`, `claude`) through real, sustained grinding on the live server — telnet-driven,
one command at a time, reading every response — and used the tuning file and source to
reason carefully about the parts of "years of play" that one evening's grinding
genuinely can't reach. Every number below is either read live off the running server or
cited from `world/tuning.py`; nothing here is a guess about what a veteran *would* feel.

## Findings, ranked by how much they matter

### 1. The flagship grind loop has almost no game left in it once you've actually played

Sabotage is ADR 0008's "closest 1:1 mob-grind analogue" — the bestiary is the apparatus.
Live count of the entire world's sabotage targets, right now, on `main`: **five live
sensors**, one in each of Assignment Hall, Unity Plaza, Central Spire Checkpoint, the
Archive Annex, and the Demonstration Corridor, plus one concealed sensor in the
Bolt-Hole (`concealment: 9`, hard to even find). A sixth, the Neon Alley watchscreen, is
permanently dead by design (nobody files the maintenance form) and can never be
targeted. `MaintenanceScript` repairs **exactly one** sabotaged sensor per
`REPAIR_INTERVAL` (600 seconds), oldest first. Sabotage every live sensor in the world
in one sitting — which `syme`, at sabotage skill 8 going in, did in about ten real
minutes of walking and typing — and the entire loop is throttled to roughly six new
targets per hour, world-wide, for every citizen currently playing, combined. There is no
version of "I want to grind sabotage tonight" past the first ten minutes that doesn't
mean standing around waiting for the maintenance crew.

This is worse than it sounds next to the skill curve. `opposed_check()` gives the actor
`skill // CHECK_SKILL_DIVISOR` (5) as a flat bonus to a d20 roll against
`SABOTAGE_BASE_DIFFICULTY (2) + sensor.sensitivity (1-2) + alert * 3`. At skill 8-13 —
already more sabotage experience than any of the other nine personas has ever had —
that's a +1 or +2 modifier. Live result, `syme`, five attempts across the five live
sensors: **four failures, one success.** Each failure is `SABOTAGE_FAIL_EXPOSURE` (12)
plus an incident; exposure went from 3 to 79 in the session, well past `DETAIN_THRESHOLD`
(50), from sabotage alone. The skill only really starts paying for itself past skill 25
(modifier +5) and doesn't stop improving until 50 (+10) — meaning the first half of the
grind is the part that bites hardest and pays the least, exactly backwards from what
"unambiguous, measurable progress" (grind-loops-without-killing.md's own first
ingredient) asks for. A returning player who remembers sabotage as *the* dark-game loop
will find, at any real skill investment, five targets and a ten-minute wait between
batches.

### 2. Couriering is a free, infinite, zero-risk faucet — and that's a balance problem, not a feature

Compare directly. Live-tested with `claude`: two full "quiet"-tier round trips (Ration
Queue → Assignment Hall → Neon Alley → Tenement Row, deliver, walk back), no target
pool, no cooldown on `carry`, and — because the quiet-tier route never crosses the
Checkpoint's scanner gate — **no chance of `CONTRABAND_SCAN_CHANCE` ever firing.**
Exposure crept from 4 to 18 over the whole test purely from routine room visibility,
nowhere near `SWEEP_MIN_EXPOSURE` (20), the floor below which the Watch never samples a
citizen at all. That means a disciplined player working the quiet tier is, provably,
never at risk: the Watch cannot select someone who's never above the floor it uses to
decide whether to look, and the only seizure trigger that exists for couriers is
watch-selection or a scanner crossing, neither of which this route can ever produce.
Compare the payout: `COURIER_JOBS["quiet"]` pays 2 standing (no jackpot risk stated, 15%
chance of +4 regardless), against sabotage's 2 (+3 dark bonus) *if* it lands, against a
50-80% chance of a 12-exposure failure at realistic skill.

For anyone actually optimizing standing-per-hour rather than roleplaying a saboteur,
couriering the quiet tier is strictly better than sabotage: unlimited, unthrottled, and
mathematically risk-free, against a target-starved, failure-prone alternative that's
supposed to be the game's marquee grind. This is the "clearly strictly better strategy"
this round was explicitly asked to look for, and principle 3's whole thesis (*did a
player change their route because of what might be watching?*) has a direct counter-
example sitting in the tuning file: the optimal route for a long-term grinder never has
to change, because it was never watched to begin with.

### 3. Two of the game's three visible progressions have a hard ceiling with nothing behind it

Live-verified on `syme`, who entered this session one point under the shadow ladder's
top tier: one more successful sabotage pushed underground standing from 44 to 49, past
the `SHADOW_TIERS` threshold of 45. `word`'s answer changed from *"you're trusted, a
little more, and you're one of the old hands"* to **"you're one of the old hands.
Nobody says what comes after that, out loud."** That's not flavor text stopping short —
`shadow_standing()` has no threshold past 45; there's nothing "out loud" *to* say. The
sanctioned ladder has the identical shape: `grades.py`'s own docstring for
`next_review()` says at Grade 1, "no further elevation is contemplated," and returns
`(points, None, None)` — merit keeps accumulating past 100 (it's lifetime, so it never
stops), but nothing reads it anymore. Between the two ladders, that's the entire
sanctioned *and* unsanctioned "number that goes up" axis topping out with silence on
both sides. `endgame-and-long-term-goals.md` already named this gap in the abstract
("what is a citizen playing toward, long-horizon") — this round confirms it concretely:
reach either cap through ordinary play (achievable within a handful of real sessions at
these payout rates, not months) and the game has nothing left to say about it.

### 4. The quest and named-lore catalogs are small and permanently exhaust

`world/errands.py`'s entire catalog is **five errands**, ever, spanning both the
orientation clerk's "nobody" chain and the lamp-mender's underground chain. None repeat
(`available_to()` checks `errands_done`, which only grows). Live-tested: `claude` took
and completed "Look Closer" this session (2/5 done now, including "The Rounds" from an
earlier round); `parsons` is at 2/5 from the previous playtest. Once a character has
done all five — genuinely reachable in one or two real sessions, not months — `errands`
returns "Nobody here has work for you" forever, with no mechanism to generate more.
Records archaeology (`world/archaeology.py`) has the same shape one layer down: the
"infinite" generic loop is real (any of 12 case names paired with any of 25 fragment
sentences, drawn without repetition within a case), but the actual hand-authored
content — the three `NAMED_CASES`, the only draws with a real narrative payoff — is a
fixed, small set solved once per citizen and never regenerated. A player who's ground
archaeology for even a modest number of sessions will have read all 25 generic
fragments multiple times (recombined under new case names, but the same 25 sentences)
and solved all three named cases permanently. `world/gear.py`'s catalog is smaller
still: four items total (badge, cuff, dampener, pocket), one per slot, no upgrades,
and the buy command's own rejection text says it outright — *"You already have one.
Sector 9 is not a place of spares."* Every piece of hand-authored, one-time content in
the game is small enough that a genuinely long-term player exhausts all of it quickly;
only the three grind loops are infinite by construction, and finding 1 above shows one
of those three barely functions as one.

### 5. Nothing in the game varies by *when* you log in

Checked the mechanisms that could plausibly give a returning player a reason to check in
today specifically: the login digest (`characters.py::login_digest()`) only reports what
changed in *your own* file since your last session, plus which circle-mates are online
right now — useful for continuity, not a hook. The propaganda engine reacts to a
rolling tally of recent sabotage/courier activity since the last bulletin, reset on
every bulletin fire, never accumulated by calendar time — genuinely session-reactive,
not session-*varying*. Assemblies cycle on a fixed ~16-real-minute loop regardless of
what day it is. There is no login streak, no rotating shop stock, no daily-reset bonus
tier, no time-limited anything. Every mechanic that exists, exists identically whether
this is a player's first session or their thousandth; the only thing that changes
session to session is the player's own progress and the rare trace another player left
behind. For a player who's already hit the ceilings in finding 3 and exhausted the
one-time content in finding 4, there is, today, no design-level answer to "why today."
(One honest asterisk: this round tried to observe a live propaganda bulletin directly —
stayed connected continuously for a window longer than one `PROPAGANDA_TICK` interval
[240s] with a tally that should have crossed the elevated threshold — and none arrived;
a direct DB read afterward showed the tally still sitting unconsumed at
`{"sabotage": 1, "courier": 2}`. The dev server's log showed a multi-hour gap with no
script activity logged at all during part of this session, consistent with the sandboxed
environment's clock rather than the game, the same category of live-verification limit
the propaganda engine's own build flagged in `CLAUDE.md`. Recorded honestly as
inconclusive, not as a confirmed delivery bug — worth a real check outside this
environment before acting on it.)

### 6. Circle projects are the one loop built right for this — but it needs a partner every time

Worth naming on its own, separate from the courier/sabotage comparison: escalating
circle projects (ADR 0013) are genuinely infinite (`circle_projects.start()` can be
called again the moment the previous one clears the registry), have real payout scale
(`PROJECT_PAYOUT` 30, split across members — enough to move most of a shadow-ladder
tier in one completion), and unlike errands or named cases, never run out of content
because they're pure accounting on top of the same sabotage/courier verbs. But Casing
and the Run are solo-completable and the Split, by design, needs two circle members in
the same dead zone at the same time. A long-term solo player — which, per finding 5's
"alive at three players" test, the game is supposed to keep viable — can fill an entire
circle's tally alone and then simply cannot finish. This isn't a bug (ADR 0013 chose
this shape deliberately, over a fully-synchronous heist, specifically to protect solo
viability for the first two stages), but it means the one loop built to escalate
correctly for veterans is also the one loop a genuinely long-term *solo* veteran cannot
complete without recruiting a partner they may not have.

## What worked

The prior round's fixes held up under a much harder push: no regressions found in the
no-match handler, NPC deflection, or the shadow ladder while grinding hard enough to hit
its ceiling. The near-miss telegraphy and patrol reactions still land at real exposure
(`syme`'s patrol tail at exposure 37, the scanner's "confirms everything is working,
which you already knew" line) — the dread mechanics genuinely survive repeated
exposure to them, which is its own small finding. The three grind loops really are
thematically distinct and each passes principle 9 cleanly; nothing sampled this round
smelled of another genre. The shallow end is real and provably safe: the quiet-tier
courier loop (finding 2's problem case) is also proof that a stress-free, low-effort
loop genuinely exists for a returning casual player who just wants a few minutes of
low-stakes progress. And the dossier's unsanctioned-ledger filtering held under load —
`claude`'s file, after two rounds of sabotage grinding, still correctly hides
`sabotage`/`couriering`/`the underground` from the Ministry's own view, exactly as
designed.

## Next-step candidates, ranked

1. **Widen or reseed the sabotage target pool, or slow its exhaustion rate.** The
   flagship grind loop currently throttles to a handful of attempts per hour world-wide
   the moment more than one player is actively grinding it, which directly contradicts
   its own design brief ("the closest 1:1 mob-grind analogue"). More sensors per room,
   sensors that respawn faster than they're destroyed at low population, or a repair
   rate that scales with backlog size are all candidate shapes; not picking one here.
2. **Give couriering's safe tiers real risk, or find the deliberate reason they should
   stay risk-free.** Right now the "quiet" tier is not merely low-risk, it's
   *mathematically* risk-free by construction (never crosses a scanner, never nears the
   sweep floor), which makes it a dominant strategy over the game's intended flagship
   loop. Either that's an accepted shallow-end faucet worth stating explicitly, or it
   needs a floor of ambient risk the current tiers don't have.
3. **Put something above the shadow ladder's top tier and Grade 1.** Both hard-cap with
   literal silence past them. `endgame-and-long-term-goals.md`'s cheapest option (a
   title/status capstone, no new mechanical systems) would close this gap at low
   implementation cost and give the two ladders players actually watch a real answer to
   "then what."
4. **Grow the one-time content pools, or accept and document that they're meant to run
   dry.** Five errands and three named archaeology cases are exhaustible in one or two
   real sessions; if more hand-authored content isn't coming, that's a legitimate
   choice, but it should be a stated one rather than something a long-term player
   discovers by hitting a wall.
5. **Something that varies by calendar day, however small.** No mechanic currently
   answers "why log in today." Even a cheap, low-commitment version (a bulletin flavor
   that reads differently by day, a courier tier that's better on some days than
   others) would be a first answer where there's currently none at all.
6. **Re-verify propaganda bulletin delivery outside this sandboxed environment.**
   Finding 5's asterisk is a real open question, not a confirmed bug — the dev server's
   own log showed unexplained multi-hour gaps in script activity during this session
   that look environmental rather than game-logic, but it deserves a clean live check
   before anyone trusts or distrusts the mechanic on this round's evidence alone.
7. **Carried over from `future-features.md`: `flip`'s usage still hasn't been checked.**
   Still true after this round — neither of the two personas pushed hard this session
   used it either. The standing "fold it into `recruit` if nobody's used it by the next
   playtest gate" clause has now survived two playtest gates unchecked.
