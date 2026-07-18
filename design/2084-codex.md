# 2084 Codex
**Working title:** 2084  
**Preference noted:** Use the term **Codex** instead of Bible

---

## Cover
**2084 Codex**  
A world codex for a text-based dystopian MUD inspired by 1984.  
Author: design team / Lauren (project lead)  
Engine: Evennia, Python, room-based text client

---

## Table of Contents
1. [Overview and Purpose](#overview-and-purpose)
2. [Lore and Setting](#lore-and-setting)
3. [Factions and Power Structures](#factions-and-power-structures)
4. [Key Locations](#key-locations)
5. [NPC Archetypes](#npc-archetypes)
6. [Player Roles and Archetypes](#player-roles-and-archetypes)
7. [Progression and Social Systems](#progression-and-social-systems)
8. [Memory, Surveillance, and Influence](#memory-surveillance-and-influence)
9. [Sample Quests and Events](#sample-quests-and-events)
10. [UX Onboarding Flow](#ux-onboarding-flow)
11. [Roadmap and Playtest Plan](#roadmap-and-playtest-plan)
12. [Assumptions and Open Questions](#assumptions-and-open-questions)

---

## Overview and Purpose
The **2084 Codex** is the canonical design reference for the MUD world. It defines tone, history, institutions, and the social mechanics that replace traditional XP and PvP. The Codex is a living document intended to guide writers, builders, and scripters.

---

## Lore and Setting
### High-level premise
A near-future technocratic state has consolidated power through pervasive surveillance, bureaucratic ritual, and memory engineering. Citizens live in layered districts, each with different levels of visibility and privilege. The state is not monolithic; competing ministries and corporate factions vie for influence.

### Historical timeline (short)
- **Pre-2028:** Tech consolidation and corporate-state partnerships.
- **2035:** The Surveillance Charter codified.
- **2048:** Memory Rewriting Act passed.
- **2084:** Present day. The city-state known as the Grid is governed by ministries, corporations, and the Watch.

### Tone and themes
- Oppressive bureaucracy and ritualized compliance
- The fragility of truth and memory
- Social engineering as progression
- Moral ambiguity and survival through influence

---

## Factions and Power Structures
### Major factions
- **Ministry of Order**: Enforces laws, runs the Watch, controls public surveillance.
- **Ministry of Records**: Manages archives, identity verification, and memory services.
- **Ministry of Commerce**: Corporate liaison, rationing, and resource allocation.
- **The Collective**: Underground network of dissidents, memory archivists, and black-market hackers.
- **Private Corporations**: Provide tech, memory hardware, and "sanitization" services.

### Faction mechanics (summary)
- Factions grant **influence** rather than XP.
- Influence unlocks access, privileges, and bureaucratic rank.
- Faction reputation is multi-dimensional: **Trust**, **Utility**, **Exposure**.

---

## Key Locations
### The Grid (city overview)
- **Central Spire**: Ministry hubs and Watch headquarters.
- **Archive District**: Ministry of Records, public archives, memory clinics.
- **Market Belt**: Commerce, black markets, corporate showrooms.
- **Lower Rings**: Dense residential zones with limited access and heavy surveillance.
- **Subterranean**: Collective safehouses, abandoned tunnels, illegal servers.

### Example rooms (short)
- `CentralSpire/Entrance` — grand checkpoint, scanners, queue.
- `Archive/ReadingRoom` — public terminals, restricted stacks.
- `Market/NeonAlley` — vendors, data brokers, rumor-mongers.
- `Subway/TunnelB` — low light, hidden caches, Collective contact.

---

## NPC Archetypes
- **Watch Patrol**: Routine enforcers, high detection, low nuance.
- **Archivist**: Gatekeepers of records, can verify or redact identity fragments.
- **Memory Technician**: Performs memory edits, sells implants, can be bribed.
- **Bureaucrat**: Controls permits, issues fines, can be influenced with paperwork.
- **Broker**: Black-market vendor for influence, forged documents, and memory fragments.
- **Propagandist**: Spreads state narratives, can alter public opinion metrics.

Each archetype has a short stat block: **Detection**, **Influence**, **Corruption**, **MemoryAccess**, **Combat**.

---

## Player Roles and Archetypes
Players choose a role that shapes starting resources and mechanics. Roles are social archetypes rather than combat classes.

- **Clerk**: Bureaucratic operator, excels at paperwork, forging, and social manipulation.
- **Technician**: Hacking and memory engineering specialist.
- **Courier**: Mobility and stealth expert, excels at moving items and information.
- **Archivist-Acolyte**: Access to records, can read and sometimes restore memories.
- **Operative**: Trained in stealth and close-quarters conflict, useful for extraction and sabotage.
- **Citizen**: Flexible starter with balanced social skills.

Each role has **starting influence**, **visibility**, **memory stability**, and **toolkit**.

---

## Progression and Social Systems
### Influence instead of XP
- **Influence** is the primary progression currency.
- Earned by completing social objectives, manipulating records, gaining allies, and performing sanctioned tasks.
- Influence unlocks **ranks** within factions, access to restricted rooms, and social privileges.

### Reputation vectors
- **Trust**: How much a faction or NPC believes you.
- **Utility**: How useful you are operationally.
- **Exposure**: How visible you are to the Watch.

Progression is non-linear and social. Players trade influence for access, favors, and memory services.

---

## Memory, Surveillance, and Influence
### Memory mechanics (narrative)
- Memories are modular objects that can be **recorded**, **shared**, **edited**, **erased**, or **fabricated**.
- Memory fragments are game objects with metadata: `origin`, `timestamp`, `confidence`, `tags`.
- Memory rewriting is a service provided by Memory Technicians and the Ministry of Records.

### Surveillance mechanics
- Surveillance is a persistent world state. Rooms and districts have **visibility levels** and **sensor arrays**.
- Player actions can increase or decrease exposure. Exposure affects random checks, NPC behavior, and access.

### Social engineering
- Influence actions include **petitioning**, **forging**, **public statements**, and **rumor seeding**.
- Social actions have cooldowns and risk of exposure.

---

## Sample Quests and Events
### Quest: "The Missing Ledger"
- **Hook**: A clerk asks the player to retrieve a ledger from the Archive.
- **Objectives**: Infiltrate Archive, bypass bureaucratic checks, extract ledger, deliver to Broker.
- **Mechanics**: Use forged paperwork, bribe an Archivist, or steal via stealth.
- **Consequences**: Ledger reveals a memory rewrite program. Delivering to Collective increases Trust with Collective but raises Exposure.

### Event: "Public Purge"
- A timed city-wide audit increases Watch patrols and forces players to hide or risk memory scans. Rewards for surviving with low Exposure.

---

## UX Onboarding Flow
1. **Intro vignette**: Short narrated scene establishing tone and stakes.
2. **Role selection**: Choose role with short mechanical summary.
3. **Tutorial district**: Guided tasks: obtain ID, pass a checkpoint, perform a simple influence action.
4. **First choice**: Side with a faction or remain independent. Choice seeds early reputation vectors.
5. **Sandbox**: Open to core districts with suggested objectives.

---

## Roadmap and Playtest Plan
- **Prototype 0.1**: Core rooms, role selection, basic movement, simple influence actions.
- **Prototype 0.2**: Memory objects, Archive interactions, faction reputation.
- **Alpha**: Full surveillance model, memory rewriting, sample quests.
- **Playtests**: Closed sessions focusing on social systems, balancing influence economy, and onboarding clarity.

---

## Assumptions and Open Questions
**Assumptions**
- Evennia backend, Python modules, room-based world, text client.
- No real-time voice or graphical UI required.
- Memory objects are stored as Evennia Attributes or separate DB models.

**Open Questions**
- Should memory edits be reversible by players or only by NPC services?
- How punitive should Exposure be for new players?
- Do you want PvP at all, even as social PvP like reputation attacks?

---

## Cross-references
- See [Progression and Social Systems](#progression-and-social-systems) for how Influence ties to factions.
- See [Memory, Surveillance, and Influence](#memory-surveillance-and-influence) for data model suggestions referenced in the Mechanics Design Document.
