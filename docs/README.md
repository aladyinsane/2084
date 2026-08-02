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
| [mobile-web-client.md](research/mobile-web-client.md) | Why the stock GoldenLayout web client can't just get responsive CSS, and the phased plan for a purpose-built mobile client on the same protocol |
| [solo-player-fun-audit.md](research/solo-player-fun-audit.md) | Solo play passes principle 8 structurally, but repeatable content hasn't grown since v0.6 — and one ten-persona playtest finding never made it into the parking lot at all |
| [endgame-and-long-term-goals.md](research/endgame-and-long-term-goals.md) | What a citizen plays *toward*: three non-exclusive long-horizon peaks (co-option, doublethink, durable underground legacy), none a "you win" cutscene — principle 8 rules that out structurally |
| [opposed-checks-for-existing-verbs.md](research/opposed-checks-for-existing-verbs.md) | D&D-style dice resolution for existing verbs like `observe`: what's already random (more than you'd think), what's genuinely missing (obstacle-driven difficulty), and why it isn't the parked combat-sparring idea in a trench coat |
| [playtest-2026-08-01-long-term-retention.md](research/playtest-2026-08-01-long-term-retention.md) | Same ten personas, a "years of play" lens instead of first-hour onboarding: the sabotage grind's target pool is nearly empty, couriering is a risk-free strictly-better alternative, and two of the three visible progressions (shadow ladder, Grade) hard-cap with nothing behind them |
| [outside-the-grid-principle-9-pass.md](research/outside-the-grid-principle-9-pass.md) | The ADR 0020-required principle-9 audit of "the world outside the Grid": Evennia hands us no CircleMUD-style stock zones, so the real magic-missile risk is authored genre-bleed (farming-sim verbs, pastoral NPCs); principle 1 is a real risk unless the area's spine is record-vs-truth on land/water, not a farming minigame; and it's the same idea as the Perimeter sketch at a different altitude, not a separate area |
| [upper-spire-design-pass.md](research/upper-spire-design-pass.md) | The ADR 0020 in-Grid district design pass: the Spire already exists up to a dead-end C-1 lobby with "ascent by appointment" already written, clearance above C-1 doesn't exist in code yet, and elevation reuses Exposure rather than earning a second stat |
| [outside-the-grid-design-pass.md](research/outside-the-grid-design-pass.md) | The follow-up design pass once Lauren confirmed a playable area with a record-vs-truth spine: `records.py`'s generic `subject` parameter turns out to make land/water records almost free to build, entry gates on shadow standing rather than Clearance (the inverse of the Spire), and the pressure valve is NPC texture, not a place |
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
| [0008](decisions/0008-grind-loops-sabotage-and-couriering.md) | The grind is sabotage and couriering, paid by the underground | The bestiary is the apparatus — a mob-grind's shape without a corpse |
| [0009](decisions/0009-shadow-ladder-is-a-checkable-whisper.md) | The shadow ladder is a checkable whisper, not a file | Zero new persistent state — the tier is a pure function of a number the game already tracks |
| [0010](decisions/0010-reputation-travels-judge-reads-citizens.md) | Reputation travels — `judge` reads a citizen's Section C | The first mechanic that lets one player surveil another's actual file, not just an NPC's |
| [0011](decisions/0011-old-incidents-compact-the-file-forgets-faster-than-the-truth-does.md) | Old incidents compact; the file forgets faster than the truth does | The count never shrinks; the event-level detail inside a compacted bucket does, once |
| [0012](decisions/0012-world-building-tooling-incremental-areas.md) | Building new areas without rebuilding the old ones | Option 1 of three candidates chosen: per-district idempotent functions, not a new contrib dependency |
| [0013](decisions/0013-escalating-circle-projects.md) | Escalating circle projects: a growing pot only finishing pays out | Mostly-solo-climax-synchronous chosen over a fully synchronous heist, to keep principle 8's solo-viability test honest |
| [0014](decisions/0014-vouching.md) | Vouching: a small, sanctioned stake on someone else's name | Hybrid chosen over a literal C-1-only reading, so the mechanic actually reaches the new/risk-averse players it was named for |
| [0015](decisions/0015-suspected-not-proven-circumstantial-informant-clues.md) | Suspected, not proven: circumstantial informant clues | Deniability already held before this ADR — the real gap was that the message had nothing circumstantial in it to reason about |
| [0016](decisions/0016-records-archaeology.md) | Records archaeology: a third grind loop, at the Annex | Atomic fragment sentences instead of grammatical recombination — infinite without the Mad-Libs agreement bugs |
| [0017](decisions/0017-propaganda-engine.md) | The propaganda engine: giving the alert system a voice | District alert already drives patrol density silently — this narrates a mechanic that was already real, rather than inventing a new one |
| [0018](decisions/0018-orientation-wing-interactive-and-sector-wide.md) | The Orientation Wing becomes genuinely interactive, and teaching starts reaching past it | Resolves the tension with v0.15's own "never gate, nobody's worse for skipping" design explicitly rather than silently overriding it |
| [0019](decisions/0019-opposed-checks-for-observe-forge-and-sabotage.md) | Opposed checks: `observe`, `forge`, and `sabotage` roll against an obstacle, not a flat constant | A shared `opposed_check()` replaces three independent formulas, each obstacle now driven by state the game already tracks (exposure, district alert, sensor sensitivity) instead of a tuning constant blind to it |
| [0020](decisions/0020-world-expansion-gated-by-progression.md) | Growing the world before launch: a new district, the world outside the Grid, gated by progression | A one-time pre-launch completeness exception to anti-principle 4, not a reversal — new geography stays gated behind earned progression so principle 8's density holds even as the footprint grows |

## Product

| Doc | What's in it |
|---|---|
| [overview.md](product/overview.md) | High-level summary of what 2084 is, creative position, and how players interact with the world |
| [principles.md](product/principles.md) | Ten principles, each traced to research, each with a test — plus what we're deliberately *not* |
| [roadmap.md](product/roadmap.md) | v0.1–v0.22, sequenced by what proves the thesis: *a surveillance state beats a bestiary* |
| [future-features.md](product/future-features.md) | The parking lot — headlined by the ASCII map — and the known risks we shipped on purpose |
| [worldbuilding-ideas.md](product/worldbuilding-ideas.md) | Worldbuilding concepts and narrative backlog feeding future gameplay features into lore |
| [game-theory-and-fun.md](product/game-theory-and-fun.md) | Informal gamification audit (not run through the ADR pipeline) — its proposals are triaged into [future-features.md](product/future-features.md) |

## Lore

| Doc | What's in it |
|---|---|
| [lore/README.md](lore/README.md) | Lore directory index, Lore Maintenance Protocol, and In-Universe Artifact Registry |
| [lore/historical-background.md](lore/historical-background.md) | The narrative history of Sector 9, the Three Ministries, the Spire, the Civic Machine, and the Underground |
| [lore/artifacts/forms-and-notices.md](lore/artifacts/forms-and-notices.md) | In-universe documentation of state forms (Form 1-A, Form 2-B, Form 9-A, Form 12-D, Form C-1, Form 77, Section C) |
| [lore/artifacts/the-chalk-marks.md](lore/artifacts/the-chalk-marks.md) | Complete transcript and textual analysis of the subterranean Tunnel B chalk curriculum |
| [lore/artifacts/apparatus-and-requisitions.md](lore/artifacts/apparatus-and-requisitions.md) | In-universe catalogue of state surveillance equipment and state issue vs. black-market gear |

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
