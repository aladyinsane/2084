# ADR 0002 — No races, no classes: a character is a record of actions

- **Status:** Accepted
- **Date:** 2026-07-17

## Context

Nearly every DIKU-lineage MUD gates characters by race and class at creation. Our named
inspiration, 3rd Millennium (1996), eliminated both — "the question of race and class
has been eliminated" ([third-millennium-mud.md](../research/third-millennium-mud.md)) —
and the source material independently demands it: the Party's hierarchy is functional
and revocable, not hereditary
([orwell-1984-source-material.md](../research/orwell-1984-source-material.md), M3).
The prior draft codex proposed six starting "roles" (Clerk, Technician, Courier…) —
classes wearing a trench coat.

## Decision

There is no race field and no class field, anywhere, ever — including chargen. A
character is:

1. **Skills** that improve through use (forgery gets better by forging);
2. **Standing** — ranks, clearances, work assignments — granted *and revoked* by
   institutions in play. If the regime stamps "Clerk, Records Section" in your dossier,
   that stamp is a data entry the fiction can change, not a build choice;
3. **A record** of what you've done, which the world reads and reacts to.

Character creation asks who you are (name, description, a few background touches that
seed the *dossier*, not stats) — never what you are. The prior codex's "Player Roles"
section is superseded by this ADR.

## Rationale

- Identity-as-record is the load-bearing beam: ADR 0005's memory mechanics only bite if
  editing the record edits the person. A class column is identity the regime *couldn't*
  edit — a hole in the fiction.
- Two independent sources (1996 MUD, 1949 novel) converged on this shape; that's the
  strongest signal in the research folder.
- Evennia makes it the *cheap* choice: skills and standing are Attributes; there's no
  class machinery to build because there's no class.

## Consequences

**Good**

- Fiction and mechanics agree everywhere. Promotion, demotion, and unpersoning need no
  special cases — they're edits to standing, which is just data.
- No content walled off by creation-screen choices a player made before understanding
  the game.

**Bad / accepted costs**

- **Convergence risk is real and documented** — classless veterans tend toward one best
  build ([mud-design-landscape.md §2](../research/mud-design-landscape.md)). Our
  mitigations (use-based advancement making breadth expensive; the world reacting to
  your record; institutional standing as the identity anchor) are *requirements*, and
  we've registered the failure signal in
  [future-features.md](../product/future-features.md#known-risks-in-shipped-features).
- **Balance is harder.** Classes are balance compartments; we've thrown the compartments
  away and accepted continuous tuning instead.
- **Blank-slate paralysis.** Classes tell a new player who they are; we must replace
  that orientation with the tutorial's work assignment (the regime *tells* you your
  function — onboarding as fiction).
- **No easy marketing shorthand.** "What classes do you have?" is the first question on
  a MUD listing; our answer is a paragraph. We accept the explanatory burden.

## Revisit when

Not revisable at the "add classes" level — too many downstream systems assume record-
based identity. Tunable at the level of how strongly standing templates behavior.
