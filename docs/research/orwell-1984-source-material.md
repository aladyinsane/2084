# Nineteen Eighty-Four as source material

The most important research document in the repo. 2084 is *loosely* based on Orwell's
novel — this doc extracts the control mechanisms the novel describes and turns each one
into a design constraint. Everything in [../product/principles.md](../product/principles.md)
traces back to a mechanism catalogued here.

Source: the novel itself ([sources/orwell1984.pdf](sources/orwell1984.pdf)). Chapter
references are to Part.Chapter of the standard three-part structure.

## "Loosely based" is a legal position, not just a creative one

The novel is public domain in the UK/EU (Orwell died in 1950; life + 70 expired in 2021)
but remains under US copyright until **2044**. We are a US-based project. So:

- **Original setting and names.** The Grid, not Airstrip One. Our own ministries, our own
  figurehead, our own slogans. No Winston, no O'Brien, no Room 101, no "Big Brother is
  watching you."
- **Mechanisms, not expression.** Ideas (surveillance state, mutable history, language
  control) are not copyrightable; Orwell's specific characters, scenes, and wording are.
  We take the machinery, never the text.
- This is also creatively correct: a game set literally in Oceania is fan fiction with a
  compliance problem. A game about *how that kind of state works* is ours.

## The control mechanisms, and what each implies

### 1. Surveillance is asymmetric and intermittent

The telescreen's power isn't that it always watches — it's that you *can't know when* it
does (I.1). Citizens self-police because any moment might be observed.

**Design constraint:** surveillance should be probabilistic and opaque in the moment,
legible only afterward. An omniscient tracker that punishes every infraction instantly
produces frustration; a sampled check whose odds scale with how visible you've been
produces *dread*. The player's imagination does the work, exactly as in the novel.

### 2. Surveillance is unevenly distributed

The proles — 85% of the population — are barely watched at all (I.7). Scrutiny is a
function of proximity to power: Outer Party members live under the tightest watch.

**Design constraint:** visibility varies by district and by *standing*. Rising in the
regime buys access and privilege at the price of scrutiny; staying low buys freedom at
the price of poverty and irrelevance. That's a real tradeoff, and it's the spine of the
progression system. It also means new players (nobodies) naturally start in the
low-surveillance shallow end — the fiction and the difficulty curve agree.

### 3. Hierarchy is functional, not hereditary

The Party is explicitly not a hereditary aristocracy: Inner Party, Outer Party, and prole
status reflect function and aptitude, and the Party co-opts able proles rather than
letting talent accumulate outside it (II.9, Goldstein's book). What you *are* is what the
regime has recorded you as doing.

**Design constraint:** no races, no character classes. A character is an accumulating
record of actions — skills earned by use, standing granted (and revocable) by
institutions. This converges with what [third-millennium-mud.md](third-millennium-mud.md)
found independently in 1996, which is why we're confident in it.

### 4. The past is editable

Winston's job is rewriting old newspapers to match the present line; superseded versions
go down the memory hole (I.4). "Who controls the past controls the future: who controls
the present controls the past" (I.3). The regime's records *are* reality, because nothing
else persists.

**Design constraint:** records and memories are game objects that can be edited, forged,
and erased — with the truth/record distinction preserved internally. The gap between what
happened and what the record says happened is where the interesting gameplay lives.

### 5. Punishment is conversion, not martyrdom

The Party doesn't make martyrs. Victims are broken, made to genuinely recant, and only
then disposed of — or released, hollowed out (III.2). Death is the *least* of it.

**Design constraint:** character death is dramatically wrong for this setting. The
stakes that fit are detainment, interrogation, memory revision, loss of standing,
becoming an unperson. Non-lethal conflict isn't a softening compromise — it's fidelity.

### 6. Betrayal is the primary weapon

Parsons is denounced by his own children (III.1). The kindly junk-shop owner is Thought
Police; the safehouse is a honeypot (II.10). O'Brien spends years cultivating Winston's
trust in order to destroy him.

**Design constraint:** trust must be mechanically scarce and mechanically consequential.
Informants, double agents, and compromised safehouses need systemic support — any NPC
relationship should be *capable* of being a honeypot. Player cells that can fracture and
leak are more true to the source than guilds with a shared bank.

### 7. Small acts are transgressions

Keeping a diary is a capital crime (I.1). Walking alone, having a hobby, an unorthodox
facial expression — "ownlife" and "facecrime" are suspicious categories (I.8, II.5).

**Design constraint:** the interesting gameplay verbs are small. Writing something down,
being somewhere off your routine, saying slightly the wrong thing. A design where only
big dramatic actions carry risk has missed the novel's texture entirely.

### 8. Ritualized participation is mandatory

Two Minutes Hate, Hate Week, community-center evenings, Physical Jerks (I.1, I.4). Not
attending is itself a signal the regime reads.

**Design constraint:** scheduled world events where *absence is data*. This gives the
world a pulse (content on a timer) and makes even inaction a meaningful choice.

### 9. Language is a control surface

Newspeak shrinks the language so heretical thought becomes literally inexpressible
(Appendix). Doublethink lets citizens hold the official truth and the real one at once.

**Design constraint:** communication mechanics — coded speech, euphemism, what can be
said on monitored channels vs whispered — are rich territory. Also genuinely hard to
mechanize well. Parked, not dropped: see
[../product/future-features.md](../product/future-features.md).

## What we deliberately do not take

**The ending.** Orwell's thesis is that resistance fails — Winston loses completely, and
the boot stamps forever. That's the correct ending for a warning and a fatal one for a
game: players who cannot ever win, matter, or carve out space stop playing, and they're
right to. 2084 is a world where resistance is *dangerous and costly*, not *pointless*.
This is a deliberate infidelity to the source, chosen with our eyes open, and it's the
single biggest tonal decision in the project.

**The bleakness ceiling.** The novel is unrelentingly grim; a MUD is a place people
choose to spend evenings. We keep the dread and the moral weight; we do not simulate
despair so faithfully that logging in feels bad. Gallows humor, small victories, and the
proles' vitality (pub, songs, gossip — I.7's warmth is real) are the pressure valves the
novel itself provides.
