# Research: "outside the Grid" against principle 9 (alien contents all the way down)

ADR 0020 scoped the farmers-vs-Ministry resource conflict ("the world outside the
Grid," `future-features.md`, Lauren's journal, 2026-07-25) into real work, and named
its own "Revisit when" condition: a principle-9 research pass, same weight every
other district's fiction got before being built, before any room-by-room content
gets written. This is that pass. Same shape as
[opposed-checks-for-existing-verbs.md](opposed-checks-for-existing-verbs.md) — it
surveys the space and names the real tensions, it does not decide anything, and
nothing here is a proposal to build.

## Background: what principle 9 actually tests, and what broke last time

Principle 9 isn't "reskin the words." The 3rd Millennium finding
([third-millennium-mud.md §7](third-millennium-mud.md)) is specifically that a
*superb* delivery fiction (implant downloads, RAM, biotech upgrades) still let
`magic missile`, `chill touch`, `cure light`, and "elves' tear" sit undisguised in
the catalog a new player opens in their first ten minutes. The failure mode isn't
"we forgot to reskin" — CircleMUD's stock *zones* are entire pre-built areas that
ship with the engine, dropped in wholesale because building fantasy content is
free and building sci-fi content isn't. The fiction converted the system (the
verbs, the framing, the delivery); it never touched the stock *content* sitting
inside that system, because the stock content was never authored by the team in
the first place — it came with the chassis.

That distinction matters for this audit, because it changes where the actual risk
sits for 2084's farming/rural area.

## Finding 1: Evennia doesn't hand us a stock-zone risk the way CircleMUD did — the risk moves upstream, into what gets *authored*

[evennia-capabilities.md](evennia-capabilities.md) is direct about this: Evennia
ships a chassis (movement, `look`, `get`/`drop`, `say`/`whisper`, `help`, locks,
cmdsets) and no world content at all — no zones, no item catalog, no spell list.
"Evennia gives us the chassis for free" (principle 9's own "Because" line) is true
in a stronger sense than it first reads: there is no equivalent of CircleMUD's
`world/` zone files bundled with the engine for a lazy build to drop in
unconverted. Every room, NPC, and item in Sector 9 and the Underground was
hand-authored by this project already (`game/world/build.py`) — there is no stock
farming content Evennia could hand us even if we wanted it.

Two specific places worth checking directly, since "no stock zones" isn't the same
as "no stock text anywhere":

- **Default help entries and command names.** Evennia's stock cmdset (`look`,
  `get`, `drop`, `say`, `whisper`, movement, `help` itself) is genre-neutral by
  construction — none of it says "sword" or "spell" or, for that matter, "crop."
  Nothing here needs conversion for a farming area specifically; it's the same
  chassis Sector 9 and the Underground already sit on cleanly.
- **Contrib packages.** `evennia-capabilities.md` lists `crafting`, `clothing`,
  and `extended_room` as available. If a farming area reached for the `crafting`
  contrib for anything (turning grain into flour, e.g.), that contrib ships its
  own example recipes and default categories from its own docs/tutorial context —
  those examples are exactly the kind of thing that could get half-adapted and
  left in a build. Not a live risk today (nothing has reached for `crafting` yet),
  but worth flagging now so a future implementer checks the contrib's own
  shipped examples with the same suspicion 3M's zone files deserved, rather than
  assuming "it's Evennia, so it's already clean."

**The actual risk for this area isn't stock content bleeding through the
engine — it's genre bleeding through the authors.** Nobody on this project has
ever had to resist "well CircleMUD already has a farm zone, let's just retheme
it" — that shortcut doesn't exist here. But a first draft of a farming area
written from scratch, without deliberate pressure against it, can arrive at the
same failure by a different road: reaching for the nearest cultural template for
"farming in a game," which is Stardew Valley / Harvest Moon / generic fantasy
farming-sim, not 1984. That template comes pre-loaded with its own verb set and
its own emotional register (wholesome, cozy, growth-and-abundance), and both are
wrong for this game.

## Finding 2: the "magic missile" equivalents to actively guard against

Concretely, the tropes a lazy first draft would reach for, and why each is wrong
for 2084 specifically (not just "wrong for a dystopia" — the game already has a
working antidote pattern in Sector 9 and the Underground, worth measuring against):

- **Dedicated farming verbs (`till`, `plant`, `water`, `harvest`).** These are the
  genre's own small-verb vocabulary, and principle 7 already commits this project
  to small verbs carrying weight — so the instinct to add hyper-specific verbs
  isn't wrong on its face. The risk is *which* verbs get added and what they
  imply about stakes. `till`/`plant`/`water`/`harvest` as a cozy agricultural
  loop (grow the thing, watch a number go up, sell it) is Stardew Valley's loop,
  not 1984's — it implies the land as a source of *personal* abundance and
  progress, when the entire point of this area, per the future-features entry,
  is the state's *appropriation* of the land. Sector 9's small verbs
  (`observe`, `petition`, `stash`) all point at surveillance or bureaucracy;
  the Underground's (`sabotage`, `word`) point at resistance and standing. A
  farming verb set needs the same discipline — verbs about what the *conflict*
  over land and water looks like moment to moment (a water allotment check, a
  land-use inspection, a boundary dispute, a crop requisition quota), not verbs
  about the pleasure of growing things for their own sake.
- **Livestock and crop *flavor as fantasy-agrarian pastoral.*** Warm hearths,
  simple honest folk, a market day — this is the generic "countryside" register
  borrowed from fantasy MUDs and farming sims alike, and it's a genre smell the
  same way `magic missile` was: instantly recognizable as *not this game's*
  voice. Sector 9's prose voice (sampled from `build.py`: "paved in regulation
  grey," "a queue exists whether or not anything is being distributed," "the
  residents work hard to keep it thinking so") is bureaucratic-bleak with dry
  irony threaded through, never quaint. A rural area drawn as quaint-agrarian
  contrast to the urban dystopia (the "unspoiled countryside" cliché) would read
  as a different, gentler game bleeding into this one.
- **A resource/economy minigame bolted on for its own sake** (crop yields,
  seasons, weather affecting output, a farming skill that levels for its own
  reward). This is the specific shape ADR 0003 already rejected wholesale for
  the whole game — XP-and-levels-shaped systems — and `game-theory-of-the-grid.md`
  / `opposed-checks-for-existing-verbs.md`'s discipline about not reviving cut
  systems applies here too. A farming subsystem with its own progression curve,
  disconnected from Exposure/Influence/standing, would be a second, incompatible
  game grafted onto this one — a subtler version of the same "genre bleeds
  through" problem, expressed as *systems* rather than *words*.
- **"Simple folk" NPC voicing.** Rural NPCs who are folksy, warm, plainspoken in
  a way that reads as *safe* by contrast with the city would undercut principle
  1 directly (see Finding 3) — it would code the countryside as an escape from
  the antagonist rather than another place the antagonist operates.

## Finding 3: principle 1, checked hard — the real risk, and it's real

The future-features entry frames this as "a different axis on principle 1's
antagonist — the regime's hunger for resources, not only its hunger for legible
citizens," and that framing is sound *in the abstract*. The open question ADR 0020
carried forward is whether it survives contact with actual play: does the
Ministry stay legible as the antagonist out here, or does the area drift into an
environmental/resource-conflict subplot that's mechanically disconnected from what
makes the rest of the game 2084?

This is a real risk, not a formality to wave through. Reasons it's real:

- **Sector 9 and the Underground both express principle 1 through the same
  small set of mechanical levers**: Exposure/Vis (principle 3), the dossier and
  record-vs-truth gap (principle 4), standing and clearance (principle 2/ADR
  0003), and non-lethal stakes running through detainment (principle 5). Every
  verb audited in Finding 2 needs an answer to "which of these levers does this
  touch," or it's decorative. A `till` verb that raises no Exposure, writes no
  record, and risks no detainment isn't a 2084 verb wearing a farming costume —
  it's a farming-sim verb wearing a thin 2084 label, which is exactly principle
  9's failure mode restated as a systems problem instead of a words problem.
- **The Perimeter concept already names the mechanical hazard explicitly.**
  `worldbuilding-ideas.md`'s Perimeter sketch describes "unmonitored prole
  housing where citizens operate without formal dossiers — too insignificant
  for the Ministry of Records to index." That's the right texture for M2
  (surveillance is unevenly distributed — proles are barely watched) but it is
  also, read mechanically, a description of a place with nothing for the
  dossier/Exposure/standing systems to hook into. An area that is *authentically*
  under-indexed, taken at face value, is an area where the game's actual
  mechanical language has the least to say — which is a legitimate fictional
  choice (M2 is real) but a design trap if nobody notices it's happening. The
  antidote can't be "make it just as watched as Sector 9" (that would erase the
  fictional point); it has to be a *different* mechanical expression of the same
  antagonist, not the absence of one. See the worked list below.
- **A resource conflict has its own narrative gravity that doesn't need the
  Ministry to work.** "Farmers vs. a hungry state" is a complete, compelling
  story on its own — which is exactly the danger. It's coherent enough to ship
  *without* ever touching Exposure, dossiers, or standing, and still feel like a
  finished area, the same way a competent fantasy zone is coherent without ever
  touching 2084's systems. Coherence-on-its-own-terms is not the bar; connection
  to *this* game's terms is.

**What "the Ministry stays legible out here" would need to mean mechanically**,
worked from principles 3/4/5/7 the way the prompt asked, without proposing actual
implementation:

- **Principle 3 (surveillance is dread, not damage), reshaped for low density.**
  Sector 9's Vis/patrol-density expression assumes camera-dense streets; a rural
  area doesn't have that texture to draw on honestly (M2 says it shouldn't). The
  mechanical question this area has to answer, not this doc: what *does* dread
  look like where cameras are sparse? Candidates worth naming as a starting
  point for that later design pass, not decided here: overflight/drone sweeps on
  a slower, more visible cadence than Sector 9's Watch sampling (dread from
  *predictability* instead of ambient uncertainty — a genuinely different flavor
  of the same principle, not a weaker copy of Sector 9's); a land/water permit
  system where the *paperwork itself* is the surveillance surface (you're watched
  through what you're required to file, not through cameras); informants drawn
  from the same rural community (M6's betrayal mechanism, relocated).
- **Principle 4 (the record is not the truth).** The clearest, most natural hook
  for this area, arguably its strongest one: land surveys, water allotments, and
  crop-yield quotas are *records* in exactly ADR 0005's sense, and a regime that
  wants your land has an obvious, textured motive to misrecord your yield, your
  allotment, or your boundary — the forgery/petition loop already built for
  citizen dossiers has a near-exact structural twin here (a falsified survey
  instead of a falsified incident). This is the strongest candidate for "what
  makes it 2084 and not generic dystopian farming" that this pass found, and it
  costs nothing new: it's the existing record-vs-truth machinery pointed at land
  instead of people.
- **Principle 5 (non-lethal stakes).** Requisition, relocation, and "resettlement"
  are the land-conflict equivalents of detainment/unpersoning — the regime does
  not need to kill a farmer to take a farm, and eviction-without-violence is
  arguably a *more* on-theme catastrophe here than anywhere else in the game,
  since ADR 0006's whole thesis is that the regime's real weapon is administrative,
  not physical.
- **Principle 7 (small verbs carry weight).** The genuinely 2084-flavored small
  verbs for this area are administrative and adjacent to the land, not
  agricultural for its own sake: filing (or not filing) a water-use report,
  under-reporting a yield, disputing a boundary marker, hosting a Ministry
  surveyor. The "till soil" instinct from Finding 2 fails this test directly —
  it's not a small verb with regime-legible weight, it's a small verb with
  *no* weight, dressed as one.

**Bottom line on principle 1**: the risk is real, and the future-features entry
was right to flag it as open rather than assumed-fine. It survives only if the
area's mechanical spine is built from the record-vs-truth and administrative-
stakes machinery above, not from a farming-simulation spine with 2084 flavor text
sprinkled over it. If nobody chooses that spine deliberately during the
follow-up design pass, this area will drift into the environmental subplot this
finding warns about — not because anyone chose that, but because a resource
conflict is compelling enough to coast on its own premise without anyone
noticing the game's actual systems never showed up.

## Finding 4: principle 10, checked — bleaker premise, but not an obvious violator

A land-and-water conflict where a resource-hungry state can simply take what it
wants from people with little recourse has real potential to read as bleaker than
Sector 9's bureaucratic dread — closer to something with no upside at all, which
principle 10 rules out ("dread, yes; tedium and despair-spirals, no").

Weighed against what's already in the game, though, this isn't obviously worse
than what Sector 9 and the Underground already carry. Detainment, unpersoning,
and betrayal (principles 5/6) are already about as bleak a catalog of outcomes as
a non-lethal game can offer, and principle 10's answer for those isn't "make the
stakes smaller," it's "give every catastrophe an obvious next move, and give the
world a pressure valve independent of the state" — the pub, gallows humor, the
proles' vitality (M2/M8's warmth, explicitly named in
`orwell-1984-source-material.md`'s "bleakness ceiling" section as the novel's own
material for this, not invented for the game). That pattern is a genuine, cited
mechanism to reuse, not just an analogy.

So the real question isn't "is this area sadder" (plausibly yes, a little) but
"does this area get its own version of the escape valve, or does it borrow
Sector 9's and expect it to reach out here." Two observations, not a decision:

- **The escape valve probably can't just be geographic proximity to the pub.**
  If this area sits far enough outside the Grid to feel genuinely different (the
  whole point, per Finding 3), routing every bad outcome back to Sector 9's pub
  for its release valve undercuts the area's own identity, the same way it would
  undercut principle 1 to route every mechanic back to Sector 9's surveillance
  UI wholesale.
- **But the underlying narrative material travels intact.** M2/M8's "the
  proles' vitality is real" isn't a Sector 9-specific finding — Orwell's own
  material (I.7's warmth, cited in `orwell-1984-source-material.md`'s
  "bleakness ceiling" section) is about the proles generally, not the city
  specifically. Rural communities plausibly get their own version of gallows
  humor, their own gathering place, their own gossip network, and the
  "warmth despite everything" texture isn't unique to the city proles.
  Whether that becomes its own literal room/NPC, or whether it's handled some
  other way, is exactly the kind of design-pass decision this audit isn't
  positioned to make — but the *need* for some version of it is a finding, not a
  guess: an area whose whole premise is loss (of land, of water, of autonomy)
  without any warm counterweight is the one shape principle 10 explicitly rules
  out.

**Bottom line on principle 10**: not an obvious violator as a *premise* — the
game already sits at a comparable bleakness ceiling elsewhere and principle 10's
answer (obvious next move + a pressure valve) is a known, working pattern, not an
open problem. But it is a real design obligation the follow-up pass needs to
carry forward explicitly, not assume is inherited for free from Sector 9's pub.

## Finding 5: is "outside the Grid" the same idea as the Perimeter, an extension of it, or separate — a real position, not a dodge

`worldbuilding-ideas.md`'s "2. The Perimeter & Industrial Fringe (Sector 9
Outskirts)" describes "the fenced boundary separating Sector 9 from outer
manufacturing zones and agricultural communes... unmonitored prole housing where
citizens operate without formal dossiers." The future-features entry for "outside
the Grid" describes "a resource conflict between farmers/rural landholders and
whichever Ministry wants their land and water for AI data centers."

Taking a real position: **these are the same geographic idea at two different
altitudes, not two separate areas, and treating them as separate would be a
mistake worth naming now rather than after two areas get built that overlap.**
The Perimeter sketch is the *place* (fenced boundary, agricultural communes,
under-indexed housing); "outside the Grid" is the *conflict* that place would be
built to dramatize (the state's hunger for that place's land and water). A
Perimeter built without the AI-data-center land grab would be scenery with no
antagonist pressure on it — exactly the principle-1 risk in Finding 3, restated.
An "outside the Grid" conflict built without the Perimeter's already-sketched
texture (fenced boundary, unindexed housing, industrial fringe abutting
agricultural communes) would be reinventing a place this project has already
spent design time sketching, under a different name, with no crossreference.

The one place they might genuinely diverge: the Perimeter sketch's "outer
manufacturing zones" reads industrial (factories, fringe production), while
"outside the Grid" reads agrarian (farms, water rights) — the Ministry's hunger
for *industrial* land (to build data centers on) and its hunger for *water*
(to run them) could plausibly be dramatized in the same conflict without the
whole Perimeter needing to be farmland. That's a reason to treat "outside the
Grid" as the *sharpened, conflict-specific version* of the Perimeter concept
rather than a fully separate area needing its own independent geography — the
follow-up design pass should start from the Perimeter sketch and ask "what does
the data-center land grab do to this," not start from a blank page.

This matters for scope: if the follow-up design/build pass treats these as two
unrelated things, ADR 0020's two additions (a new in-Grid district, and "outside
the Grid") risk *accidentally* becoming three areas' worth of unindexed-rural
territory once someone eventually also picks up the Perimeter sketch on its own.
Naming the overlap now is cheap; discovering it after both get built independently
is not.

## What a lazy first draft of this area would get wrong, summarized

Pulling Findings 1–5 together into the single list the audit was asked for:

1. Ships a farming-sim verb set (`till`/`plant`/`water`/`harvest`) with no
   Exposure, record, or standing hooks — mechanically inert, a costume rather
   than a system (Findings 2, 3).
2. Voices rural NPCs as warm/folksy/plainspoken-safe, coding the countryside as
   an escape from the antagonist instead of another place it operates (Finding 2).
3. Builds a self-contained resource-management minigame (yields, seasons,
   weather) disconnected from Exposure/Influence — a second game grafted onto
   this one, ADR 0003's XP-and-levels rejection recurring in a new shape
   (Finding 2).
4. Treats "unmonitored/under-indexed" (correctly drawn from M2 and the Perimeter
   sketch) as an excuse for the area to have nothing for the game's actual
   systems to hook into, rather than finding the *different* mechanical
   expression of principle 1 that low-camera-density rural surveillance would
   actually take (record-vs-truth on land/water records, administrative stakes,
   informant betrayal) (Finding 3).
5. Ships without any version of a pressure valve, on the assumption Sector 9's
   pub or gallows humor covers an area whose whole premise is a different kind
   of loss (Finding 4).
6. Gets built as a geographically separate area from the Perimeter concept
   already sketched in `worldbuilding-ideas.md`, duplicating or contradicting
   that sketch instead of sharpening it (Finding 5).

None of these are inevitable. All six are avoidable with the same discipline
principle 9 already demands elsewhere in the project — they're listed here so
the follow-up design pass has them in view before the first room gets drafted,
the same function this doc's sibling research passes serve for their own
features.

## Open questions for Lauren

This is a survey, not a proposal to build — per ADR 0020, the next step (if this
reads as sound) is the still-open follow-up design pass for both of ADR 0020's
additions, not an ADR from this doc directly.

1. **Perimeter vs. "outside the Grid": confirm or reject the position in Finding
   5.** This doc's read is that they're the same idea at two altitudes (place vs.
   conflict) and the follow-up design pass should treat "outside the Grid" as a
   sharpened version of the Perimeter sketch rather than independent geography.
   If that's wrong, or if there's a reason to keep them formally separate (e.g.
   the Perimeter's industrial fringe and the farmland conflict end up needing
   genuinely different room graphs), that needs to be said before build work
   starts on either.
2. **Backstory/lore vs. actual playable area.** The original 2026-07-25 parking-
   lot entry flagged this explicitly and it never got resolved before ADR 0020
   scoped the idea in: does citizens *hear about* this conflict secondhand
   (newsfeeds, NPC dialogue, propaganda-engine bulletins — reusing ADR 0017's
   existing machinery, zero new geography), or does it become an actual walkable
   area with its own rooms? ADR 0020's language ("gated behind existing
   progression at its entry point") reads as assuming the playable-area answer,
   but the ADR itself doesn't rule on this explicitly and it's a materially
   different scope of work either way — worth confirming rather than inferring.
3. **If playable: which mechanical spine, concretely?** Finding 3 names
   record-vs-truth (land/water records) as the strongest candidate hook, with
   administrative small-verbs and non-lethal requisition/resettlement stakes as
   supporting texture, and flags a reshaped, lower-density expression of
   principle 3 (surveillance) as a real open design question rather than a
   solved one. Worth deciding this before any specific verb or room gets
   written, since it's the difference between "a new expression of principle 1"
   and "a farming sim with 2084 flavor text," per Finding 3's bottom line.
4. **What's this area's version of principle 10's pressure valve?** Finding 4
   argues the premise itself isn't disqualifying, but that it needs its own
   answer to "the pub is warm, gallows humor is canon" rather than inheriting
   Sector 9's by default — worth deciding whether that's a literal place, an
   NPC texture, or something else, as part of the same follow-up design pass.
