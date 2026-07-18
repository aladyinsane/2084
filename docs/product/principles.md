# Product Principles

These exist to be *used in arguments*. When a feature idea arrives, it gets checked
against this list; a principle that never rejects anything is a slogan. Each one traces
to a specific finding in [../research/](../research/) — mechanisms cited as "M1"–"M9"
refer to [orwell-1984-source-material.md](../research/orwell-1984-source-material.md).

---

## 1. The world is the antagonist

The player's enemy is the state — its sensors, clerks, patrols, records, and rituals —
not a bestiary and not other players. Content effort goes into making the regime feel
present, reactive, and inescapable.

*Because:* the original brainstorm's strongest line, and the novel's whole architecture.
A dystopian MUD where you grind mobs is "1984 with swords," which we are explicitly not.

**Test:** does this feature make the state more *present* — or just the player stronger?

## 2. You are what you do

No races. No classes. A character is an accumulating record: skills that grow by use,
standing that institutions grant and revoke, a reputation that follows behavior. The
regime may stamp a *function* on you; the stamp is data, not a database column.

*Because:* 3rd Millennium proved the design in 1996; the Party's functional hierarchy
(M3) demands it. Known classless failure mode — build convergence — gets active
mitigation, not hope ([mud-design-landscape.md §2](../research/mud-design-landscape.md)).

**Test:** can two characters created identically become, through play alone, people the
world treats completely differently?

## 3. Surveillance is dread, not damage

Being watched is probabilistic, unevenly distributed, and opaque in the moment — but
always legible in trend. Rising exposure is *felt* (prompt, NPC behavior, patrol
density) before it ever lands. Certain in direction, uncertain in timing: that's the
telescreen (M1, M2), and it's also the fairness bar harsh games must clear
([mud-design-landscape.md §4](../research/mud-design-landscape.md)).

**Test:** did a player change their route because of what *might* be watching? And when
the hammer fell, could they truthfully say they saw it coming?

## 4. The record is not the truth

What happened and what the record says happened are separate game states, and the gap
between them is playable. Records can be edited, forged, and erased; the truth persists
underneath, in an audit trail and in what characters saw (M4).

**Test:** can the player point at a specific lie in the record and know how it got there?

## 5. Stakes are conversion, not death

The regime doesn't make martyrs (M5). The catastrophic outcomes are detainment,
interrogation, memory revision, demotion, unpersoning. Death would be a *mercy* — so
it's off the table, and lethal PvP with it.

**Test:** is the worst thing on the table something a character might rationally fear
more than dying?

## 6. Trust is the scarcest currency

Any relationship must be capable of being a honeypot (M6). Informants, double agents,
and cells that fracture need systemic support. The deepest wound available in the game
should be betrayal, and it should be player-reachable without any combat system at all.

**Test:** can a betrayal hurt more than any weapon in the game?

## 7. Small verbs carry weight

Writing something down, loitering, missing an assembly, saying the slightly wrong thing
on a monitored channel — one-command actions with real consequence (M7, M8). If risk
only attaches to heists and hacking, we've missed the novel's texture.

**Test:** name the single-command action this feature makes meaningful.

## 8. Alive at three players

Every core loop works with one player online; the world generates pressure via NPCs,
scheduled events, and the traces other players leave behind. Geography stays small and
dense so the players who *are* online collide.

*Because:* the empty-world problem is the leading cause of MUD death, including our own
inspiration's ([mud-design-landscape.md §1](../research/mud-design-landscape.md),
[third-millennium-mud.md §3](../research/third-millennium-mud.md)).

**Test:** is this feature still fun tonight, alone, at 1 a.m.?

## 9. Familiar shell, alien contents

A 1996 MUD veteran's fingers should just work: `n`, `s`, `look`, `say`, the prompt.
Everything *behind* the prompt — progression, stakes, what the numbers mean — is
different. (Which is, not incidentally, the texture of the setting itself.)

*Because:* 3rd Millennium kept the CircleMUD chassis while gutting the organs, and
Evennia gives us the chassis for free
([evennia-capabilities.md](../research/evennia-capabilities.md)).

**Test:** can a MUD veteran get from login to their first mistake without a help file?

## 10. Oppression is the fiction, not the UX

The world is grim; *playing* must not be. Dread, yes; tedium and despair-spirals, no.
New players start as nobodies in the barely-watched shallows (the fiction and the
difficulty curve agree — M2). After every catastrophe the player has an obvious,
interesting next move. The proles' pub is warm, and gallows humor is canon.

*Because:* the novel's ending is correct for a warning and fatal for a game — our one
deliberate infidelity, chosen in
[orwell-1984-source-material.md](../research/orwell-1984-source-material.md).

**Test:** after the worst outcome the game can inflict, does the player log back in
tomorrow — and is that a rational choice?

---

## Anti-principles: things we are deliberately not

- **Not a combat MUD.** Confrontation exists, subordinate to social and stealth play.
  Players who want a fighting game should be told, kindly, where to find one.
- **Not a faithful adaptation.** Loosely based, legally and creatively: our own names,
  our own city, and — unlike Orwell — resistance that can matter (principle 10).
- **Not permadeath-hardcore.** Harsh loss without consent kills retention; our stakes
  telegraph, and the truly irreversible is reserved and rare.
- **Not a big world.** Rooms are added when population justifies them, never because
  building is fun.
- **Not staff-policed roleplay.** Mechanics carry the tone (monitored channels raise
  exposure; the game reacts to your record). Mechanics are the staff that never sleeps.
