# 2084 Mechanics Design Document
**Working title:** 2084  
**Engine:** Evennia, Python, room-based MUD, text client

---

## Cover
**2084 Mechanics Design Document**  
Detailed mechanics implementing CircleMUD-style movement and combat while replacing XP and PvP with surveillance, influence, memory mechanics, and social systems.  
Author: design team / Lauren

---

## Table of Contents
1. [Design Goals and Constraints](#design-goals-and-constraints)
2. [Core Systems Overview](#core-systems-overview)
3. [Movement and World Model](#movement-and-world-model)
4. [Combat and Non-lethal Conflict](#combat-and-non-lethal-conflict)
5. [Surveillance and Exposure System](#surveillance-and-exposure-system)
6. [Influence and Reputation System](#influence-and-reputation-system)
7. [Memory Mechanics and Rewriting](#memory-mechanics-and-rewriting)
8. [Bureaucracy and Social Actions](#bureaucracy-and-social-actions)
9. [Data Models and Persistence for Evennia](#data-models-and-persistence-for-evennia)
10. [Commands, Prompts, and Examples](#commands-prompts-and-examples)
11. [Sample Quests and Events with Flowcharts](#sample-quests-and-events-with-flowcharts)
12. [Balancing Notes and Metrics](#balancing-notes-and-metrics)
13. [UX Onboarding and Player Flow](#ux-onboarding-and-player-flow)
14. [Prototype Roadmap and Testing Plan](#prototype-roadmap-and-testing-plan)
15. [Assumptions and Open Questions](#assumptions-and-open-questions)

---

## Design Goals and Constraints
**Goals**
- Preserve CircleMUD-style movement and feel.
- Replace XP/PvP with social systems: Influence, Reputation, Memory.
- Make surveillance a persistent, meaningful mechanic.
- Keep interactions text-first and low-latency.

**Constraints**
- Use Evennia's object model and command system.
- Keep server-side logic in Python modules.
- Avoid heavy real-time computations; prefer event-driven checks.

---

## Core Systems Overview
- **Movement**: Room-based, exits, door states, access checks.
- **Conflict**: Non-lethal, social, and stealth-based. Combat exists but is de-emphasized.
- **Surveillance**: Global visibility grid, sensor arrays, and exposure accumulation.
- **Influence**: Currency for progression and access.
- **Memory**: Objects representing memories that can be manipulated.
- **Bureaucracy**: Paperwork, permits, and procedural actions as gameplay.

---

## Movement and World Model
### Movement rules
- Standard CircleMUD commands: `n`, `s`, `e`, `w`, `u`, `d`, `enter <exit>`.
- Exits have metadata: `visibility_requirement`, `faction_access`, `exposure_modifier`.
- Movement triggers:
  - **Exposure check**: moving through high-visibility rooms increases Exposure.
  - **Sensor ping**: rooms with active sensors may log movement and create events.

### Example Evennia exit definition
```python
# Evennia-style pseudo-code
class SecureExit(DefaultExit):
    db.visibility_requirement = 2
    db.exposure_modifier = 5
    db.faction_access = ["Ministry of Order"]
    def at_traverse(self, traversing_object, target_location):
        traversing_object.scripts.get('exposure_script').add(self.db.exposure_modifier)
        super().at_traverse(traversing_object, target_location)
```

### Movement UX
- Prompt shows current room, visibility level, and Exposure.
- Example prompt:
```
[Central Spire Entrance] Vis:3 Exp:12 > 
```

---

## Combat and Non-lethal Conflict
### Philosophy
Combat exists but is framed as **confrontation** with social consequences. Lethal PvP is disabled by default. Conflicts resolve via a mix of stealth, tools, and social mechanics.

### Combat types
- **Physical confrontation**: brief, non-lethal, causes temporary penalties and Exposure.
- **Social confrontation**: debates, petitions, and public statements that change Reputation.
- **Hacking confrontation**: attempts to seize or corrupt data, affecting Memory objects and Influence.

### Combat flow (physical)
1. **Engage**: `attack <target>` or `subdue <target>`.
2. **Resolve**: Turn-based checks using attributes: `Stealth`, `Strength`, `Tech`, `Bureaucracy`.
3. **Outcome**: `Stunned`, `Detained`, `Fled`, or `Subdued`. Detainment triggers Memory scan.

### Example combat check (pseudo)
```python
# Pseudocode for a single attack resolution
attacker_roll = rand(1,20) + attacker.db.stealth
defender_roll = rand(1,20) + defender.db.awareness
if attacker_roll > defender_roll:
    defender.msg("You are subdued.")
    defender.db.status = "subdued"
    attacker.db.influence += 1
else:
    attacker.msg("Your attempt failed.")
    attacker.db.exposure += 2
```

---

## Surveillance and Exposure System
### Concepts
- **Exposure**: numeric value per player. Higher Exposure increases chance of Watch interactions.
- **Visibility**: per-room static value 0-5.
- **Sensor arrays**: dynamic objects that can increase visibility or create logs.

### Mechanics
- **Exposure accumulation**: actions add or subtract Exposure. Examples:
  - Passing a checkpoint: +1
  - Forging a document: +3
  - Memory rewrite attempt: +10
  - Using a sanctioned service: -2
- **Exposure decay**: Exposure decays slowly over time or via services.
- **Watch checks**: periodic checks sample players with probability proportional to Exposure.

### Watch check algorithm (concept)
- For each tick, sample players in a district.
- Probability of selection = `min(0.9, base_rate * (1 + Exposure/50))`.
- Selected players may face scans, fines, detainment, or memory audits.

---

## Influence and Reputation System
### Influence model
- **Influence** is a numeric ledger per player per faction.
- Influence is spent to gain **permits**, **rank**, and **services**.
- Influence sources: quests, favors, data sales, public statements, sanctioned work.

### Reputation vectors
- Stored as a dict: `{"Ministry of Order": {"trust": 10, "utility": 5, "exposure": 2}}`.
- Reputation affects NPC reactions, access checks, and event triggers.

### Example Influence transaction
```python
# Pseudocode
player.db.influence['Ministry of Order'] += 5
if player.db.influence['Ministry of Order'] >= 20:
    grant_rank(player, 'Order Associate')
```

---

## Memory Mechanics and Rewriting
### Memory object model
- Memory is a first-class object with fields:
  - `id`, `owner`, `origin`, `timestamp`, `confidence`, `tags`, `content`, `authenticity_score`
- Memories can be **attached** to players, NPCs, or rooms.

### Memory operations
- **Record**: create a memory object from an event.
- **Share**: transfer memory to another player or NPC.
- **Edit**: change `content` and adjust `authenticity_score`.
- **Erase**: remove memory from a player's accessible set but keep an audit trail.
- **Fabricate**: create a false memory with low authenticity.

### Memory rewriting service
- Performed by Memory Technicians or Ministry of Records.
- Costs Influence and increases Exposure.
- Rewrites adjust `confidence` and `authenticity_score`. Some memories are immutable without high-level clearance.

### Example Evennia memory model (pseudo)
```python
class Memory(DefaultObject):
    db.owner = None
    db.origin = None
    db.timestamp = None
    db.confidence = 100
    db.tags = []
    db.content = ""
    db.authenticity_score = 100

    def edit(self, editor, new_content, cost):
        if editor.pay_influence(cost):
            self.db.content = new_content
            self.db.authenticity_score -= cost * 2
            editor.db.exposure += cost
            return True
        return False
```

---

## Bureaucracy and Social Actions
### Paperwork as gameplay
- **Forms** are objects with fields and validation rules.
- Players can **fill**, **forge**, **submit**, and **appeal** forms.
- Bureaucratic success depends on `Bureaucracy` skill, Influence, and forged documents.

### Example form flow
1. Acquire form template from a kiosk.
2. Fill fields using `fill form <form_id> field:value`.
3. Submit with `submit form <form_id> to <office>`.
4. Office runs checks and returns `approved`, `rejected`, or `flagged`.

### Social actions
- `petition <target>`, `announce <message>`, `seed_rumor <topic>`.
- Social actions affect public metrics and can be amplified by NPC propagandists.

---

## Data Models and Persistence for Evennia
### Core Evennia objects
- **Rooms**: standard Evennia Room with additional attributes `visibility_level`, `sensor_ids`, `district`.
- **Exits**: extended with `exposure_modifier`, `access_requirements`.
- **Player (Account/Character)**: attributes:
  - `db.exposure` integer
  - `db.influence` dict per faction
  - `db.reputation` dict per faction with vectors
  - `db.memory_ids` list of Memory object dbrefs
  - `db.skills` dict
  - `db.status` flags
- **Memory**: separate Evennia Object type as shown above
- **Form**: object with schema and validation script
- **Sensor**: script or object that logs events and raises alerts

### Persistence notes
- Use Evennia Attributes for small fields and separate DB models for Memory objects if size grows.
- Index Memory objects by `owner` and `tags` for fast lookup.
- Use Evennia Scripts for periodic Watch checks and Exposure decay.
- Consider a separate Redis cache for hot Exposure values to reduce DB writes.

---

## Commands, Prompts, and Examples
### Movement and prompt
```
[Archive/ReadingRoom] Vis:2 Exp:8 Faction:Records> 
n
You pass through the scanner. A soft chime notes your ID.
```

### Example commands
- `n`, `s`, `e`, `w`, `enter <exit>`
- `attack <target>` or `subdue <target>`
- `hack terminal` or `hack <target>`
- `record memory "saw a ledger"` or `share memory <id> to <player>`
- `fill form <id> field:value`
- `submit form <id> to <office>`
- `petition <npc> for <request>`
- `forge document <template> with <skill>`

### Command examples with Evennia Command class snippet
```python
from evennia import Command

class CmdRecordMemory(Command):
    key = "record memory"
    locks = "cmd:all()"
    def func(self):
        content = self.args.strip()
        mem = create_object("typeclasses.memory.Memory", key="memory")
        mem.db.owner = self.caller
        mem.db.content = content
        mem.db.timestamp = time.time()
        self.caller.db.memory_ids.append(mem.dbref)
        self.caller.msg("Memory recorded.")
```

---

## Sample Quests and Events with Flowcharts
### Quest: "Ledger Retrieval" flow
1. **Trigger**: Broker offers mission.
2. **Infiltrate**: Enter Archive, pass a guard or bribe an Archivist.
3. **Extract**: Locate ledger, create memory object of ledger contents.
4. **Deliver**: Return to Broker or Collective.
5. **Outcome**: Influence awarded, Exposure change, memory fragment created.

### Event: "Audit Sweep"
- **Trigger**: Random or story-driven.
- **Effect**: Increased Watch checks, temporary sensor activation.
- **Player choices**: Hide, bribe, comply, or resist.
- **Consequences**: Detainment, fines, or reputation shifts.

---

## Balancing Notes and Metrics
### Key metrics to track
- **Average Exposure per player per hour**
- **Influence inflation rate**
- **Memory edits per session**
- **Number of detainments per day**
- **Faction rank progression speed**

### Balancing guidelines
- Keep Exposure decay slow enough to make choices meaningful but not punitive.
- Influence sinks: services, permits, memory rewrites to prevent inflation.
- Limit high-impact memory edits behind high Influence costs and exposure penalties.
- Use soft caps on faction ranks to encourage cross-faction play.

---

## UX Onboarding and Player Flow
1. **Narrative intro**: 2-3 lines of scene setting.
2. **Role selection**: concise descriptions and starting stats.
3. **Guided tasks**: obtain ID, pass checkpoint, record first memory.
4. **First social choice**: small quest that seeds faction reputation.
5. **Help system**: `help codex`, `help commands`, `help memory`.

---

## Prototype Roadmap and Testing Plan
**Sprint 1**: Movement, rooms, exits, basic prompt, role selection. Test movement and prompt clarity.  
**Sprint 2**: Exposure system, sensors, Watch checks. Playtest for fairness and frequency.  
**Sprint 3**: Memory object model, record/share/edit operations. Test persistence and audit trails.  
**Sprint 4**: Influence economy, forms, and bureaucracy. Balance sinks and progression.  
**Playtests**: Small closed groups focusing on social mechanics, then larger stress tests.

---

## Assumptions and Open Questions
**Assumptions**
- Evennia is available and familiar to the team.
- Memory objects can be stored as Evennia Objects or in a separate DB table.
- No lethal PvP by default.

**Open Questions**
- Should memory authenticity be visible to players or only to certain NPCs?
- How granular should Exposure be across districts?
- Do you want cross-server persistence for memory archives?

---

## Iterations

### Iteration 1 — Draft mechanics
- Implemented movement, basic Exposure, and Memory object concept.
- Combat minimal and non-lethal.
- Basic Evennia pseudo-code included.

### Iteration 2 — Refinement
- Added Influence ledger, reputation vectors, and bureaucracy flows.
- Introduced Watch check algorithm and Exposure decay.
- Expanded command examples and Evennia snippets.

### Iteration 3 — Balance and Playability
- Added balancing metrics and influence sinks.
- Clarified Memory edit costs and consequences.
- Added onboarding flow and prototype roadmap.

### Final Polished Mechanics Doc
- Consolidated all iterations into the sections above.
- Cleaned code snippets and added concrete Evennia object attributes.
- Included explicit testing metrics and playtest plan.

---

## Cross-references
- See `2084_Codex.md` for lore, factions, and sample quests referenced in this document.
- Memory object model in this doc maps to the Codex's Memory section.