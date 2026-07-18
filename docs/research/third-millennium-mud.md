# 3rd Millennium MUD (1996)

The named design inspiration for 2084's character system. This doc has two layers:
what remote sources say, and — since 2026-07-18 — **first-hand field research**: the MUD
is alive again, and we played it. A revival runs at `3m.vineyard.haus:3000` (classic
CircleMUD port; a modernized tbaMUD port runs on 3001). Our character: Fenwick, level 3,
10 lives intact. Full session log preserved; credentials in the repo-root dev-notes.

## What the remote sources say

From the [MudStats listing](https://www.mudstats.com/World/3rdMillennium) and confirmed
in-game:

- Founded **1996** by Mezrik; original run 1996–2006; revived December 2018 with the
  founder's blessing (per the in-game welcome room).
- Codebase: **CircleMUD 3.0, heavily modified** (the login screen credits it).
- Setting: year 3000. Time travel (~2050) broke civilization; its abuse tore the
  **Nexus** — a permanent spacetime distortion — into the world. Time travel was
  outlawed in 2099; the Nexus remains, and is now literally the game's hub room.
- The load-bearing line, displayed to every new character: *"The question of race and
  class has been eliminated. All men and women are created equal. We as individuals
  determine who we are and what we do."*

## Field findings (2026-07-18 expedition)

### 1. Chargen is classless and raceless — but not statless

Character creation, in full: name → password → gender (M/F) → **rolled stats**
(Str/Int/Wis/Dex/Con/Cha, rerollable) → email. No race question, no class question —
the 1996 claim is real. But note the nuance: they kept DIKU stat rolls. Classless
doesn't mean characterless; it means the *categories* are gone while the dials remain.
(2084 goes further — ADR 0002 derives everything from the record — but 3M shows the
minimum viable version shipped in 1996.)

Also noted honestly: the gender binary and some room text (an immortal's shrine
describes worshippers in terms that aged badly) are 1996 texture we observe and leave
behind.

### 2. The identity system is "skills as software," and it's the best thing in the game

Spells and skills don't exist by name. Instead:

- Everyone receives a **Neural-Link Interface** implant (price in the implant shop:
  **1 credit** — the "everyone is implanted at birth" lore is *mechanically enforced*
  by making it universally affordable).
- Abilities are **programs** you **download** into implant memory at the
  Bioprogramming Hall — a physical place, with category-specific store rooms
  (Health-1, Combat-2, Defensive-2…) each holding a Programming Device.
- Each download chunk costs **credits and a memory slot**; a program needs several
  chunks, shown as a progress bar (`sneak [********..]` — this is CircleMUD's practice
  percentage, re-skinned as download progress, and the re-skin genuinely reads better).
- Memory slots come from leveling (we had 3; spent all 3 on 80% of `sneak`). Scarcity
  makes "what do you know?" a real economic decision.
- A **Deprogramming Center** (wired chairs, ominous) will *delete* a program and refund
  its slots — for 150,000 credits against our starting 3,350. Unlearning exists and is
  deliberately much more expensive than learning.

### 3. Leveling is a place and a service, not an event

You don't "level up" — you walk to the Bioengineer's Laboratory and ask to be
**upgraded** (the NPC greets you by name; the first two upgrades are "complimentary").
Mana is **RAM**, and RAM/Energy/Health regen faster if you meditate. XP is awarded
**per blow struck, in real time, visible in the prompt** (`{35000 Lev}` ticking down
mid-fight) — you keep it even if you flee. Progression framed as biotech maintenance
turns a game abstraction into a *fictional errand*, and errands are content.

### 4. Death: 10 lives, an insurance salesman, and Purgatory

- Every character starts with **10 lives**. Death costs a life and some XP (equipment
  stays with you). At zero lives the character is **permanently deactivated**.
- You can **buy more lives from the Life Insurance Salesman** in the Metroplex.
- Death traps send your gear to a **Purgatory** maze, where you navigate to the Reaper
  partly by reading **notes left by previous players** — asynchronous player traces as
  a designed navigation mechanic, in 1996.
- The escape valves are generous: `/` recalls to the Nexus from anywhere *including
  mid-combat*, no XP loss; `wimpy` auto-flees you (it saved Fenwick at 6 HP from a
  training cyborg we shouldn't have picked a fight with).

The shape: **harsh stakes, purchased consent, soft edges.** Permadeath exists, but you
see it coming ten deaths away, you can buy distance from it, and the moment-to-moment
game hands you escape ropes. This is the consent-to-stakes lesson
([mud-design-landscape.md §4](mud-design-landscape.md)) implemented as an *economy*.

### 5. The tutorial is architecture

The Center of Higher Learning is a walkable manual: "Beginners Room – Stats" leads east
to "– Commands" to "– Eating & Drinking," looping back to the hub; an Advanced wing
mirrors it westward. Rooms *are* the help files. A Combat Training Hall full of
wandering, explicitly-labeled "Level 1/3/4 Training Cyborgs" gives safe practice with
difficulty printed on the target. The MOTD orders you to read three help files before
playing (`HELP NEWBIE`, `HELP DT`, `HELP LIVES`), and the newbie kit includes
protective signet rings and a free NPC healer by the hub.

### 6. The world is animated by its service layer

Metroplex Central at population ~1 (us) still felt inhabited, entirely because of
ambient civic NPCs: **patrolling security guards** ("…he is surrounded by a silver
globe!"), **cleaning droids** hunting garbage, a singing drunk, bioenhanced rats.
Shops have voice — *Needless Things* (junk), *Mercs-R-Us*, *The Flesh Mechanic*
(implants; the shopkeeper visibly stacked with defensive buffs, theft-deterrence worn
as flavor text). An ATM in a wall. A Jolt-cola fountain with free refills.

### 7. The cautionary finding: the reskin is skin-deep, and everyone can tell

The delivery fiction (downloads, RAM, upgrades) is superb — and then the program list
includes **`magic missile`, `chill touch`, `cure light`, `bless`**, and the Reaper
sells "elves' tear." Stock CircleMUD content bleeds straight through the sci-fi frame.
The current maintainers say so themselves on the in-game board: *"a lot of the 3m world
carries over from stock CircleMUD"* (Veekster, discussing whether to keep stock zones
as a tip of the cap). 3M renamed the *system* and kept the *content*; the seams show
everywhere, thirty years later, to a first-time visitor inside of an hour.

### 8. The empty world, observed from inside

`who` listed two AFK immortals ("Higher Beings") and Fenwick ("Lesser Beings": 1). The
Library board held 8 messages spanning years — including the founder's, in its
entirety: "Amazing work, guys!" The revival is lovingly maintained and almost empty.
Walking a city built for hundreds, alone, is the strongest argument for principle 8
we've encountered: nothing in the design failed, and the world is still a museum.

## What we take (updated)

1. **Classless works, and 2084's version goes deeper.** Confirmed shipping in 1996.
   3M kept rolled stats; we derive identity from the record instead (ADR 0002).
2. **Fiction-wrapped mechanics beat renamed mechanics — but only if the wrap goes all
   the way down.** "Download progress" for practice-% is brilliant; `magic missile` in
   the catalog undoes it. For 2084: no magic-missile moments — every default engine
   message, help text, and stock verb must pass through the fiction (principle 9 now
   says this explicitly).
3. **Services-as-places.** Upgrading at the Lab, downloading at the Hall, healing at
   the E.R., deleting at the Deprogramming Center: capabilities live at *addresses*,
   which makes geography meaningful and progression an errand through watched space —
   made for 2084, where going somewhere is what exposure taxes.
4. **Scarce memory + expensive deletion** is practically a 2084 mechanic already:
   aptitudes as record entries, deletion as a service someone else controls. Parked
   concretely in [future-features.md](../product/future-features.md) (deprogramming as
   re-education).
5. **Consent-to-stakes as an economy** (lives + insurance). 2084 has no death (ADR
   0006), but the pattern — catastrophe visible ten steps away, distance from it
   purchasable — maps onto detainment and record damage directly.
6. **Async player traces** (Purgatory notes, boards) — already on the roadmap (v0.3),
   now with 1996 precedent.
7. **Ambient civic NPCs are cheap liveness.** Patrols, cleaning droids, drunks: the
   city performs itself for an audience of one. Directly informs v0.2's patrol work.
8. **Design for the museum case.** Even revived and polished, 3M holds ~0 players.
   Small, dense, single-player-viable loops aren't a nice-to-have (principle 8); they
   are the difference between a game and an exhibit.

## What we don't take

- The time-travel/Nexus lore — wrong genre for us.
- Rolled stats, XP-per-damage, and the combat-centric core loop — replaced wholesale
  by ADR 0003's exposure/influence model.
- The gender binary and other 1996-era texture, noted above.

Sources: first-hand session at `3m.vineyard.haus:3000` (2026-07-18, session log
retained); [MudStats — 3rd Millennium](https://www.mudstats.com/World/3rdMillennium);
[Top Mud Sites — 3rd Millennium](https://www.topmudsites.com/forums/muddisplay.php?mudid=3M);
in-game boards and help files (`HELP NEWBIE`, `HELP DT`, `HELP LIVES`, `HELP PROGRAMS`).
