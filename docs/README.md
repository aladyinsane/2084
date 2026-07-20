# 2084 Documentation

A dystopian text MUD, loosely based on *Nineteen Eighty-Four*, built on Evennia. The
development process lives here: what we learned, what we decided, why, and what we
deliberately said no to. Research drives principles; principles drive ADRs.

## Start here

**[research/orwell-1984-source-material.md](research/orwell-1984-source-material.md)** —
the most important document in the repo. It converts the novel's control mechanisms
(numbered M1–M9, cited everywhere else) into design constraints, and states our one
deliberate infidelity to the source.

Then **[product/principles.md](product/principles.md)** — the ten principles those
mechanisms produced. They exist to be used in arguments, and each one has a test.

## Research

| Doc | What's in it |
|---|---|
| [orwell-1984-source-material.md](research/orwell-1984-source-material.md) | The novel's control mechanisms as design constraints — and the "loosely based" legal position |
| [third-millennium-mud.md](research/third-millennium-mud.md) | The 1996 MUD that eliminated race and class; what we take (the principle), what we honestly can't (the details), and its cautionary second lesson |
| [evennia-capabilities.md](research/evennia-capabilities.md) | What the engine makes cheap and expensive, verified against 6.1.0 locally — including the three ASCII-mapping doors |
| [mud-design-landscape.md](research/mud-design-landscape.md) | Why MUDs die (empty worlds), the classless-convergence failure mode, progression-as-retention, consent-to-stakes — with confidence labels |
| [grind-loops-without-killing.md](research/grind-loops-without-killing.md) | What grinding is *for* psychologically, and five ways to keep its shape with the Grid's own materials — the shelf ADR 0008 shopped from |
| [playtest-2026-07-19-first-human.md](research/playtest-2026-07-19-first-human.md) | The first human playtest: mechanically safe, experientially rough — the confusion taxes and the "a bit dull" verdict that spawned v0.7–v0.11 |
| [command-surface-audit.md](research/command-surface-audit.md) | The command-overwhelm audit: organization, not amputation — and the standing rule that new features ride existing verb patterns |
| [fun-and-game-feel.md](research/fun-and-game-feel.md) | Five named dullnesses, each assigned a fix — near-misses, the login digest, ambience, risk stated up front, the want-ladder |
| [game-theory-of-the-grid.md](research/game-theory-of-the-grid.md) | The trust machine audited against the repeated-PD literature, and the invariant every betrayal mechanic must keep: profitable once, costly as a career |
| [the-first-hour.md](research/the-first-hour.md) | Onboarding and learning-curve research: the ladder we have but don't show, progressive disclosure, and why familiar combat isn't the fix — the v0.12/v0.13 rationale |
| [playtest-2026-07-20-ten-personas.md](research/playtest-2026-07-20-ten-personas.md) | Ten play styles in one evening: the hostile command suggester, the deaf world, the missing shadow ladder — and what held (the ladder, the circle flow, `next`) |
| [prior-drafts/](research/prior-drafts/README.md) | Pre-workflow design material (codex, mechanics draft, brainstorm), frozen; ADRs beat anything in there |
| [sources/](research/sources/) | The novel itself |

## Decisions (ADRs)

Numbered, immutable once accepted, superseded rather than edited. Every one has a real
**Consequences** section — an ADR with no downsides listed hasn't finished thinking.

| ADR | Decision | The interesting part |
|---|---|---|
| [0001](decisions/0001-evennia-engine.md) | Build on Evennia | CmdSets alone justify it: detainment is a command-set swap, not an if-statement |
| [0002](decisions/0002-no-race-no-class.md) | No races, no classes — a character is a record | The regime must be able to edit who you are; a class column would be identity it couldn't touch |
| [0003](decisions/0003-exposure-influence-not-xp.md) | Exposure + Influence replace XP | The rare inversion: the number you watch most is best when it goes *down* |
| [0004](decisions/0004-surveillance-is-event-driven.md) | Surveillance is event-driven, never omniscient | An engine constraint and the telescreen's intermittency demanded the same design |
| [0005](decisions/0005-records-are-objects.md) | Records are objects; the record ≠ the truth | Editable records over an append-only audit trail — forgery gameplay needs somewhere truth still lives |
| [0006](decisions/0006-conflict-is-non-lethal.md) | No death, no lethal PvP | Not a softening: what the regime does instead is scarier, and social ruin out-griefs ganking (that cost is faced) |
| [0007](decisions/0007-room-graph-grid-consistent.md) | Hand-built room graph, grid-consistent | The map feature is deferred; the *mappability* decision couldn't be |

## Product

| Doc | What's in it |
|---|---|
| [principles.md](product/principles.md) | Ten principles, each traced to research, each with a test — plus what we're deliberately *not* |
| [roadmap.md](product/roadmap.md) | v0.1–v0.13, sequenced by what proves the thesis: *a surveillance state beats a bestiary* |
| [future-features.md](product/future-features.md) | The parking lot — headlined by the ASCII map (three Evennia doors analyzed, one kept open by ADR 0007) — and the known risks we shipped on purpose |

## Engineering

| Doc | What's in it |
|---|---|
| [architecture.md](engineering/architecture.md) | Where every system lives, the data-model conventions, why all tuning numbers share one file |
| [contributing.md](engineering/contributing.md) | Setup on Windows, and the rules that don't bend |

## Conventions

- **ADRs are immutable.** Supersede, don't edit — the same append-only discipline the
  game applies to its own records, for the same reason.
- **Research cites sources**; experience-based claims are labeled as such.
- **Costs get written down.** Anywhere we chose a trade-off, the thing we gave up is on
  the page. A doc that only lists upsides is marketing.
