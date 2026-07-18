# MUD design landscape

What three decades of MUDs teach about what keeps a text game alive, and where 2084's
premise cuts with or against that grain. Sourcing note, honestly: parts of this are
community lore and designer experience (rec.games.mud.* archives, MudStats population
data, post-mortems) rather than citable studies. Claims here are marked by confidence.

## 1. The empty-world problem kills more MUDs than bad design does

**High confidence** — observable on any MUD listing site: hundreds of technically
functional games with 0–2 players connected ([MudStats](https://www.mudstats.com/) shows
this in a single scroll, our own inspiration among them).

A MUD's content is mostly *other people*. Below a critical population, every system that
depends on players interacting stops working, which drives away the remaining players.
Implications we build on:

- **Every core loop must be single-player-viable.** The state, its NPCs, and its
  scheduled events must generate pressure and story with one player online.
- **Small, dense geography.** Rooms should be added when the population supports them,
  not because builders enjoy building. A 150-room Grid that forces path-crossing beats
  8,000 rooms of silence. (Also the cheap-to-map choice — convenient.)
- **Asynchronous traces.** Players who never co-exist online should still affect each
  other: graffiti, rumors in NPC mouths, altered records, exposure consequences. A
  surveillance state is, conveniently, a machine for making absent people felt.

## 2. Classes vs. classless is an old, settled-enough debate

**Medium confidence.** The argument goes back to Usenet
([rec.games.mud.admin, "Classes vs Classless"](https://groups.google.com/g/rec.games.mud.admin/c/IiBTdx1JsX4)):
classes give instant identity, easy balance, and content gating; classless (skill-web)
systems give organic characters at the cost of balance work and "everyone converges on
the one best build" risk.

The known failure mode of classless systems is **convergence**: with no class walls and
one optimal strategy, every veteran character becomes the same character. The known
mitigations, which we adopt as design requirements rather than hopes:

- Skills advance by *use*, making breadth expensive in time;
- The world reacts to your record (a known forger is *watched differently* than a known
  clerk), so builds carry social consequences, not just stat consequences;
- Institutional standing — ranks, clearances, job assignments — is granted and revoked
  by factions, providing the identity anchor classes normally provide. Your "class" is
  what the regime currently says you are. This is where 2084's premise turns a known
  genre weakness into theme: see [third-millennium-mud.md](third-millennium-mud.md).

## 3. Progression is retention, and XP is only one shape of it

**High confidence.** Players stay when numbers they care about can go up (or meaningfully
down). Replacing XP is fine — *replacing it with nothing is fatal*. The replacement must
still be: visible, mostly monotonic early on, and player-attributable ("I did that").

2084's ledger: skills (up with use), standing/clearance (up and down, institutionally),
exposure (down is good — a rare and interesting inversion), and access as the spend.
The design risk to watch in playtests: exposure-driven loss aversion feeling like
punishment roulette. New players need a protected shallow end — which the fiction
provides for free, since nobodies aren't worth watching
([orwell-1984-source-material.md](orwell-1984-source-material.md), mechanism 2).

## 4. Permadeath and harsh loss: the lesson is consent

**Medium-high confidence.** Games with brutal stakes retain players only when the player
opted into the stakes and can see the risk coming. Uninvited catastrophic loss (rare in
successful MUDs, common in dead ones) reads as unfair even when mechanically "earned."

For 2084: detainment, memory edits, and unpersoning are our catastrophic outcomes. They
must telegraph — rising exposure should be *felt* (prompt, NPC behavior, patrol density)
before it lands. The novel's dread comes from uncertainty about *when*, not *whether*;
we copy that: consequences are certain-ish and visible in trend, random only in timing.

## 5. Roleplay enforcement is a spectrum, and machinery beats moderation

**Medium confidence.** RP-required MUDs produce the deepest dystopian experiences (the
genre's standouts are RP-enforced) but demand staff the project doesn't have. RP-optional
MUDs scale down to zero staff but the tone erodes.

Our position: encode the tone in *mechanics* rather than moderation wherever possible.
If saying reckless things on a monitored channel mechanically raises exposure, the game
polices tone without a human on duty. Mechanics are the staff that never logs off.

## What this folder adds up to

The research stack ends here. Findings from this doc + the 1984 mechanisms + 3rd
Millennium's precedent + Evennia's constraints produce the principles in
[../product/principles.md](../product/principles.md); the principles produce the ADRs.
When a later argument breaks out, trace it back this far before re-litigating.
