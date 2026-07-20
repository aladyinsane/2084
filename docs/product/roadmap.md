# Roadmap

Sequenced by "what proves the thesis," not by "what's easy." The thesis: *a surveillance
state is a better MUD antagonist than a bestiary.* Each version is a playable claim.

## v0.1 — The spine (current)

Walkable world + the surveillance loop's skeleton: move through the Grid, be seen,
watch your exposure climb and decay, read your own dossier. No Watch consequences yet —
v0.1 proves the *feeling* of being watched is worth building on before anything punishes.

- [x] Docs workflow: research → principles → ADRs ([ADR 0001](../decisions/0001-evennia-engine.md)–[0007](../decisions/0007-room-graph-grid-consistent.md))
- [x] Evennia project scaffold, pinned venv, runs on Windows
- [x] Classless character: skills/standing/exposure as attributes, no class column
      anywhere ([ADR 0002](../decisions/0002-no-race-no-class.md))
- [x] Rooms with visibility levels 0–5; exits with exposure modifiers; movement through
      watched space accrues exposure ([ADR 0004](../decisions/0004-surveillance-is-event-driven.md))
- [x] Exposure decay on a global script tick
- [x] Prompt shows room visibility and current exposure (`Vis:3 Exp:12`)
- [x] `dossier` command — what the regime's record says about you (the seed of
      [ADR 0005](../decisions/0005-records-are-objects.md)'s record-vs-truth split)
- [x] Starting district: a small, grid-consistent slice of the Grid spanning the
      visibility extremes (checkpoint plaza → tenements → market → tunnels), built from
      versioned batch code ([ADR 0007](../decisions/0007-room-graph-grid-consistent.md))
- [x] Basic tests (exposure accrual, decay, dossier)

## v0.2 — Being watched has teeth

The dread loop closes: consequences arrive, telegraphed in trend, uncertain in timing
(principle 3).

- [x] Sensors as discoverable objects in rooms (spottable; active ones add exposure,
      the broken one in Neon Alley adds nothing — sabotage-able comes later)
- [x] Watch sweep script: samples players with probability scaled by exposure — never
      omniscient, per [ADR 0004](../decisions/0004-surveillance-is-event-driven.md).
      Ships with the ADR's promised dev-facing `watchlog:` trace; verification
      watched a sweep *miss* at roll 0.76 before catching at roll 0.17
- [x] Patrol NPCs whose density visibly tracks district alert level (the telegraph):
      alert rises per detention, decays over quiet sweeps; patrols = baseline + alert
- [x] **Detainment as cmdset swap**: arrested characters lose movement, gain
      `confess`/`wait`/`demand`; release loop returns them changed (exposure reset,
      record annotated) — stakes per [ADR 0006](../decisions/0006-conflict-is-non-lethal.md).
      Verified end-to-end from the player side: swept at Exp 60, celled, `demand`
      resets the wait clock, `confess` releases with the file three incidents longer
- [x] NPC reactions read exposure (the ration clerk's three tiers; patrol visor-tracks
      the noticed and detains the hot on sight)
- [x] Connection screen and all Watch prose pass principle 9's no-magic-missile rule
      (the login terminal is the Ministry's, not the engine's) ← added mid-version
      from the 3M field-research finding
- [x] New-player shallow end verified in **human** playtest (principle 10) —
      happened 2026-07-19 ([findings](../research/playtest-2026-07-19-first-human.md)).
      Verdict: mechanically safe, *experientially* rough — the confusion taxes
      (command overwhelm, unexplained stats, naming collisions) and a flat
      moment-to-moment loop ("a bit dull") spawned v0.7–v0.11 below

## v0.3 — The record is not the truth

The memory/records thesis ([ADR 0005](../decisions/0005-records-are-objects.md)) becomes
playable.

- [x] Record objects: incidents and sensor movement-logs as typeclassed objects, each
      carrying origin/author/subject/content and an **append-only audit trail** every
      mutation writes to first. Sensors log citizens above notice exposure, rate-limited
      (ADR 0005's growth concern)
- [x] Dossier v2: a view over the record layer. Redacted entries vanish but keep their
      numbers — the gap in the numbering is the visible seam
- [x] Record services: the archivist at the Annex amends (4) and redacts (8) for
      standing with the Ministry of Records, earned by `work`; using the service is
      itself noted (+10 exposure). Audit trail always kept
- [x] First skill-by-use loops: clerking (`work`), observation (`observe` — tiered
      readout of a room's devices), forgery (`forge` — rewrite your own file off the
      books, only in visibility-0 dead zones; failure *is* an incident)
- [x] Asynchronous traces, first pass: `listen` in the ration queue surfaces recent
      unredacted incidents about *other* citizens; sensor logs put your movements in
      your file. Richer ambient gossip (NPCs volunteering names unprompted) still to come
- [x] Dead zones are dead ← added mid-version from in-game verification: the sweep
      cannot select someone in a visibility-0 room. Hiding works; exposure barely
      decays; you have to come up sometime

## v0.3.5 — The Orientation Wing (pulled from the parking lot 2026-07-18)

Tutorial-as-architecture, straight from the 3M field research: rooms whose
descriptions are the manual.

- [x] Five-room lattice east of the Assignment Hall (grid-consistent, in the world's
      voice): prompt & exposure basics → the Watch → your file → civic life → a
      **Demonstration Corridor** at Vis 5 whose placard tells you to watch your Exp
      rise as it rises (+5 on entry — teaching by mechanism, not by text)
- [x] The stencilled arrow in the Hall: ATTENDANCE IS VOLUNTARY. ATTENDANCE IS NOTED.
- [x] The orientation clerk (exposure-tiered greetings, per the Citizen system)
- [x] The unsanctioned curriculum: the chalk marks in Tunnel B teach what the Ministry
      won't — dead zones, `forge`, and what a form can do
- [x] The ADR 0007 lint, automated at last: a build test that verifies every compass
      exit has a true reciprocal and the holding cell stays exitless — plus a
      described-devices-exist check (principle 9's in-world corollary)

## v0.4 — Standing and paperwork

The regime as economy: influence, clearances, and bureaucracy-as-content.

- [x] Influence ledger per faction: three ministries now pay standing (Records, Order,
      Commerce), and Records standing is the coin of petitions and Form C-1
- [x] Clearance levels gating exits (locks, not plot flags): a `clearance(N)` lockfunc,
      and the Spire Lobby behind a C-1 gate whose refusal is a palm to the sternum
- [x] EvMenu bureaucratic form: **Form C-1, Application for Elevated Clearance** —
      purposes that are not different, a declaration you must affirm ("my file is
      accurate; it has always been accurate"), a fee retained on rejection, and a
      missing-stamp rejection (Form 77: Employment Verification). The systems chain on
      purpose: a dirty file fails the references check, and the fix is v0.3's record
      laundering. No formal appeal path yet — reapplication after improving one's
      circumstances *is* the appeal, as the archivist hints
- [x] Work assignments: `report`, and the regime reads your recorded aptitudes and
      stamps a *function* on you (Clerk / Auditor / Steward — your skills are your
      application whether you meant them as one). Working your own post pays triple;
      detention **suspends your function** on release — [ADR 0002](../decisions/0002-no-race-no-class.md)'s
      revocable class, demonstrated
- [x] Monitored public channel: `gridwide`, defined in settings so citizens are
      auto-subscribed at registration (the playtest caught the rename-after-creation
      approach silently unsubscribing everyone). Speaking on it costs exposure:
      "your words join the public record"

## v0.5 — Trust

The multiplayer thesis: betrayal outguns everything (principle 6).

- [x] Cells: formed, joined, and left only where nothing watches (`cell`,
      taught by the chalk, not the Ministry); membership is a tag with no
      object to seize; `signal` passes word cell-wide — safe from quiet
      places, interceptable from watched ones. The collective risk is
      **Section C**: a detained member's confession form arrives with
      exactly as many blank lines as they have comrades — `confess names`
      walks free on everyone else's file (+25 exposure each, incident
      recorded), `confess alone` keeps faith and leaves on a shorter leash.
      Verified two-player (claude + julia): the full arc, tip → betrayal →
      julia alone in the kettle circle with two incidents she didn't earn
- [x] Informant NPCs: `recruit`/`sound`/`flip`. Two in Neon Alley; one is
      the Ministry's, and *which* is only readable at real observation
      skill. Street informants tip the cell when a member is taken; plants
      file "Reported by a source" incidents from inside on a cooldown.
      Flipping a plant is a Commerce transaction, and requires being able
      to read them at all
- [x] Scheduled world events where absence is data (M8): civic assemblies
      announce over every loudspeaker, then take the roll at Unity Plaza.
      Present: exposure relief, attendance on file. Absent — *anywhere*,
      including dead zones: an incident, because the list sees what the
      sensors can't. Detainees excused; the Ministry knows where they are
- [x] First honeypot: the Bolt-Hole off Tunnel B, chalk-marked safe,
      Vis 0 — and lying. A concealed live sensor (view-locked; the playtest
      caught it standing in plain sight under "You see:") means the sweep
      reaches in, `forge` refuses without saying why, and movements are
      logged. Fair-warning layers: the too-neat blankets, the chalk's own
      "ask yourself who," the +1 exposure tick at Vis 0, and — if you run
      hot enough to be logged — your own dossier names the room
- [ ] Not yet from this version's ambitions: cell *benefits* beyond
      communication (shared stashes, joint operations) — cells currently
      pool risk more than they pool power. Deliberate: trust must cost
      before it pays, but the pay side is v0.6+ material

## v0.6 — The grind ([ADR 0008](../decisions/0008-grind-loops-sabotage-and-couriering.md))

The mob-grind's shape without the corpse: Lauren picked options 1+2 off the
grind shelf ([research](../research/grind-loops-without-killing.md)). Both loops
pay **the underground** — the first non-Ministry ledger.

- [x] Sensor sabotage circuit: `sabotage <device>` skill checks against live
      devices; failure is an incident + heat (verified live: "the housing
      gives, then bites back", +12 Exp, fault report filed); the maintenance
      crew repairs oldest-first on a timer so the circuit respawns — and only
      repairs *sabotage*: the alley screen predates the backlog and stays
      broken, because nobody files the form. Concealed devices targetable
      only at a practiced observation skill (the honeypot can be blinded —
      temporarily, expensively, gloriously)
- [x] Courier runs: the broker in the ration queue, four destination tiers
      priced by visibility, parcels as real objects, seizure via the systems
      that already exist (papers checks, detainment processing, scanner
      gates). Verified live: a gate run that paid 8+4 jackpot, and a second
      one where gloved hands found the parcel on the second pat — and the
      exposure from *that* fed the patrol detention two rooms later. The
      systems chain without being told to
- [x] The underground's first sink: clean `papers` (standing → exposure
      relief) so the loop closes in one session. Playtest caught the dossier
      leaking the underground's ledger and the off-the-books aptitudes
      (including `forgery`, leaking since v0.3) — the Ministry's file now
      contains only what the Ministry could have observed
- [x] Curriculum audit (contributing.md rule 9, new this version): assemblies
      added to the Wing's civic placard; sabotage/carry/papers added to the
      chalk — and the audit itself caught that v0.5 never chalked the
      informant verbs (recruit/sound/flip). Now it does

## The 2026-07-19 batch (from the [first human playtest](../research/playtest-2026-07-19-first-human.md))

Sequenced legibility-first: fix what confuses before building what excites,
because renames get more expensive with every feature built on top of them,
and because confusion is a fun-tax on everything downstream. One PR per
version; merge on green tests per Lauren's standing instruction.

## v0.7 — Legibility

The playtest-response version. No new systems; the existing ones become
readable.

- [x] Prompt spells out `Exposure` (Exp reads as experience points to every
      MUD veteran)
- [x] Helpfiles for the two core stats (visibility, exposure) plus
      `help the grid` — file-based entries in the world's voice
- [x] Command-overwhelm audit
      ([command-surface-audit.md](../research/command-surface-audit.md)):
      verdict was organization, not amputation — help now splits "the grid"
      from "the underground" (mirroring Wing vs. chalk), `score` aliases to
      `dossier` for thirty years of muscle memory, and one standing rule:
      new features ride existing verb patterns before minting new ones
- [x] Rename: `sound` → `judge` (old name kept as alias); player cells →
      **circles** (`circle form/invite/join/leave`) — the holding cell
      keeps the word, it had it first
- [x] Display fixes: NPC names capitalized in listings/poses (keys stay
      lowercase for the fiction); "a the chalk marks" article stacking
      fixed for any "the "-prefixed key
- [x] Detention onboarding: `help` joined the detained command set, and the
      holding cell wall now carries Form 12-D, NOTICE OF REMAINING
      ENTITLEMENTS — the room is its own manual, per the Wing's pattern

## v0.8 — The map (left the parking lot)

The ASCII map, deferred since v0.1 on purpose (ADR 0007 kept it cheap).
Disorientation stopped being tonally useful and started being friction.
Default choice per the parking lot: the `ingame_map_display` contrib over
our grid-consistent room graph, presented in-fiction.

- [x] `map` command rendering the local area from the room/exit graph
      (`ingame_map_display` contrib subclassed — ADR 0007's discipline paid
      off: zero migration, the world just mapped)
- [x] In-fiction framing: your own recollection, since no map of Sector 9
      is issued or acknowledged to exist. The 2084 twist: rooms render as
      their |wvisibility digits|n, so the map is a route-planning tool for
      staying dark, not a convenience. Locked exits aren't drawn past —
      the Spire is off your map until you hold C-1 (though the gate's
      dangling exit-line hints at it, which is better fiction than hiding
      the gate). The Bolt-Hole maps as 0: the map is your knowledge, and
      your knowledge is exactly as good as the room's lie

## v0.9 — Errands (the quest system)

The broker proved the shape; generalize it so any tagged NPC can hand out
work with a destination, a condition, and a payout.

- [x] Quest framework (`world/errands.py`): one verb (`errands`) per the
      command-surface audit; completion *listens* to verbs the player
      already has (movement, `work`, `observe`, `deliver`, assembly rolls)
      rather than minting quest actions. Risk stated on every offer;
      chains gate on prerequisites and never repeat (a re-takeable
      commendation would be a farm)
- [x] The courier board rides the framework the other way round: courier
      runs stay as they are, and errands can *require* one (the
      lamp-mender's "Legs" sends you to the broker) — generalizing the
      giver, not duplicating the run
- [x] Five launch errands in two chains: the orientation clerk's "nobody"
      questline (The Rounds → Visible Usefulness → Countable, ending in a
      named commendation in your file — safe play is now a campaign, per
      the fun research) and the lamp-mender's careful-people chain (Look
      Closer → Legs, ending in the bolt-hole warning — a named reward
      worth more than it pays)

## v0.10 — Implants (equipment)

3M's implant catalog ([field research](../research/third-millennium-mud.md)),
inverted for the Grid: the state issues what it can monitor; the black market
sells what it can't.

- [x] Wear/remove slots (one item per slot — 3M's memory-slot lesson, worn
      instead of implanted because Airstrip One is analog); MUD-stock verbs
      per the audit: `list`/`buy`/`wear`/`remove`. State issue at the new
      requisitions window: the **badge** (better counter pay / warmer in
      watched rooms) and the **wellness monitor** (heat fades twice as
      fast / movements log twice as easily). Every issue recorded, of
      course
- [x] Black-market gear on the broker's second shelf, shown only to
      citizens the underground knows: the **foil-lined coat** (entry heat
      shaved / clerks distrust it) and the **dead-man pocket** (eats
      exactly one search, then it's spent) — the courier's insurance
      policy
- [x] Principle 9 gate: every item is cloth, foil, or lamination doing
      exactly what such a thing could do; every item is a trade, never an
      upgrade. Playtest caught the buy message advertising an alias the
      item didn't have ("wear cuff") — fixed

## v0.11 — Circle benefits

The pay side of trust (owed since ADR 0008 named the one-sink economy).

- [x] Shared stash: `stash` establishes one cache per circle, first use,
      dead zones only — a loose brick, invisible to everyone including
      members (knowing where it is IS the membership; no lock ever worked
      better). And Section C has an address line now: a confessed circle's
      cache is confiscated wholesale, the last member out spills it where
      it stands. Emergent bonus found in playtest: caching a parcel
      mid-run is real smuggling risk-management
- [x] Joint operation: the lamp-mender's "Four Hands" — completes only
      with a circle-mate standing in the same dark room, whichever of you
      arrives second
- [x] Underground-ledger sinks: v0.10's black-market shelf (8+5) plus
      papers already sized the sink side; the stash adds storable value.
      Watch inflation at the next playtest gate regardless

## v0.8.5 — Juice (from [fun-and-game-feel.md](../research/fun-and-game-feel.md))

The cheap immediate fixes for "a bit dull," ahead of the content versions:

- [x] Near-miss telegraphy: sweep rolls and scanner-gate rolls that *miss*
      are felt ("a visor lingers a half-second too long"; "the scanner's
      tone deepens for one syllable") — dread we already computed and were
      throwing away
- [x] Login digest: "Since you were last on the Grid:" — new file entries
      since last logout, plus which of your circle is out there now.
      Deliberately silent when there is nothing to tell
- [x] Ambient texture tick: `AmbienceScript`, occupied rooms only,
      rate-limited per room; six rooms got bespoke murmur lines and the
      rest fall back by visibility (dead zones get their silence described)

## Cross-cutting for the batch

- ~~The **fun research pass**~~ done — [fun-and-game-feel.md](../research/fun-and-game-feel.md):
  five named dullnesses, each assigned to a version; quests and implants
  inherit its shapes (risk tiers stated up front, named rewards, the
  want-ladder, a "nobody" questline so lying low is a campaign)
- Curriculum audit per version (contributing rule 9), as always

## The learning-curve response (from [the-first-hour.md](../research/the-first-hour.md))

Lauren's concern, 2026-07-19: the world is right but the curve is steep enough
to chase players away, and familiar combat/leveling might be the answer. The
research's verdict: the familiar shapes already exist wearing unfamiliar
clothes; surface and sequence them before adding systems. Tier 3 (composure
sparring, the combat-shaped loop) stays parked until tiers 1–2 are measured.

## v0.12 — Citizen Grades (the familiar ladder)

One visible grade — the legibility of a level without a new progression
system underneath. Derived entirely from numbers we already track.

- [x] Grade derived from sanctioned progress only (ministry standing,
      errands completed, function held, clearance) — formula in tuning.py;
      the underground ledger never feeds it, and neither do the errands it
      pays for (the dossier-leak lesson, applied in advance this time).
      Merit is *lifetime* earnings (`db.influence_earned`), so spending
      standing at the Annex never demotes — the XP/gold confusion the
      ladder exists to prevent. Losing your function does demote, on
      purpose: detention now costs a visible rung
- [x] Civil-service shape: Grade 6 (probationary) descending to Grade 1;
      dossier states merit and the next review threshold
- [x] Prompt leads with the grade (`[G5 Vis:0 Exposure:12]`);
      reclassification is FORM 9-A with fanfare and a record entry —
      verified live: G6 → G5 → G4 inside one first-session arc
      (orientation → report → The Rounds → one shift)
- [x] Endowed progress: walking the Demonstration Corridor credits merit
      sized to land Grade 5 exactly — the first grade-up arrives minutes
      into play
- [x] Display-only, as planned: grades gate nothing (Form C-1 or pay
      referencing them would be a new decision)
- [x] Curriculum audit: the civic placard explains the ladder, the
      corridor placard announces the credit, `help grade` (aliases
      level/rank/merit) speaks to thirty years of muscle memory
- [x] Playtest finding worth its own entry: an idle-but-connected citizen
      accrues an assembly-absence incident every ~16 minutes (claude
      logged 35 overnight). Recorded under known risks — MUD players
      idle, and the current rule farms them

## v0.13 — The First Hour

Sequencing the existing surface. Nothing locked, everything staged.

- [x] Progressive disclosure: bare `help` shows THE PERMITTED FORMS OF
      ASSISTANCE (ABRIDGED) — nine first-hour verbs — until orientation
      completes; `help all` is always the full index (shown, never
      locked — MUD veterans skip ahead by right)
- [x] `next` (aliases hint/whatnow): CITIZEN ADVISORY, FORM 2-B — one
      suggestion from actual state, priority-ordered: active errand →
      orientation → `report` → cooling down when hot → an errand giver
      (catalog order on purpose, so the clerk's safe chain is suggested
      before the lamp-mender's — the playtest caught set-ordering
      offering the underground to a citizen five minutes old) → the
      standing fallback
- [x] The remaining aliases: `quests`/`quest` → errands; `grade` is now
      a command (`level`/`rank`/`merit`) giving the three-line answer to
      "am I leveling?" — its helpfile moved from the file entry into the
      command, which shadows same-key file help
- [x] First-login funnel: NOTICE OF ARRIVAL (FORM 1-A) on first puppet —
      one card naming orientation, `next`, and `help`, never shown
      again; the antechamber placard teaches `next`
- [x] Gate met: fresh-account run (parsons) — welcome → orientation →
      Grade 5 in ~60 seconds; function, first errand complete, and
      Grade 4 in under three driven minutes (~25 commands, zero dead
      ends; a reading human should land G4 inside the first quarter
      hour). `grade` mid-arc read "1 to go," which is the goal-gradient
      working as the research drew it
- [x] Playtest also sharpened the idler risk: parsons was fined for
      missing an assembly announced before the account existed (entry
      updated under known risks)

## v0.14 — The Grid hears you (from the [ten-persona playtest](../research/playtest-2026-07-20-ten-personas.md))

The command-not-found overhaul: six of ten personas hit the default
fuzzy-suggester, which leaks the unsanctioned curriculum (`sabotage`,
`stash`), leaks engine verbs (`charcreate`, `setdesc`), and answers the
commonest newbie error (a direction with no exit) with nonsense.

- [ ] Custom no-match handler: unknown directions answer in-fiction with
      what actually leads out
- [ ] Instinct verbs (kill/attack/flee/cast/hide/sneak/talk/ask/where/
      read/stats/go) each get a bespoke line in the Ministry's voice,
      with a mechanical pointer where one exists — the "no combat"
      thesis finally gets to speak when someone types `kill`
- [ ] Suggestions filtered to the sanctioned surface: never the chalk's
      verbs, never the engine's
- [ ] Curriculum audit as always

## Later / undecided

The parking lot, including the **ASCII map**: [future-features.md](future-features.md).

## Cross-cutting, always

- World stays grid-consistent — every batch-built room passes the ADR 0007 discipline
- Every loop single-player-viable before it ships (principle 8's test)
- Every version audits the curriculum before merge: new sanctioned verbs reach the
  Orientation Wing placards, new unsanctioned ones reach the Tunnel B chalk
  (contributing.md rule 9)
- Playtest gate between versions: the named risks in
  [future-features.md](future-features.md#known-risks-in-shipped-features) get checked
  against real sessions, not intuition
