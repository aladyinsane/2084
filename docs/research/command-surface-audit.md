# Command-surface audit (v0.7)

First-human-playtest finding #1: "all these custom commands are a bit
overwhelming — weigh the complexity against what players might be expecting
from a MUD." This is that weighing.

## The inventory (as of v0.7)

**Sanctioned — help category "the grid" (7):** `dossier` (aliases `score`,
`file`, `record`), `report`, `work`, `observe`, `listen`, `petition`, `apply`

**Unsanctioned — help category "the underground" (10):** `forge`, `circle`,
`signal`, `recruit`, `judge` (alias `sound`), `flip`, `sabotage`, `carry`,
`deliver`, `papers`

**Detention-only (3):** `confess`, `wait`, `demand` — these replace the whole
vocabulary, so they don't add to ambient load.

Plus all Evennia stock (`look`, `say`, `get`, `inventory`, `who`, `help`,
channels...).

## Against MUD expectations

Twenty custom verbs is mid-pack for the genre — Discworld or Achaea ship
hundreds. The overwhelm wasn't the count; it was that all seventeen ambient
verbs arrived **flat**: one help category, no gradient, several with names
that didn't say what they do. What a MUD veteran actually expects:

- `score` shows my character → **now aliased to `dossier`** (the muscle
  memory lands on the thematically correct answer).
- `kill <thing>` → absent by thesis (ADR 0006); `help the grid` now says so
  up front, so nobody spends an evening discovering it.
- Verbs to arrive in learnable layers → the split into "the grid" /
  "the underground" help categories mirrors how the game itself teaches
  them (Wing placards vs. Tunnel B chalk); a new player's `help` now shows
  a sanctioned starter set and a second category that is legible as
  "later."

## Folds considered and rejected

- **`carry`+`deliver` as one verb** — rejected: accepting a risk and
  completing it are different decisions, and the seizure mechanics live
  between them.
- **`papers` folded into `carry`** — rejected: the sink deserves its own
  discoverable name; hiding it makes the economy less legible, not more.
- **Dropping `flip`** — considered (it's the narrowest verb), retained: it
  is the observation grind's best payoff. Watch it; if nobody flips anyone
  by the next playtest gate, it folds into `recruit`.

## The rule going forward

New features must **ride existing verb patterns before minting new ones**:
the quest system (v0.9) should generalize `carry`/`deliver` rather than add
`quest accept`/`quest turn-in`; implants (v0.10) use stock `wear`/`remove`.
A new verb must displace a confusion, not add one. This is the command-surface
corollary of the feature rule "a new feature should say what it pushes out."
