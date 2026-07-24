# In-Universe Artifacts: Surveillance Apparatus & Requisitions

> *"The lens does not judge; it collects. The record does the judging."*  
> — Ministry of Order Maintenance Manual, Item 44-B

---

## I. Surveillance Apparatus

Sector 9 is outfitted with state surveillance hardware designed to maintain continuous event-driven observation ([ADR 0004](../../decisions/0004-surveillance-is-event-driven.md)).

### 1. Watchscreens
* **Description**: Multi-story or wall-mounted municipal screens cycling Ministry directives and production figures.
* **Integrated Hardware**: Beneath or above each screen sits an unblinking lens array focused outward at the crowd rather than the display.
* **Locations**: Assignment Hall, Unity Plaza, Neon Alley (broken).

### 2. Scanner Arrays
* **Description**: High-surveillance black glass domes mounted on articulated tracks at sector chokepoints.
* **Operation**: Tracks citizens in smooth, silent arcs. Features green diode status rows.
* **Locations**: Central Spire Checkpoint (Vis 5). Adds direct entry exposure modifiers to characters traversing the gate.

### 3. Reading-Desk Monitors
* **Description**: Slim cameras mounted on articulated brass arms above public reading terminals at the Archive Annex.
* **Operation**: Positioned to observe citizen expressions and reading habits rather than terminal screens. Formally inscribed: *FOR YOUR SECURITY AND CONVENIENCE*.

### 4. Demonstration Lens Arrays
* **Description**: Ranks of polished, numbered lenses in the Orientation Demonstration Corridor (Vis 5).
* **Pedagogical Purpose**: Designed to artificially raise citizen Exposure on entry so citizens learn the physical feeling of high surveillance.

### 5. Concealed Hairline Seams
* **Description**: Secret, re-pointed conduit seams concealing miniature live sensors.
* **Locations**: Installed in state honeypots like **The Bolt-Hole**. Invisible to basic observation; surfaceable only at high Observation skill.

---

## II. State-Issued Gear

Citizens may purchase state-sanctioned equipment at the Assignment Hall Requisitions Window (`requisitions.py`, `typeclasses/gear.py`). Every purchase is logged into the citizen's file.

### 1. The Citizen Badge
* **Slot**: Badge / Chest
* **Effect**: Increases standing payouts from counter shifts and improves clerk demeanor in watched rooms.
* **Lore Framing**: A laminated municipal badge confirming visible alignment with state institutions.

### 2. The Wellness Monitor
* **Slot**: Wrist / Cuff
* **Effect**: Accelerates Exposure heat decay, but logs citizen movements twice as easily in sensor audit trails.
* **Lore Framing**: A state-issued wrist monitor marketed under public safety and health management.

---

## III. Underground Black-Market Gear

Citizens holding high Underground standing (`word`) gain access to the queue broker's secondary stock.

### 1. The Foil-Lined Coat
* **Slot**: Torso / Outerwear
* **Effect**: Reduces Exposure accrued upon entering high-visibility rooms, though civic clerks view the garment with suspicion.
* **Lore Framing**: A heavy, worn coat lined with discarded industrial foil that dampens electronic scanner reflection.

### 2. The Dead-Man Pocket
* **Slot**: Accessory / Concealed
* **Effect**: Absorbs one contraband search during a scanner or patrol frisk before being destroyed.
* **Lore Framing**: A false-bottom pouch stitched into inner lining, designed to disintegrate or misdirect scanner beams during pat-downs.
