# In-Universe Artifacts: The Chalk Marks of Tunnel B

> *"they write it down. so can we."*  
> — Scratched into the lowermost brick of Tunnel B

In the damp service conduits beneath Tenement Row, where Ministry sensors cannot reach (Visibility 0), the Underground maintains its unsanctioned curriculum. Scratched in layers of chalk across the sweating brickwork of Tunnel B is a collective manual of resistance.

---

## Verbatim Text & Analysis

The chalk marks (`world/build.py`) contain sixteen distinct principles, each directly explaining an unsanctioned game verb or subterranean mechanic:

### 1. On Visibility & Sweeps
> *"sweeps can't reach where nothing watches. down here you are a rumor."*
* **Mechanical Counterpart**: Visibility 0 rooms exclude characters from sampled Watch sweeps ([ADR 0004](../../decisions/0004-surveillance-is-event-driven.md)).

### 2. On Forgery
> *"the file isn't you. a steady hand and a dead terminal can `forge` it. first try goes badly for most. so did yours."*
* **Mechanical Counterpart**: The `forge` verb permits off-the-books dossier modification in dead zones, training the Forgery skill but risking incident creation on failure.

### 3. On Bureaucratic Exploitation
> *"the broken screen on the alley stays broken because nobody files the form. remember what a form can do."*
* **Mechanical Counterpart**: Teaches that state maintenance is strictly form-driven; unsanctioned spaces persist because no form requested their repair.

### 4. On Heat Decay
> *"heat fades. sit. breathe. count the water drips. then go up and be boring."*
* **Mechanical Counterpart**: Time spent in low-visibility zones passively decays accrued Exposure.

### 5. On Circles & Organization
> *"alone you are a file. together you are a problem. draw a `circle`, down here, with people you'd go to the cells for."*
* **Mechanical Counterpart**: The `circle` suite (`form`, `invite`, `join`, `leave`) creates underground player cells in dead zones.

### 6. On Encrypted Communication
> *"pass word with `signal`. from quiet places only. walls have wires in them sometimes."*
* **Mechanical Counterpart**: `signal` broadcasts messages to circle members, safe when sent from dead zones but interceptable from monitored rooms.

### 7. On Informants & Reputation
> *"people on corners hear things. `recruit` them if you must, but `judge` them first, and learn to look before you trust the judging. not every ear is yours. some can be bought back (`flip`). none can be returned."*
* **Mechanical Counterpart**: Street vs. Ministry informants (`recruit`, `judge`, `flip`).

### 8. On Reading Citizens
> *"`judge` works on people too, not just ears, if you've looked long enough. a signed section c doesn't wash off just because they've found a new circle."*
* **Mechanical Counterpart**: Citizen reputation checks ([ADR 0010](../../decisions/0010-reputation-travels-judge-reads-citizens.md)) via `judge`.

### 9. On Honeypots
> *"the bolt-hole west of here has cots and a kettle. somebody keeps it nice. ask yourself who."*
* **Mechanical Counterpart**: Warns against the Bolt-Hole honeypot room.

### 10. On Sensor Sabotage
> *"every lens you `sabotage` is a street that forgets you. the crew fixes them oldest-first. so there is always work."*
* **Mechanical Counterpart**: `sabotage <device>` disables active sensors and pays Underground standing.

### 11. On Couriering & Papers
> *"the queue pays legs. `carry` for the broker, `deliver`, don't get checked. earn enough and she sells clean `papers`."*
* **Mechanical Counterpart**: Courier runs for the queue broker (`carry`/`deliver`) and purchasing clean papers for exposure relief.

### 12. On Subterranean Errands
> *"the lamp-mender has `errands` for careful people. do the first one. the last one is worth more than it pays."*
* **Mechanical Counterpart**: The lamp-mender's questline in Neon Alley.

### 13. On Black Market Gear
> *"the broker sells more than legs-work to people she knows. a coat that muffles. a pocket that lies. `list`, when your standing with the right people is more than nothing."*
* **Mechanical Counterpart**: Underground black market requisitions (foil-lined coats, dead-man pockets).

### 14. On Brick Stashes & Section C
> *"what a circle keeps, it keeps in a brick (`stash`), somewhere dark, once. choose the somewhere well, and remember when you sign anything: section c has an address line."*
* **Mechanical Counterpart**: Brick caches (`stash`) and the confiscation of circle stashes upon Section C betrayal.

### 15. On Joint Projects & Shared Stakes
> *"a circle that finishes something together is worth more than one of you talking. `circle project start`, when you're ready, and mean it: signing after the fact costs the whole circle the pot, not just you."*
* **Mechanical Counterpart**: Escalating circle projects ([ADR 0013](../../decisions/0013-escalating-circle-projects.md)) — cumulative solo sabotage and courier stages, then a synchronous two-member climax, paying underground standing only on completion and forfeiting the whole pot on a completed Section C confession.

### 16. On Underground Standing (`word`)
> *"no ledger holds what you're worth down here. ask with `word`, somewhere it's safe to ask. nobody writes down the answer either."*
* **Mechanical Counterpart**: Checking off-the-books Underground standing via `word` ([ADR 0009](../../decisions/0009-shadow-ladder-is-a-checkable-whisper.md)).

---

## Pedagogical Role

While the Ministry of Orientation Wing uses official placards to teach sanctioned mechanics, the Tunnel B chalk marks serve as the subterranean mirror—ensuring that every unsanctioned mechanic in *2084* is taught diegetically within the world ([contributing.md rule 9](../../engineering/contributing.md)).
