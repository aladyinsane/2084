# The game theory of the Grid: making the trust machine hum

Follow-on research to [fun-and-game-feel.md](fun-and-game-feel.md), per
Lauren's ask for depth on game theory and mechanics. 2084's multiplayer
thesis (principle 6: betrayal outguns everything) is, formally, a **repeated
prisoner's dilemma with hidden roles and an institutional adversary** — a
structure the literature knows a great deal about. This doc audits our
mechanics against that literature and lists the gaps worth building toward.

## 1. What we already have, in formal terms

- **Section C is a textbook one-shot PD** — defect (name names) walks free
  and burns the cooperators; cooperate (confess alone) costs you and spares
  them. Correct and brutal. But [Axelrod's core result](https://ncase.me/trust/notes/)
  is that cooperation only becomes *rational* in **repeated** play with
  memory: known partners, visible histories, a future worth protecting.
- Our repetition machinery exists — circles persist, files persist — but a
  betrayer's history is only *discoverable* (gossip via `listen`, the
  "Section C complete" entry in their file), not ambient. In
  [Diplomacy studies](https://arxiv.org/pdf/1506.04744), betrayal's
  aftermath is public and reputational; in 2084 a Section C signer can walk
  into a new circle whose members never thought to read his file.
- **Hidden roles** ([Werewolf/Among Us tension](https://brain-games.com/en-us/blogs/board-game-explorer/game-theory-in-hidden-role-games)):
  our informants have hidden loyalty with a skill-gated reveal (`judge`) —
  structurally sound. What's missing is the *social deduction between
  players*: nothing currently lets a circle suspect which member leaked.

## 2. The gaps, as buildable mechanics (parking-lot candidates)

1. **Reputation must travel or defection dominates.** Cheap fix, high
   leverage: when someone with "Section C complete" in their file attempts
   `circle join`, the inviter (not the Ministry — the *street*) should get
   a chance to know: "word is, they sign things." Mechanic: `judge` works
   on citizens, not just informants, reading betrayal-shaped file entries
   at sufficient skill. Keeps it earned, keeps it diegetic.
2. **The shadow of the future needs length.** One-shot circles die after
   one betrayal payout. [Repeated-game theory](https://www.numberanalytics.com/blog/modern-look-prisoners-dilemma-game-theory)
   says cooperation stabilizes when continued membership is *worth more
   than one defection*. The stash starts this; escalating circle projects
   (joint errand chains with growing pots) would finish it — make the pot
   worth more tomorrow than Section C pays today, and watch players do the
   math the fiction wants them doing.
3. **Deniable defection is what makes hidden-role games sing.** Plants file
   reports with no fingerprints; an intercepted signal doesn't say whose
   room the wire was in. Good. Preserve this property in every future
   leak mechanic: [betrayal that can be *suspected but not proven*](https://analoggamestudies.org/2016/07/ruse-trust-and-the-fiction-of-betrayal-how-game-designers-can-author-player-experiences/)
   generates the conversations that make these games legendary; provable
   betrayal just generates kick-lists.
4. **Asymmetric stakes recruit the risk-averse.** Werewolf works because
   the timid still get to vote. Our shallow-end players need trust-game
   participation below circle-stakes: e.g., vouching (staking a little
   standing on another citizen's clearance application) — small, capped,
   recoverable — as the gateway drug to real conspiracy.

## 3. One warning from the same literature

[Zero-determinant strategy research](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4425415/)
shows extortionate strategies win one-on-one but die in populations —
translated: if we ever let a single mechanic reliably extract value from
cooperators (an unbeatable informant build, a risk-free betrayal loop),
the population stops cooperating *at all* and the multiplayer thesis dies
not with drama but with silence. Every trust mechanic should keep betrayal
**profitable once, costly as a career**. That's the design invariant this
doc exists to name.

## Sources

- https://ncase.me/trust/notes/ (Axelrod/Evolution of Trust)
- https://arxiv.org/pdf/1506.04744 (Linguistic Harbingers of Betrayal — Diplomacy)
- https://brain-games.com/en-us/blogs/board-game-explorer/game-theory-in-hidden-role-games
- https://analoggamestudies.org/2016/07/ruse-trust-and-the-fiction-of-betrayal-how-game-designers-can-author-player-experiences/
- https://www.numberanalytics.com/blog/modern-look-prisoners-dilemma-game-theory
- https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4425415/ (zero-determinant strategies)
