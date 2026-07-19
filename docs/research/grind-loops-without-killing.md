# Grind loops without killing: what other MUDs do, and what 2084 could do

Research toward a question Lauren posed after v0.4: *experienced mudders arrive
wanting the familiar shape of combat — go somewhere, fight something, get
numbers, repeat. We have deliberately forsworn lethal combat (ADR 0006). What
is our equivalent?* This doc collects what the genre does and extracts the
load-bearing parts, so any 2084 design keeps the **feel** of the grind without
importing a bestiary.

## 1. Why the mob-grind works (the psychology, briefly)

The literature on grinding converges on a short list of ingredients
([Komad](https://medium.com/@milijanakomad/product-design-and-psychology-the-role-of-grinding-in-video-game-design-72a2c70a9ae4),
[Seasoned Gaming](https://seasonedgaming.com/2020/05/21/the-psychology-of-grinding-in-video-games/),
[Gamescrye](https://gamescrye.com/blog/designing-a-progression-focused-game-without-the-grind/)):

- **Unambiguous, measurable progress.** You were 49; now you are 50. The
  number moved because of what you did.
- **Small, frequent rewards on a partly variable schedule.** Every kill pays
  a little; occasionally one pays a lot (the rare drop). Variable-ratio
  reinforcement is the strongest schedule known.
- **Mild flow.** The activity is low-intensity and repeatable — you can do it
  tired, half-watching, in fifteen-minute sessions. It is *relaxing*, which
  bounded, telegraphed risk does not break (danger you opted into is spice;
  danger you can't read is stress).
- **Visible transformation over time.** Sessions accumulate into a character
  who is durably different.
- The failure mode: when the grind becomes **mandatory rather than
  meaningful**, motivation flips extrinsic and burns out.

None of these ingredients is "violence." The corpse is just the receipt.

## 2. What the genre actually does

- **Diku-line combat MUDs** (Discworld, and the 3M revival we field-researched):
  ["Combat is the most common way to gain experience, items, and money"](https://discworld.starturtle.net/lpc/playing/documentation.c?path=/concepts/combat)
  — the mob-grind is the *default faucet* for all three currencies at once,
  which is exactly why it dominates: one loop, three rewards.
- **Iron Realms games (Achaea etc.)** wrap the same faucet in factional
  purpose — [deep PvP, political systems, player-run cities](https://www.ironrealms.com/mud-games/30-mud-games/)
  give the ground-out power somewhere to matter.
- **Sindome** (dystopian cyberpunk, the closest cousin to us in tone)
  [rewards roleplaying over stat grinding](https://mudstats.com/World/Sindome)
  and keeps death survivable through clone mechanics — conflict is chronic,
  recovery is slow and costly rather than terminal, and reputation/faction
  standing is the real scoreboard.
- **RPI MUDs (Armageddon)**: ["while conflict abounds, the game is not about
  killing things"](https://writing-games.com/game-design-investment-stakes-conflict-rpi-muds/)
  — thematic divisions generate the conflict, and stakes come from
  *investment* in a character, not from XP. Notably, players report
  [stealth as the overpowered discipline](https://musoapbox.net/topic/2028/armageddon-mud) —
  in a scarcity world, not-being-seen is the strongest stat. (We already
  built that game; ours just says so out loud.)
- **Our own 3M field research** (docs/research/third-millennium-mud.md): the
  revival's grind is classic mob-clearing, and its lesson for us was mostly
  cautionary (magic-missile-in-the-implant-catalog → principle 9). But its
  *services-as-places* pattern — you go somewhere specific to spend the
  grind's proceeds — is the piece that made grinding legible: the loop has a
  geography.

## 3. The extraction: what a 2084 "grind" must provide

A 2084 analogue of "killing NPCs for XP" needs, concretely:

1. A **repeatable verb** aimed at a **target that exists in the world**
   (a place or object you travel to, not a menu),
2. that pays **immediately and visibly** in our currencies (skill ticks,
   standing, exposure relief — the numbers already in the prompt),
3. with **bounded, telegraphed risk** you opt into for better pay,
4. an occasional **jackpot** (variable schedule),
5. and **no requirement** that anyone do it (principle: meaningful, not
   mandatory).

And one constraint the genre doesn't have: per ADR 0006 and principle 9,
the loop must pass through the fiction. Nothing in Sector 9 hands out
experience points for violence, because violence against the state is
suicide and violence against citizens is the state's monopoly. What the
Grid *does* have in infinite supply: **apparatus, paperwork, and other
people's problems** — all of which can be farmed.

The candidate designs extracted from this research live in
[future-features.md](../product/future-features.md#the-grind-shelf) and were
presented as options rather than decisions — an ADR only exists once Lauren
picks a direction.

## Sources

- https://medium.com/@milijanakomad/product-design-and-psychology-the-role-of-grinding-in-video-game-design-72a2c70a9ae4
- https://seasonedgaming.com/2020/05/21/the-psychology-of-grinding-in-video-games/
- https://gamescrye.com/blog/designing-a-progression-focused-game-without-the-grind/
- https://discworld.starturtle.net/lpc/playing/documentation.c?path=/concepts/combat
- https://www.ironrealms.com/mud-games/30-mud-games/
- https://mudstats.com/World/Sindome
- https://writing-games.com/game-design-investment-stakes-conflict-rpi-muds/
- https://musoapbox.net/topic/2028/armageddon-mud
- Field research: docs/research/third-millennium-mud.md
