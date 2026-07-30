# ADR 0018 — The Orientation Wing becomes genuinely interactive, and teaching starts reaching past it

- **Status:** Accepted
- **Date:** 2026-07-28

## Context

Lauren's ask, 2026-07-27 (delivered while she was signing off for the night, with
explicit license to keep working without her): redo the tutorial area so it walks a
citizen through actually *using* each command, very interactively — and floated that
"it's possible the entirety of Sector 9 will ultimately become the tutorial area."
She also wants the tutorial's ending to leave a citizen with a concrete idea of what
to do next to move down grades.

This ADR is written and the safer parts of it implemented tonight, without her
review — a genuine judgment call given how much of this touches load-bearing,
identity-defining content (every new player's first ten minutes). The riskier,
more creative parts (new room prose) are sketched here as illustrative drafts, not
yet written into `world/build.py`, so there's something concrete to react to without
content having shipped unreviewed. See §6.

**Auditing what's actually there first**, same move as every ADR since 0015: the
Wing is 5 rooms (`o_ante` → `o_watched` → `o_file` → `o_civic` → `o_corridor`,
[v0.3.5](../product/roadmap.md), deepened [v0.15](../product/roadmap.md)). Of those,
only **two** currently have a genuine "try it now, type X" interactive moment —
`o_watched` (`observe`) and `o_file` (`dossier`). `o_corridor`'s exposure-jump is
interactive in a different, mechanical sense (teaching by *feeling* a number move,
not by typing a verb). `o_ante` and, most notably, `o_civic` are prose walls: `o_civic`
alone currently *mentions* `report`, `work`, `apply`, `vouch`/`unvouch`, `listen`,
`grade`, `gridwide`, `errands`, and `list`/`buy`/`wear` — nine verbs, zero enforced
interaction. Separately, `world/onboarding.py` (v0.15) already gives the Wing a
sector-wide reach in spirit: a citizen's first-ever use of a tracked verb gets a
one-time in-fiction acknowledgment *wherever it happens*, deliberately placeless —
but it currently only tracks seven verbs (`map`, `observe`, `dossier`, `grade`,
`errands`, `report`, `work`), the exact v0.13-era set. The verb surface has grown
past both of these systems since (`research`, `vouch`/`unvouch`, `apply`,
`list`/`buy`/`wear`, `petition` all shipped after the Wing's last content pass), and
neither system caught up.

**One real, named tension worth resolving explicitly, not silently overriding:**
[v0.15's own design note](../product/roadmap.md) states the acknowledgment system is
deliberately non-gating — "nobody who skips it is worse taught for finding the verbs
on their own" (ten-persona playtest: the min-maxer who skipped orientation entirely
still did fine). Lauren's ask for something citizens are *walked through* is a real
step toward enforcement, which is in tension with that. Resolution: keep the
underlying principle (nobody is punished for skipping the *Wing specifically* — a
citizen who finds `sabotage` via the chalk instead of orientation is still fine, same
as always) but change what happens **inside** the Wing if a citizen chooses to walk
it: currently walking through costs nothing and teaches passively; this ADR makes
entering the Wing a genuine, enforced, interactive experience, the same shape 3rd
Millennium's Center for Higher Learning already proved works (field research,
[third-millennium-mud.md](../research/third-millennium-mud.md) §5) — nothing
*outside* the Wing becomes less accessible, but *inside* it, walking past a room
without doing the verb no longer counts as having done it.

## Decision

**1. One enforced "try it now" per Wing room, not a wall of mentions.**
Every Wing room keeps exactly one verb it actually requires. `o_civic` currently
tries to teach nine; this ADR narrows its *required* verb to `grade` (already the
hint `firsthour.py`'s `_wing_hint` gives for that room, so this is catching up to
what `next` already assumes) and moves the other eight to natural-location teaching
(§2) instead of cramming them into one room's placard. Illustrative sketch of what
"enforced" looks like in-fiction for `o_watched` (not yet written into `build.py` —
see §6):

> *(current, unenforced)* "Try it now: type observe, right here..."
> *(proposed, enforced)* the room's exit north stays a real exit the whole time
> (never a hard lock — see the "no magic-missile moments"/principle 9 note below),
> but the room's own completion credit (the `wing_watched` tag firing its
> onboarding acknowledgment) only fires once `observe` has actually been typed
> there — tracked via `onboarding.py`'s existing `first_use_verbs` set, which
> already exists and already knows exactly this.

**Deliberately not a hard exit-lock.** A literal "you cannot leave until you comply"
gate is a magic-missile moment principle 9 explicitly warns against (that's a puzzle-
room mechanic, not a citizen's actual relationship to a room) — and it would also
resurrect exactly the "MUD veterans skip ahead by right" problem `the-first-hour.md`
already fought to remove (progressive disclosure, never locking). Instead: leaving
without trying the verb is always possible, but orientation's *completion credit*
(`db.oriented`, gating the abridged-help card and feeding Grade merit) requires
having exercised the core verbs somewhere along the way — enforced at the finish
line (`o_corridor`), not at every doorway.

**2. Natural-location teaching for the verbs the Wing can't hold.**
`onboarding.py`'s acknowledgment dict grows to cover the verbs that shipped after
v0.13 and don't fit the Wing's five rooms: `research`, `vouch`/`unvouch`, `apply`,
`petition`, `list`/`buy`/`wear`, `listen`. This is the actual, cheap, honest answer
to "possibly all of Sector 9 becomes the tutorial area" — not a Wing rebuild, but
deepening a system that was *already* placeless and sector-wide by design. A citizen
who first uses `research` at the real Archive Annex gets a real, first-time
in-fiction acknowledgment right there, the same shape `map`/`observe`/`dossier`
already get. This scales indefinitely as the verb surface keeps growing, without
ever needing the Wing itself to grow room-for-room to match — which is the actual
lesson of v0.15's original design, just not yet applied past its original seven
verbs.

**3. Orientation completion is gated on having actually used the core verbs.**
`db.oriented` currently sets on walking `o_corridor` OR taking `report` (v0.16 fix
for orientation-skippers). This stays — a citizen who skips the Wing and reports for
work is still correctly "oriented" per the existing, deliberate v0.15/v0.16 logic.
What changes: a citizen walking the Wing itself doesn't get the Corridor's merit
credit and Grade-5 endowment until `map`, `observe`, `dossier`, and `grade` all
appear in their `first_use_verbs` set — closing the actual gap Lauren named (you
could currently walk all five rooms, read every placard, type nothing, and still
get full credit).

**4. Orientation completion hands off to `next` explicitly, not by reference.**
`o_corridor`'s placard already says "Exit WEST... The Grid is waiting" — it never
actually shows the citizen what `next` would say. The completion moment (wherever
`db.oriented` flips to `True` via the Corridor path) now also fires `CmdNext`'s own
`_advice()` logic directly, printed as part of the completion message, so a citizen
who has never once thought to type `next` still receives its answer at exactly the
moment they need it — the concrete "what do I do to move down grades" close Lauren
asked for, built entirely out of `next`'s existing, already-good, state-aware logic
rather than a new hand-written speech that would drift out of sync with reality
(exactly the kind of drift ADR 0015/the docs audit kept finding elsewhere).

## Consequences

**Good**

- Directly answers all three parts of the ask: genuine interactivity (gated, not
  just suggested), sector-wide reach without a Wing rebuild, and a concrete
  next-steps close built from state, not scripted prose.
- Resolves the v0.15-vs-"walk the user through" tension explicitly, in writing,
  rather than quietly picking a side — the underlying "skipping the Wing costs
  nothing" principle survives; only what happens *inside* the Wing changes.
- Reuses `onboarding.py`'s architecture wholesale (it was already placeless and
  sector-wide *in design*, just narrow in *content* — this is catching up, not a new
  system) and `next`'s existing advice logic (no new hand-written text to maintain
  in parallel with what `next` would say anyway).
- No magic-missile hard-locks; principle 9 and `the-first-hour.md`'s "never lock,
  only sequence" rule both stay intact.

**Bad**

- **`o_civic`'s eight demoted verbs lose their one placard mention** unless
  natural-location acknowledgments (§2) genuinely land as well as a dedicated room
  currently does. This is a real bet that "taught where you actually do it" beats
  "taught in the museum room," unverified until a playtest — the same bet v0.15
  already made and the ten-persona playtest already validated once, but not at this
  scale (seven verbs then, growing to thirteen-plus here).
- **A returning citizen who partially orients, logs off, and comes back** needs
  `first_use_verbs` to have actually persisted the right entries — it's a normal
  Attribute, so it does, but this is the first feature to make that set load-bearing
  for something more than flavor text; worth a specific test.
- **This ADR explicitly does not implement new Wing room prose tonight** (§6) — the
  gating/hand-off mechanism ships, but `o_civic`'s new narrower text and any new
  natural-location acknowledgment copy are sketched, not committed. That's a
  deliberate scope cut given the hour, not an oversight; see Revisit-when.
- **Doesn't touch "possibly all of Sector 9" in the literal sense** of rewriting
  every room description as tutorial content. Reads Lauren's own hedge ("it's
  possible... ultimately") as permission to answer the *spirit* of that (teaching
  reaches everywhere) without committing to the much bigger, riskier literal version
  (every room description rewritten) unilaterally, overnight, without her having
  seen a single line of it.

## §6. What's implemented tonight vs. sketched for review

**Implemented** (mechanical, low creative risk, follows existing patterns exactly):
`onboarding.py` gains entries for the six additional verbs named in §2, gating
logic for `o_corridor`'s completion credit (§3), and the `next`-advice hand-off at
completion (§4). Tests cover all three. Not touched: any existing room's `desc`
string in `build.py`.

**Sketched, not written (at merge time):** `o_civic`'s narrowed placard (dropping
to just the `grade` prompt, per §1's illustrative sketch) and the exact wording of
the six new onboarding acknowledgments. Both were exactly the kind of voice-matching
creative work worth Lauren's eyes before it ships, at this scale, given how
load-bearing this content is.

**Update, 2026-07-29:** Lauren reviewed this ADR and approved the approach as
written, including the §1 split (narrow `o_civic` to `grade`, teach the other eight
verbs at their real locations) and the no-hard-lock shape. The onboarding
acknowledgment wording actually shipped with this ADR's original implementation
commit, not in a follow-up — that part of this note was already stale by merge
time. `o_civic`'s placard narrowing is the one piece that genuinely followed as a
separate PR, implementing the §1 sketch as written.

## Revisit when

- Lauren reviews and either approves the sketched room-prose direction as-is, wants
  a different split of which verbs live in the Wing vs. natural-location teaching,
  or wants the Wing to physically grow instead (more rooms, not fewer verbs-per-room)
  — a real, different shape this ADR didn't choose, and should if she prefers it.
- A playtest shows the demoted `o_civic` verbs going genuinely untaught (nobody
  reaches the Annex/Requisitions window/vouch naturally within a first session) —
  candidate fix: `next`'s advice sequence could explicitly route a fresh citizen
  through those locations the way it already routes through errand givers.
- Someone wants the literal "whole sector rewritten as tutorial" version after all
  — that's a much bigger, separate commitment and should get its own ADR rather than
  retrofitting this one.
