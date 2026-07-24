# Game Theory & Gamification Audit: Making 2084 Thrilling

This document performs a comprehensive game-theoretic audit of *2084*, addressing two core player retention risks:
1. **The "Fun / Pull" Risk**: Will players find surviving in a surveillance state engaging, or will the optimal strategy ("be nobody / lie low") feel tedious?
2. **The Cognitive Load Risk**: Will new players feel overwhelmed by novel commands, administrative forms, and text-MUD abstractions?

---

## 1. Game-Theoretic Diagnosis

From a game theory perspective, **fun is defined as a series of meaningful, strategic decisions under uncertainty with clear feedback and escalating stakes**.

### Risk A: The Inaction Trap (Dominant Strategy = Boredom)
In survival games, if the safest strategy is doing nothing ("lying low in a dead zone"), players naturally optimize toward zero action. When zero-input is optimal, engagement collapses.

* **Current Reality**: Stepping into Tunnel B decays Exposure. Walking into Unity Plaza raises Exposure. If Exposure only brings punishment, players are incentivized to avoid monitored space unless forced by an assembly.
* **Game Theory Solution**: **Push-Your-Luck Dynamics & High-Risk/High-Yield Asymmetry**. Monitored space must contain high-yield rewards that scale with risk. Staying in watched space should feel like a high-wire act where players voluntarily push their luck for greater payoffs.

### Risk B: Command Overwhelm & Cognitive Friction
Text MUDs force the brain to parse syntax before strategy. If a player is struggling to remember command syntax (`form_c1`, `petition`, `signal`, `stash`, `word`), they have zero mental bandwidth to think strategically about exposure, surveillance, or trust.

* **Game Theory Solution**: **Syntax Abstraction & Contextual Prompts**. Reduce syntax friction so cognitive effort is spent on *strategic choices* (Who do I trust? Do I risk one more delivery? Do I defect in Section C?), not on *syntax lookup*.

### Risk C: The Prisoner's Dilemma Equilibrium in Multiplayer
In repeated prisoner's dilemmas (RPDs), cooperation between players only stabilizes if the **Shadow of the Future** is large enough—meaning the expected long-term value of teamwork ($V_{\text{cooperate}}$) exceeds the immediate one-time payout of betrayal ($V_{\text{defect}}$).

* **Current Reality**: Section C confessions pay immediate freedom upon defecting (`confess names`). Circles currently pool risk more than they pool game-changing power.
* **Game Theory Solution**: **Escalating Joint Projects & Paranoia Engines**. Circle activities must yield exponentially higher rewards than single-player play, while betrayal mechanics must generate *suspected but unproven tension* rather than instant kick-lists.

---

## 2. Five Core Gamification Proposals

To make *2084* deeply addictive while preserving its atmospheric, dystopian identity, we propose five concrete mechanics:

```
+--------------------------------------------------------------------------+
|                        2084 GAMIFICATION ENGINE                          |
+--------------------------------------------------------------------------+
|  1. PUSH-YOUR-LUCK HEAT MULTIPLIERS (High Risk -> High Payoff)            |
|  2. ESCALATING CIRCLE HEISTS (Teamwork Payoff > Betrayal Payoff)         |
|  3. THE PARANOIA ENGINE (Suspected-Deniable Leaks & Clues)              |
|  4. CONTEXTUAL ACTION MENU & VERB HARMONIZATION (Zero Syntax Friction)   |
|  5. TANGIBLE MINIGAME MECHANICS (Timing & Sequence Skill vs Pure RNG)    |
+--------------------------------------------------------------------------+
```

### Proposal 1: Push-Your-Luck Heat Multipliers ("The High-Wire Streak")
* **The Mechanic**: Performing consecutive sanctioned or unsanctioned actions in watched space (Vis 3–5) builds a **Streak Multiplier** ($1.2\times \to 2.5\times$ standing, credits, or underground reputation).
* **The Catch**: Each tier of the multiplier doubles Exposure accrual and increases Watch sweep sampling odds. Stepping into a Vis 0 dead zone resets the multiplier.
* **Game Theory Impact**: Creates a classic "Press Your Luck" tension (like Blackjack or *Risk of Rain*). Players constantly ask themselves: *"Do I push for one more 2.0x shift/delivery while hot, or cash out and go dark?"* Lying low becomes a deliberate strategic recovery phase rather than boring idle time.

### Proposal 2: Escalating Circle Heists & Projects
* **The Mechanic**: Multi-stage subterranean operations requiring 2+ circle members standing in specific locations:
  * **Stage 1 (Preparation)**: Sabotage 2 specific watchscreens within a 3-minute window.
  * **Stage 2 (Execution)**: Intercept a patrol route at Unity Plaza while a comrade accesses the Archive Annex.
  * **Stage 3 (Payoff)**: Clean entire dossier histories or unlock high-tier black market gear.
* **Game Theory Impact**: Solves $V_{\text{cooperate}} > V_{\text{defect}}$. The payoff of completing a joint operation is exponentially higher than Section C's individual betrayal payout. Betrayal remains possible at every stage, escalating paranoia to thrilling levels right before the final score.

### Proposal 3: The Paranoia Engine (Deniable Clues)
* **The Mechanic**: When a plant leaks or a circle member confesses, the game never prints a clean system message identifying the betrayer. Instead, it generates **diegetic clues**:
  * *"The Watch checkpoint knew your exact delivery destination before you arrived."*
  * *"A recent incident entry at Records references a detail discussed in Tunnel B."*
* **Game Theory Impact**: Turns hidden-role betrayal into an active social deduction puzzle (*Among Us*, *Diplomacy*). Players compare itineraries, audit each other's dossiers with `judge`, and attempt to sniff out leaks without false accusations.

### Proposal 4: Contextual Verb Surface & Action Prompts
* **The Mechanic**: Eliminate syntax friction by expanding command aliases and adding dynamic action suggestions:
  * **Contextual Prompts**: Rooms and prompts dynamically list valid actions: `[G5 Vis:3 Exp:12] (Actions available: report, work, list, errands)`.
  * **Verb Harmonization**: Allow universal verbs (`use`, `interact`, `talk`) to route cleanly:
    * `interact clerk` $\to$ opens an in-fiction menu listing `1. Report`, `2. Errands`, `3. Requisitions`.
    * `use coat` / `use badge` $\to$ maps directly to `wear`.
* **UX Impact**: New players can immediately play using standard MUD verbs without feeling lost in administrative syntax.

### Proposal 5: Skill-Based Action Mini-Loops (Timing & Sequence over Pure RNG)
* **The Mechanic**: Replace flat probability checks (`sabotage`, `forge`) with interactive timing/sequence mini-mechanics:
  * **Forgery Sequence**: To `forge` a dossier entry, the player must balance three parameters (Ink / Date / Stamp) in sequence within a short time window.
  * **Sabotage Timing**: `sabotage` prompts a short scanning rhythm where pressing command at the right interval guarantees clean execution without raising alert.
* **Game Theory Impact**: Gives players a sense of personal mastery. Success feels earned through player skill rather than a background dice roll.

---

## 3. Implementation Sequencing Roadmap

| Phase | Target Version | Focus | Core Deliverable |
|---|---|---|---|
| **Phase 1** | **v0.15** | Contextual Action Surface | Dynamic prompt action hints + `interact` menu verb to eliminate syntax friction |
| **Phase 2** | **v0.16** | Push-Your-Luck Economy | Streak Multipliers for consecutive watched-space actions |
| **Phase 3** | **v0.17** | Paranoia Clue System | Diegetic leak signals and enhanced citizen `judge` audit trails |
| **Phase 4** | **v0.18** | Circle Heists / Projects | Multi-stage joint operations with massive subterranean payouts |
