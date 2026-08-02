# Design pass: the Upper Spire

The "new in-Grid district" half of [ADR 0020](../decisions/0020-world-expansion-gated-by-progression.md).
`future-features.md`'s entry for it says a dedicated design pass has to happen
before any `build.py` work starts — this is that pass. Same posture as every
other research doc here: it proposes a concrete shape and names the real open
questions, it does not decide anything, and nothing in it is prose meant to
ship. Lauren picked "the Upper Spire" from `worldbuilding-ideas.md`'s existing
sketch (item 1, "The Upper Spire (Clearance C-2 through C-5)") over the
Perimeter/outside-the-Grid option, which is being left for after that other
research pass lands ([PR #70](../research/outside-the-grid-principle-9-pass.md)).

## This isn't a blank page — the Spire already exists up to its front door

This is the single most important thing this pass found, and it changes the
shape of the work a lot: **the Spire isn't a new location, it's an unfinished
one.** `game/world/build.py` already builds the Central Spire Checkpoint and
the Central Spire Lobby, gated at `clearance(1)` — the *first* clearance-locked
exit in the whole game (`build.py:400-404`). The lobby's own shipped
description already sets up exactly what this pass would build next:

> "Elevator banks line the far wall, each door stencilled with a number and a
> floor and, in two cases, nothing at all... ASCENT BY APPOINTMENT."

And `map.py`'s help text, also already shipped: *"Places beyond your clearance
are not on it, because as far as you are concerned they are not anywhere,"*
and *"the Grid above your clearance is rumor."* Nobody wrote this for the
Upper Spire specifically — it was written for the lobby as a dead end, a nod
at scale the player was never meant to reach. It turns out to be a
near-perfect setup for this district, unintentionally. This pass leans on that
rather than inventing new framing.

Confirmed by reading the code directly: `spire_lobby` has exactly one exit
today (the gate in from the checkpoint). Nothing north, up, or otherwise leads
out of it. And clearance itself only goes to C-1 anywhere in the codebase —
`world/functions.py`'s `adjudicate_c1`/`grant_c1` and `world/form_c1.py` are
the only clearance-granting code that exists; `world/tuning.py` even already
carries the thematic seed for going further: `CLEARANCE_GRANT_EXPOSURE = 10
# elevation means scrutiny (M2)` — a tuning constant that's already citing the
exact Orwell mechanism (M2, surveillance concentrates around proximity to
power) this district exists to dramatize, written before this district was
ever discussed.

## Geometry: up, not sideways

ADR 0007 requires grid-consistent geometry, and the `map` command (built on
the `ingame_map_display` contrib) already natively renders vertical shafts —
`[0^` for a way up, `v1]` for a way down (`commands/map.py`'s `GridMap`). That
tooling has never been used yet (no room in the game currently has an `up` or
`down` exit — the honeypot's `down` into Tunnel B is the only vertical
movement that exists, and it's `down`, not `up`). The Upper Spire would be the
first `up` geometry in the game, and the elevator-bank framing already in the
lobby's text makes `up` read as an elevator ride rather than a staircase,
which fits "ASCENT BY APPOINTMENT" literally.

Proposed shape, not final: each floor is a single `up` exit from the one
below it (`spire_lobby` → floor C-2 → floor C-3 → ...), each gated the same
way the lobby's own entrance already is —
`exit.locks.add("traverse:clearance(N)")`, reusing the exact idiom instead of
inventing a new one. A citizen without the floor's clearance doesn't see the
exit at all on `map` (per the contrib's existing traverse-check behavior,
already proven for the lobby itself), so the elevator bank's "two doors with
nothing stencilled on them" line is *already* accurate today, before a single
room gets built — a nice accident worth keeping.

## Getting past C-1: the open mechanical question

Nothing today grants clearance above C-1. The natural extension is a Form
C-2 mirroring the existing Form C-1 flow almost exactly
(`functions.py:122-162`): `adjudicate_c1` reads the record layer (visible
incidents against a threshold, vouching offsets it per ADR 0014, a Function
required on file), `grant_c1` writes the standing and taxes it with
`CLEARANCE_GRANT_EXPOSURE`. A `adjudicate_c2`/`grant_c2` pair could reuse that
shape with a tighter threshold and a bigger Exposure tax — mechanically cheap,
thematically consistent (the record, not the truth, is still what's being
judged, per ADR 0005).

But a straight escalation of the same form risks making C-2 feel like "C-1
again, but harder," which undersells what floor two of the Spire is supposed
to *be*. Worth naming as a real fork rather than deciding it here:

- **Escalating paperwork** (Form C-2, stricter version of Form C-1): cheapest
  to build, mechanically proven, but risks reading as a bigger number rather
  than a different kind of access.
- **Sponsorship**, not application: an existing C-2+ citizen (NPC or, later,
  player) vouches you up a floor, the way ADR 0014's vouching already exists
  for incident tolerance but repurposed as the actual gate itself rather than
  a modifier on one. This would give principle 6 (trust is the scarcest
  currency) real teeth in this district specifically — elevation becomes
  something someone else can grant or withhold, which is more interesting
  than a form, and sets up betrayal stakes (a sponsor who turns out to be
  testing you, a rescinded sponsorship) that a form can't.
- **Function-gated only**: certain Functions (assigned at the Assignment Hall)
  simply come with clearance attached, no separate application at all — you
  don't apply to see the Spire's upper floors, you're posted there. Simplest
  of the three, but removes player agency from the gate entirely, which cuts
  against how every other progression system in the game works (skills by
  use, standing by paperwork you choose to file).

This pass's read: sponsorship is the most interesting and most 2084-flavored
of the three, but it's also the most new mechanical surface to build. Worth
Lauren's actual call rather than picking unilaterally, the same way the
opposed-checks ADR's shape got decided by a real options question instead of
a default.

## What makes elevation *feel* like elevation: reusing Exposure, not inventing a second stat

`worldbuilding-ideas.md`'s existing sketch already names the mechanical
texture: "exposure accrues from small breaches in elite etiquette rather than
dirty clothes." The cleanest reading of that, and the one this pass
recommends as the default: **this is the same Exposure stat the whole game
already uses, with different fictional triggers** — not a second, parallel
"etiquette" meter. The game already has one register for "the state is
watching and judging you," and principle 9's discipline (every default
message passes through the fiction, engine mechanics don't multiply per
district) argues against giving the Spire its own bespoke stakes system when
the existing one already does the job. What changes is *what raises it*:
using an unmarked door, addressing an NPC out of the correct order, idling
somewhere idling isn't done, being seen without an appointment on the floor
you're on. Same number, same prompt, same Watch-sweep mechanism underneath —
only the *fiction* of what trips it changes, which is exactly what principle
9 asks for and exactly what "reuse the machinery, change the trigger" already
worked for the land-record hook the outside-the-Grid pass found.

Flagging this as a judgment call this pass is making, not something it's
entitled to decide alone: if Lauren wants the Spire to feel mechanically
distinct from street-level Sector 9, not just re-skinned, that's a bigger
design commitment (a genuinely new stat, new UI, new sweep logic) and worth
saying now rather than discovering after the reused-Exposure version ships
and feels thin.

## Principle checks

- **Principle 1 (the world is the antagonist).** Strong fit, arguably the
  cleanest of any district — this is the antagonist's own interior, not
  another place it operates. Confirmed by the M2 tuning comment already
  sitting in the codebase months before this conversation happened.
- **Principle 2 / M2 (you are what you do; scrutiny follows power).** This is
  the district that finally gives clearance a *place*, not just a lockfunc
  value. Right now C-1 only ever manifests as a line in `dossier` and one
  gated exit; the Spire is the first time "holding elevated clearance" is
  something a player *experiences* rather than reads about.
- **Principle 8 / anti-principle 4 (density, gating).** This is exactly the
  mechanism ADR 0020 promised: only players who've earned clearance reach any
  of this, so newcomers stay dense at street level in Sector 9 regardless of
  how many floors eventually exist above the lobby. The elevator-shaft
  geometry makes this literal — you cannot wander in by accident, there's
  nothing to stumble onto without the gate opening for you first.
- **Principle 9 (alien contents all the way down) — a real risk, worth
  naming.** Elite-bureaucracy-with-secrets is exactly the territory where a
  first draft could reach for corporate-thriller or spy-genre furniture
  instead of Ministry banality — keycards read as generic-thriller if the
  prose leans on "clearance" as a technothriller access-badge concept rather
  than the same paperwork-and-forms register the rest of the game already
  established (Form C-1's "application conforms to schedule" is the right
  voice; a floor described with biometric scanners and laser grids would not
  be). The existing lobby prose ("Ascent by appointment," the reception
  pillar's slogan) already sets the right register — matching it, not
  upgrading it to spy-movie tech, is the actual bar for whatever gets built
  next.
- **Principle 10 (oppression is the fiction, not the UX).** "Comfort as
  horror" needs its own pressure valve the same way the outside-the-Grid pass
  found for that area — inheriting Sector 9's pub doesn't reach a player who's
  spent real effort climbing to C-2+. Candidate texture, not decided here:
  petty status games and rivalries among mid-tier clerks, gallows humor
  specific to people who know exactly how replaceable they are because
  they're close enough to see it happen to others. Worth its own answer,
  not assumed solved by proximity to the rest of the game's existing warmth.

## Scope: how much to build now

Given how "thin tutorial rooms" landed well in the Orientation Wing (ADR
0018) and the same instinct underlies ADR 0020's caution about over-committing
before real human population exists — this pass recommends building **one
floor (C-2) fully, and stubbing nothing above it** rather than committing to
all four floors (C-2 through C-5) up front. `worldbuilding-ideas.md`'s "C-2
through C-5" framing was a scale gesture, not a build order; one real floor
proves the geometry, the clearance-grant mechanism, and the etiquette-Exposure
texture before more effort goes in. C-3 through C-5 stay in the parking lot's
back pocket, same shape as this pass, until the first floor's actually been
played.

## Open questions for Lauren

1. **How is clearance above C-1 actually granted** — escalating Form C-2,
   NPC/player sponsorship, or Function-gated by default? This pass's lean is
   sponsorship (best principle-6 payoff), but it's the biggest new mechanical
   surface of the three and deserves a real decision, not a default.
2. **Does elevation reuse Exposure as-is (different triggers, same stat) or
   earn its own mechanical register?** This pass defaults to reuse, per
   principle 9's discipline against multiplying systems — flagging it rather
   than assuming it, since "the Spire should feel different" is a reasonable
   instinct that cuts the other way.
3. **Scope for this pass:** one floor (C-2) now, C-3 through C-5 deferred —
   agree, or is there a reason to commit further up front?
4. **This district's principle-10 pressure valve** — what it actually is
   (an NPC, a room, a recurring bit of texture) is genuinely undesigned;
   this pass only established that it's needed.

Once these are answered, the natural next step is the same shape as every
other feature here: an ADR that picks the specific mechanism (clearance
grant, Exposure reuse), then implementation against ADR 0012's now-idempotent
`build()` pattern.
