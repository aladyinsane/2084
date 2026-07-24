# 2084: World & Interaction Overview

A high-level summary of what *2084* is, how the player interacts with the world, and how its mechanics express the core dystopian setting.

---

## What 2084 Is

*2084* is a text-based MUD set in **Sector 9 of the Grid**, a totalitarian surveillance state loosely inspired by George Orwell’s *Nineteen Eighty-Four*. 

### Creative & Legal Position
*2084* operates under a distinct legal and creative framework ([research/orwell-1984-source-material.md](../research/orwell-1984-source-material.md)):
* **Original World & Names**: The Grid, Sector 9, the Central Spire, and original Ministries (Order, Records, Commerce) replace Airstrip One, Oceania, and Orwell's named characters.
* **Mechanisms over Expression**: The game adapts the control mechanisms of total surveillance, editable history, non-lethal conversion, and betrayal without reproducing Orwell’s specific text or characters.
* **Playable Agency**: Unlike Orwell’s novel, where resistance is strictly doomed, *2084* allows player resistance to matter. Oppression is the fiction, not the UX ([Principle 10](principles.md)).

---

## How Players Interact With the World

### 1. Surveillance & Visibility (`Vis` and `Exposure`)
The state is the primary antagonist ([Principle 1](principles.md)). The player’s location dictates their visibility level (0 to 5), shown in the prompt (`[G5 Vis:3 Exposure:12]`):
* **Watched Space (Vis 3–5)**: Moving through plazas or checkpoints raises **Exposure (`Exp`)**. Exposure is felt through prompt updates, lingering patrol visors, and cold NPC reactions.
* **Watch Sweeps**: Surveillance is sampled and probabilistic ([ADR 0004](../decisions/0004-surveillance-is-event-driven.md)). High exposure raises the odds of being selected during a Watch sweep.
* **Dark Zones (Vis 0–1)**: Low-surveillance areas (Tenement Row, Tunnel B) allow heat to decay over time and provide safe ground for unsanctioned actions.

### 2. The Dossier (Record vs. Truth)
There are no character classes or races ([ADR 0002](../decisions/0002-no-race-no-class.md)). A character is an accumulating **dossier** ([ADR 0005](../decisions/0005-records-are-objects.md)):
* **Audit Trail**: Infractions, sensor logs, missed assemblies, and commendations write to an append-only audit log.
* **Record Laundering**: Players can `petition` at the Archive Annex using Ministry standing to redact or amend entries, or risk illegal off-the-books `forge` attempts in dead zones.
* **Record Compaction**: Old routine incidents compact over time into summary counts ([ADR 0011](../decisions/0011-old-incidents-compact-the-file-forgets-faster-than-the-truth-does.md)), keeping `visible_count` (editable) separate from `true_count` (permanent).

### 3. Non-Lethal Stakes & Detention
There is no character death or lethal PvP ([ADR 0006](../decisions/0006-conflict-is-non-lethal.md)):
* High exposure or contraband checks lead to **detainment** in a Holding Cell.
* Detainment swaps the player's command set to `wait`, `demand`, or `confess`.
* Release resets exposure, suspends the player's assigned function, and annotates their dossier.

### 4. The Civic Order: Grades & Functions
* **Civic Grades**: Legible civil-service ranks from Grade 6 (probationary) down to Grade 1 (exemplary), computed dynamically from standing, errands, clearance, and function ([v0.12](roadmap.md)).
* **Work Assignments**: Reporting at the Assignment Hall assigns a **Function** (Clerk, Auditor, Steward). Working your post pays triple standing with the governing Ministry.
* **Civic Assemblies**: Scheduled world events where **absence is data** ([Principle 8](principles.md)). Active citizens must report to Unity Plaza; unexcused absence files an incident.

### 5. The Underground & Counter-Mechanics
Citizens seeking to operate outside state control interact with subterranean networks:
* **Circles & Signal**: Secret underground cells formed in dead zones (`circle form/invite/join/leave`) communicating via private `signal` calls.
* **Brick Stashes**: Cache contraband items in loose brick walls (`stash`).
* **Sabotage**: Target live sensors (`sabotage <device>`) to open temporary dark zones on monitored streets.
* **Couriering**: Accept contraband runs from the broker in the queue (`carry`/`deliver`), earning clean `papers` and underground standing (`word`).
* **Informants & Betrayal**: NPC informants (`recruit`, `judge`, `flip`) provide intelligence or report to the Ministry. Detained circle members face **Section C confessions**: confessing names grants immediate freedom while penalizing circle members (+25 exposure + dossier incident).
