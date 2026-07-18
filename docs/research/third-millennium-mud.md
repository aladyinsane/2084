# 3rd Millennium MUD (1996)

The named design inspiration for 2084's character system. This doc records what we could
verify, what we take from it, and what we honestly can't know.

## What the sources say

From the [MudStats listing](https://www.mudstats.com/World/3rdMillennium) (the best
surviving primary-ish source):

- Founded **1996**, English-language, hosted in Europe. Sci-fi theme.
- Codebase: **CircleMUD, heavily modified**.
- Setting: the year 3000, after time travel (invented ~2050, outlawed 2099) tore a
  permanent distortion — "the Nexus" — into spacetime.
- The load-bearing line: *"The question of race and class has been eliminated. All men
  and women are created equal."* Characters were defined by their choices and actions,
  not by a creation-screen category.
- Present-day status: effectively dead — 0 players connected, minimal activity.

Also listed at [Top Mud Sites](https://www.topmudsites.com/forums/muddisplay.php?mudid=3M).

## Honesty about source quality

The MUD is nearly thirty years old and its documentation didn't survive. We could not
recover skill lists, progression details, or reviews describing how the classless design
actually played. **What we take from 3rd Millennium is the principle and the proof of
concept, not a mechanical blueprint.** Anything below the principle level in our design
is our own work, attributed to us, not to a game we can't inspect.

## What we take

### 1. Classless, raceless characters fit a dystopia unusually well

3rd Millennium dropped race and class in *1996*, when nearly every DIKU-lineage MUD was
built on both. In its sci-fi frame the justification was egalitarian ("all men and women
are created equal"). In a 1984-shaped world the same design lands even harder, and darker:

- The state's whole apparatus is *assigning* people functions and revoking them. A
  hard-coded character class would fight the fiction — your "class" should be a stamp in
  a dossier, grantable and erasable, not a database column set at creation.
- The novel agrees: Party hierarchy is functional, not hereditary (see
  [orwell-1984-source-material.md](orwell-1984-source-material.md), mechanism 3).
- "You are what you do" gives the memory-editing mechanics something to bite on. If
  identity is an accumulated record, then editing the record *is* editing the person.

Two independent sources — a 1996 MUD and a 1949 novel — arriving at the same shape is
the strongest signal in this research folder.

### 2. CircleMUD bones, different organs

3rd Millennium kept the CircleMUD chassis (rooms, compass movement, the familiar prompt
rhythm) while gutting the progression system. That's our plan too: veterans should find
`n`, `s`, `look`, and the prompt exactly where their fingers expect them, and find
everything *behind* the prompt changed. Familiar shell, alien contents — which is
incidentally also the texture of life in a surveillance state.

### 3. A cautionary lesson, not just an inspirational one

3rd Millennium is dead, like most MUDs of its generation. Being well-designed in 1996
did not save it. The takeaways we act on:

- **Design for a small population.** A niche MUD's realistic steady state is a handful
  of concurrent players. Systems that need 50 people online to function (player-run
  economies, faction wars) will never function. Every core loop must work with 3 players
  online — or with zero, via NPCs and world simulation.
- **Small and dense beats large and empty.** An 8,000-room world with 4 players is a
  ghost town; a 150-room district where those same 4 players keep crossing paths feels
  alive. See [mud-design-landscape.md](mud-design-landscape.md).

## What we don't take

- The time-travel/Nexus lore — wrong genre for us.
- Any specific mechanic, because we can't see them. Where the prior drafts in
  [prior-drafts/](prior-drafts/) invented mechanics (Influence, Exposure, memory
  objects), those are original work that this research now grounds.

Sources: [MudStats — 3rd Millennium](https://www.mudstats.com/World/3rdMillennium),
[Top Mud Sites — 3rd Millennium](https://www.topmudsites.com/forums/muddisplay.php?mudid=3M)
