# Contributing

## Setup (Windows, matching the dev machine)

```powershell
cd C:\dev\2084
py -m venv .venv
.venv\Scripts\pip install evennia
cd game
..\.venv\Scripts\evennia migrate      # creates the SQLite db + superuser prompt
..\.venv\Scripts\evennia start
```

Connect: telnet `localhost 4000`, or the web client at `http://localhost:4001`.
Day-to-day: `evennia reload` applies code changes without dropping connections;
`evennia stop` when done. Tests: `evennia test --settings settings.py .` from `game/`.

The venv is pinned to Evennia 6.1.x ([ADR 0001](../decisions/0001-evennia-engine.md));
upgrading Evennia is a deliberate chore with its own commit, never a side effect.

## The rules that don't bend

1. **ADRs are immutable.** Changed your mind? Write a new ADR that supersedes the old
   one. The audit trail of our decisions works exactly like the game's record audit
   trail ([ADR 0005](../decisions/0005-records-are-objects.md)) — that's not a
   coincidence, it's the same value.
2. **Costs get written down.** Any trade-off's losing side goes on the page. An ADR
   with an empty "Bad" section hasn't finished thinking; a doc that only lists upsides
   is marketing.
3. **Research cites sources.** Claims about players, MUD history, or the novel trace to
   something checkable — a URL, the PDF, a named archive. Experience-based claims get
   marked as such (see [mud-design-landscape.md](../research/mud-design-landscape.md)'s
   confidence labels).
4. **Research drives principles; principles drive ADRs.** A feature argument that can't
   trace back through that chain isn't ready to be code.
5. **No class fields, ever** — including "just for now" ([ADR 0002](../decisions/0002-no-race-no-class.md)).
   Review rejects any `race`/`class`/`archetype` column, attribute, or chargen branch.
6. **Every new room passes the grid-consistency rule** ([ADR 0007](../decisions/0007-room-graph-grid-consistent.md)):
   compass exits with true reciprocals, sane 2D plan per level, non-compass exits as
   flagged exceptions. Sketch the district before writing batch code.
7. **Gameplay numbers live in `world/tuning.py`**, nowhere else.
8. **The world is code.** Rooms are built by batch files under `world/`, not by
   hand-`dig`ging on the live server. If it isn't in the repo, it doesn't exist.

## Workflow

- Branch per change; PRs even solo (the PR description is where "what changed and why"
  lives); main stays runnable.
- Prose docs follow the folder contract: findings → `research/`, position → `product/`,
  decision → `decisions/` (next number), how-it's-built → `engineering/`.
- Parking-lot discipline: a good idea that isn't scheduled goes to
  [future-features.md](../product/future-features.md) *with its reasoning*, in the same
  commit as the discussion that spawned it.
