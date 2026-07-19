# Fun and game feel: why 2084 is "a bit dull," and what to do about it

The first human playtest delivered the verdict every mechanics-first project
eventually hears: the systems chain, the prose lands, and the moment-to-moment
experience doesn't pull. This doc diagnoses why, grounds the diagnosis in what
game research actually knows about pull, and hands concrete shapes to the
upcoming versions (juice pass, quests v0.9, implants v0.10, circle benefits
v0.11).

## 1. The diagnosis: five specific dullnesses

Playing our own game adversarially, the dullness decomposes into five
concrete, fixable problems — none of which is "the premise is wrong":

1. **The optimal strategy is boredom.** The design says "be nobody" is how
   you survive — but we made being nobody *contentless*. In Darkest Dungeon
   the same tension exists (aggression wins, aggression kills) and stays fun
   because [both branches are full of decisions](https://nicolaluigidau.wordpress.com/2024/02/06/the-dynamics-of-stress-in-darkest-dungeon/).
   Our "lie low" branch has nothing to decide. *The fix is not making heat
   mandatory; it's making low-profile play a real activity* (quiet errands,
   observation work, route planning — the map already helps).
2. **The machine is invisible when it matters most.** A Watch sweep that
   *rolls you and misses* is currently silent. That's the single cheapest
   unfired gun in the design: the [near-miss is neurologically almost a
   win](https://news.eternalslots.com/the-psychology-behind-near-misses-in-slot-games/)
   — anticipation stretched between hope and outcome is where engagement
   lives. Every sweep roll against you should be *felt*: a visor that
   lingers, a van that slows and then doesn't stop. Dread we already
   compute and then throw away.
3. **Dead air.** Work cooldown 45s, sweep 90s, assembly ~16min — between
   events, nothing happens *at* you. The world only speaks when it acts.
   Rooms need ambient motion (loudspeaker murmurs, queue shuffles, a
   distant van) on a slow tick, and NPCs need occasional unprompted barks.
   Not information — *texture*. Silence should be a chosen beat, not the
   default.
4. **No goal gradient.** [FTL keeps tension high](https://gogemio.com/best-roguelike-games-to-play-now/)
   because you always have a next-thing with a cost attached. Our player
   finishes orientation and faces... open-ended civic life. The courier
   board is the only "next thing" in the game. Quests (v0.9) are the
   structural fix; the login digest ("since you were last on the Grid...")
   is the cheap session-level fix — principle 8's async traces, finally
   pointed at the player.
5. **Progress has no horizon.** Skills tick invisibly toward a silent cap;
   clearance C-1 is the only unlock and most players won't smell it for
   hours. There is nothing to *want* at the five-minute, one-hour, and
   ten-hour marks. Implants (v0.10) are the natural want-ladder; quest
   chains and circle benefits extend it.

What is deliberately *not* on this list: complexity (v0.7 addressed
legibility), lethality (ADR 0006 stands — Sindome and Armageddon prove
dystopia pulls without corpses), or the premise. The premise is the moat.

## 2. What the research says pull is made of

- **Anticipation beats reward.** Dopamine research on gambling design keeps
  finding that [the hover between hope and outcome stimulates more than the
  payout](https://anteupmagazine.com/2024/07/12/slot-machine-psychology-what-drives-players-to-keep-spinning/).
  Design translation: telegraph *rolls*, stretch *outcomes*, make the
  player watch the scanner hum. (We are a surveillance game. Anticipation
  is literally our subject.)
- **Interesting decisions** — Sid Meier's definition of a game — require
  visible stakes on both branches. Every verb should offer a
  cheap-safe/rich-risky pair, priced legibly (the courier tiers do this
  right; `work` does not).
- **Variable ratio schedules** hook harder than fixed ones — but in an
  ethics-forward design we use them on *flavor and jackpots*, never on
  core progress (fixed +1 skill stays; the occasional windfall varies).
- **Losses must teach.** Darkest Dungeon's punishments stay fun because
  [each one traces to a choice](https://www.jannekeparrish.com/game/darkest-dungeon/).
  Our seizures/detentions already do this well — the playtest chain
  (seizure → exposure → patrol) was the most *game-like* moment we've
  produced. More systems should collide like that.

## 3. The recommendations, sized and sequenced

**Juice pass (cheap, immediate — target: the next PR):**

- J1. **Near-miss telegraphy**: when a sweep rolls a player and misses,
  the player feels it ("a visor lingers on you a half-second too long,
  then moves on"). Ditto scanner gates that roll contraband and miss.
- J2. **Login digest**: "Since you were last on the Grid:" — new file
  entries, circle signals missed, assembly outcomes, repairs in your
  known sector. Async presence (principle 8), pointed home.
- J3. **Ambient texture tick**: a slow script giving watched rooms their
  murmur (loudspeakers, queue shuffle, distant vans; dead zones get drips
  and silence *described*). Rate-limited, room-flavored, skippable.

**Shapes handed to the next versions:**

- **Quests (v0.9)**: every quest states its risk tier up front (the
  courier board pattern); chains end in a *named* reward (an implant, an
  introduction, a clearance sponsor — never bare standing); at least one
  giver offers a genuinely safe "nobody" questline so lying low is a
  campaign, not an absence (fixes dullness #1).
- **Implants (v0.10)**: the want-ladder. Visible in shop/catalog before
  affordable (anticipation), trade-offs not upgrades (state-issued gear
  pays but watches; black-market gear hides but risks), and at least one
  early cheap implant a new player can want in their first session.
- **Circle benefits (v0.11)**: shared goals are the strongest retention
  device MUDs ever found; the stash and joint ops give circles a *project*.

## 4. What we do not import

No energy meters, no daily login streaks, no pay-shaped scarcity, no
fail-forward removal of consequence. The game's ethics are part of its
premise: the Grid manipulates its citizens; the *game* should not
manipulate its players — it should make them feel watched, not farmed.
(Comfort excepted where the fiction is the discomfort: near-miss dread is
the product working.)

## Sources

- https://news.eternalslots.com/the-psychology-behind-near-misses-in-slot-games/
- https://anteupmagazine.com/2024/07/12/slot-machine-psychology-what-drives-players-to-keep-spinning/
- https://nicolaluigidau.wordpress.com/2024/02/06/the-dynamics-of-stress-in-darkest-dungeon/
- https://www.jannekeparrish.com/game/darkest-dungeon/
- https://gogemio.com/best-roguelike-games-to-play-now/
- Prior: [grind-loops-without-killing.md](grind-loops-without-killing.md),
  [playtest-2026-07-19-first-human.md](playtest-2026-07-19-first-human.md)
