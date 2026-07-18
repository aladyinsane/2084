# Evennia capabilities

Engineering research: what the engine gives us, what it makes cheap, what it makes
expensive. Verified against **Evennia 6.1.0** installed locally (the `another-world`
project on this machine runs it on Python 3.14 / Windows, so the stack is proven in this
exact environment). Primary source: [evennia.com docs](https://www.evennia.com/docs/latest/)
and the contrib READMEs shipped in the package.

## Core primitives, mapped to what 2084 needs

| Evennia primitive | What it is | What we use it for |
|---|---|---|
| **Typeclasses** | Django models with a Python class layer; subclass `DefaultRoom`, `DefaultCharacter`, `DefaultExit`, `DefaultScript` | `Room` with a visibility level, `Character` with exposure/skills/standing, `Exit` with exposure modifiers |
| **Attributes / AttributeProperty** | Arbitrary persisted per-object data, no schema migrations | All character state (exposure, skill dict, dossier). This is why classless is *cheap* here — no class tables to fight |
| **Tags** | Cheap many-to-many labels with categories | District membership, faction marks, "wanted" flags, unperson status. Fast bulk queries ("everyone tagged wanted in district X") |
| **Scripts** | Persistent objects with optional timers; global or attached | Exposure decay tick, Watch sweep sampling, scheduled world events (mechanism 8 in the 1984 research) |
| **CmdSets** | Command collections that merge/swap at runtime | The killer feature for us: **being detained is a cmdset swap**. Arrested characters lose movement commands and gain `confess`, `wait`, `demand`. States-as-commands instead of if-checks everywhere |
| **EvMenu** | Menu/state-machine system for multi-step interactions | Character creation, interrogations, and bureaucratic forms (filling in Form 27-B is naturally a menu tree) |
| **Channels / Msg** | Comms with persistence | Public (monitored!) channels vs. whispers — the monitored/unmonitored distinction is core theme material |
| **Locks** | String-defined access rules on any object/command | Access levels, clearance-gated exits, faction-gated doors |
| **Web client + Django site** | Browser client and admin out of the box | Zero-install playtesting; Django admin as a free "Ministry of Records" back-office for us |
| **Batch processors** | `.ev`/`.py` files that build the world reproducibly | The Grid gets rebuilt from versioned files, not hand-`dig`ging — world-as-code |

## The CircleMUD-feel checklist

The default command set already provides compass movement (`n/s/e/w/u/d`), `look`,
`get/drop`, `say/whisper`, `help` — the muscle-memory layer comes free. A configurable
prompt (`Vis:2 Exp:8 >`) is a small override. Nothing about the CircleMUD feel requires
fighting the engine.

## Mapping options (for the parked ASCII map feature)

All three shipped contribs inspected in `evennia/contrib/grid/` (6.1.0):

1. **`ingame_map_display`** (helpme, 2022) — generates an ASCII map *dynamically from
   the existing room/exit graph* and shows it via a `map` command. Needs no coordinates
   — only that exits use compass directions. **The cheap option**, and the likely v-later
   choice.
2. **`xyzgrid`** (Griatch, 2021) — places the whole world on an X/Y(/Z) coordinate grid
   defined by externally-parsed ASCII maps; adds fast shortest-path routing and a
   limited-radius map view. Powerful, but the world must live on the grid — adopting it
   late is a migration, not a toggle.
3. **`mapbuilder`** (Cloud_Keeper, 2016) — the reverse direction: draw an ASCII map,
   generate the rooms from it. A *building* tool, usable any time regardless of the
   display choice.

**The design consequence, needed *now*:** both display options assume compass-direction
exits and sane geometry. If builders freely create `enter portal`-style exits and
Escher rooms (two rooms both "north" of the same place), every mapping option degrades.
Keeping the world grid-consistent is a cheap discipline today that keeps all three doors
open — this becomes [ADR 0007](../decisions/0007-room-graph-grid-consistent.md).

Also relevant, same package: `extended_room` (time/season-varying descriptions, room
details — good for telescreen flavor), `slow_exit` (movement delay — pacing tool),
`simpledoor` (lockable doors), `cooldowns` (rate-limiting social actions),
`menu_login` (themed login flow — first-contact tone-setting), `turnbattle` (a base if
non-lethal confrontation ever needs turn structure), `crafting`, `clothing`.

## What Evennia makes expensive (honest costs)

- **The stack is heavy for a text game.** Django + Twisted, a database, two cooperating
  processes (portal + server). Fine on this machine (proven), but "compile telnet server
  in C" it is not; contributor onboarding includes Python tooling.
- **Single-process game logic.** Heavy per-tick simulation across thousands of objects
  is the anti-pattern; the engine wants event-driven design. Our surveillance model must
  be *sampling on events* (movement, actions, timed sweeps), never a per-second scan of
  every player. This constraint is baked into ADR 0004.
- **Attribute reads/writes hit the ORM.** Hot values (exposure) should be touched at
  event granularity, not in tight loops. Premature to optimize further; noted.
- **Smaller community than the DIKU lineage.** Fewer drop-in systems than 30 years of
  CircleMUD snippets; in exchange, the ones that exist are maintained and in Python.
- **Upgrade churn.** Evennia does make breaking major releases (5→6 changed contrib
  layouts). Pinning the version in the venv and vendoring nothing mitigates this.

## Alternatives considered (briefly)

- **CircleMUD/tbaMUD (C):** authentic feel, but 1990s C, world-as-binary-format, no
  tests, and every 2084 system (memory objects, dossiers, forms) would be built from
  telnet up. Authenticity of *feel* is achievable in Evennia; authenticity of *codebase*
  buys us nothing but pain.
- **Custom Python server:** we'd spend the first three months rebuilding login, persistence,
  and command parsing — the parts Evennia has already debugged for fifteen years.
- Full comparison and decision: [ADR 0001](../decisions/0001-evennia-engine.md).
