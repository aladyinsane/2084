# ADR 0015 — Suspected, not proven: circumstantial informant clues

- **Status:** Proposed
- **Date:** 2026-07-26

## Context

[game-theory-of-the-grid.md](../research/game-theory-of-the-grid.md) names the
trust-machine backlog's third gap: "betrayal that can be suspected but not proven
generates the conversations that make these games legendary; provable betrayal just
generates kick-lists." The doc frames this as a property to *preserve* in every future
leak mechanic, citing plant reports with no fingerprints and interceptions that don't
name a room as the examples already in hand.

Auditing what's actually shipped against that framing: the property already holds
structurally. `circles.collect_informant_reports()` never names the informant or the
room; `circles.send_signal()`'s interception message never names the room either. What's
missing isn't deniability — it's *texture*. Both messages are static flavor text with
nothing circumstantial in them, which means there's nothing for a circle to actually
reason about when one arrives. "Reported by a source" every time, regardless of what the
circle has actually been doing, gives players a shrug, not a mystery.

Two shapes were sketched and presented to Lauren:

1. **Sharpen the existing deniable clues.** Extend the informant-report message to
   reference a real circumstantial detail drawn from the circle's own recent activity —
   something to compare notes over — without ever naming a member or an informant.
   Small, extends `circles.py`/`circle_projects.py` as they already exist, no new
   hidden-role concept.
2. **The mole: a player can be turned.** A new Section C option lets a detained citizen
   stay in their circle but start reporting on it from the inside, deniable the same way
   an NPC plant is. This is the literal "hidden role among players" the research doc's
   diagnosis section names as the one structural piece missing (informants have hidden
   loyalty; player circle-mates don't). Real payoff, real scope: needs its own
   telegraphing, its own detection tools, and a harder fairness question — a circle-mate
   secretly working against you touches principle 9 in a way NPC informants don't, since
   the informants are recruited by choice and the "who's the mole" tension doesn't exist
   between players today at all.

**Option 1 chosen.** The mole is a substantially bigger swing — a new hidden-role
mechanic between players, not an extension of one that already exists — and deserves its
own research/design pass rather than riding in as "finishing item 3." It's recorded in
[future-features.md](../product/future-features.md) rather than built here.

## Decision

`circles.collect_informant_reports()`'s message gains one optional clause. When the
target's circle has an active project ([ADR 0013](0013-escalating-circle-projects.md)),
the report references the room where the project's most recent qualifying action
happened:

> "Reported by a source: associates with an unregistered circle, one of them recently
> active near {room}."

When there's no active project (most circles, most of the time, especially new/small
ones), the message is unchanged from today: "Reported by a source: associates with an
unregistered circle." No clue, same as now — a circle with nothing running yet has
nothing for the Ministry to plausibly reference, and forcing a hint anyway would read as
noise rather than tension.

The room comes from one new field, `last_event_room`, written by
`circle_projects.check()` whenever it records a qualifying sabotage or delivery
(`char.location.key` at the moment of the call — sabotage happens at the device's room,
delivery at the destination, so this is always the true location of a real, recent,
circle-relevant act). It lives in the same per-slug registry dict the rest of the
project's state already lives in, so it forfeits, resets, and gets wiped exactly when
the project itself does — no separate lifecycle to maintain.

Deliberately **not** wired to a specific member: the room names an act, not an actor.
Casing and the Run are already a shared tally ("any member's sabotage counts") per ADR
0013, so a room hint can never narrow to one name by construction — the ambiguity here
isn't an accident of the message text, it's inherited from the mechanic underneath it.
This also keeps clear of the trap the informant's own fixed location would fall into: a
circle that's recruited exactly one informant would have that informant's post as the
*only* candidate source, turning a "suspected" clue into a "confirmed" one on the spot.
Anchoring to the circle's own activity instead of the informant's position sidesteps
that collapse entirely.

`send_signal()`'s interception message is left untouched. Its "who" isn't ambiguous
(the sender chose to speak, the interception isn't a *leak*) — reading a real room-hint
requirement into it would be sharpening a mechanic that was never the one with a gap.

## Consequences

**Good**

- Directly answers the research doc's framing: circles now have something concrete —
  and true — to argue about when a report lands, instead of identical flavor text every
  time.
- Zero new persistent lifecycle: `last_event_room` piggybacks entirely on
  `circle_projects`' existing registry entry, wiped, forfeited, and reset on exactly the
  same events the rest of that state already is.
- Structurally can't collapse to a named suspect: the shared-tally property that makes
  Casing/the Run circle-wide (not per-member) is what keeps the room hint from ever
  pointing at one person, by construction rather than by care taken in the prose.
- Synergizes with ADR 0013 rather than competing with it: the clue only exists once a
  circle is running a project, so the mechanic sharpens exactly when the stakes (a
  growing pot) are highest, and stays silent for circles that haven't earned any texture
  yet.

**Bad**

- **Coverage is partial, not universal.** Item 3's framing ("every future leak
  mechanic") suggested a general principle; what ships is one sharpened message,
  gated on one precondition (an active project). A circle between projects, or one that
  never starts one, gets the same static text as before this ADR. Worth naming rather
  than implying this "solves" suspected-not-proven everywhere the idiom could apply.
- **The clue is about the circle's activity, not about who received the incident.** The
  member whose file gets the new entry and the member whose action supplied the room
  hint are frequently different people — intentional (it's what keeps this deniable),
  but it means the "victim" of a given report often has no personal stake in the clue
  itself beyond passing it along to circle-mates who do.
- **Still purely reactive.** Nothing changes about *when* reports fire
  (`INFORMANT_REPORT_COOLDOWN`, unchanged) or how often — this ADR only changes what the
  message says when one does.
- **The mole stays undesigned.** The research diagnosis's actual "missing structural
  piece" (hidden roles between players, not just NPCs) is explicitly not addressed here;
  recorded in future-features.md so it isn't lost, but the trust-machine backlog's
  spirit (a real hidden-role tension between circle-mates) is only partially answered by
  this version.

## Revisit when

- A playtest shows players never mention the room hint to each other at all (i.e., it's
  going unread the way a system message would, defeating the point of making it
  diegetic rather than mechanical).
- Someone wants the same treatment extended to circles without an active project —
  would need a different, weaker anchor (there's no equivalent "last real act" tracked
  outside project state today) and is its own design question, not an obvious extension
  of this one.
- The mole (or any other player-vs-player hidden-role mechanic) gets picked up — this
  ADR's "sharpen, don't invent a role" scope choice should be revisited explicitly
  against whatever that design turns out to need, not assumed compatible.
