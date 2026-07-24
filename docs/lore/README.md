# 2084 Lore & World Archive

This directory contains the narrative background, in-universe artifacts, and worldbuilding documentation for *2084*.

---

## Contents

| Document | What's in it |
|---|---|
| [historical-background.md](historical-background.md) | The narrative history of Sector 9, the Three Ministries, the Spire, the Civic Machine, and the Underground |
| [artifacts/forms-and-notices.md](artifacts/forms-and-notices.md) | In-universe documentation of state forms (Form 1-A, Form 2-B, Form 9-A, Form 12-D, Form C-1, Form 77, Section C) |
| [artifacts/the-chalk-marks.md](artifacts/the-chalk-marks.md) | Complete transcript and textual analysis of the subterranean Tunnel B chalk curriculum |
| [artifacts/apparatus-and-requisitions.md](artifacts/apparatus-and-requisitions.md) | In-universe catalogue of state surveillance equipment and black-market contraband gear |

---

## Lore Alignment & Maintenance Mechanism

To ensure that the world narrative stays strictly aligned with game mechanics as *2084* evolves, all design and implementation work must follow this **Lore Maintenance Protocol**:

### 1. The Lore-Code Parity Rule
*(Extends [contributing.md rule 9](../engineering/contributing.md))*

Every feature added to the codebase that introduces a user-facing form, NPC line, room placard, state issue item, or subterranean chalk line **MUST** be paired with an update to the corresponding lore document in `docs/lore/`.

```
 Code Addition (world/ or commands/)
       |
       +---> Curriculum Update (Orientation Placards or Chalk)
       |
       +---> Lore Registry Update (docs/lore/artifacts/)
```

### 2. Lore Audit Checklist for Pull Requests
Before any feature PR is merged into `main`, check:
- [ ] **Sanctioned Verbs / State Forms**: Are any new forms added to `world/form_c1.py` or `commands/` documented in `docs/lore/artifacts/forms-and-notices.md`?
- [ ] **Unsanctioned Verbs / Underground Markings**: Are any new chalk lines in `world/build.py` analyzed in `docs/lore/artifacts/the-chalk-marks.md`?
- [ ] **Equipment & Devices**: Are new state-issued items or black-market gear catalogued in `docs/lore/artifacts/apparatus-and-requisitions.md`?
- [ ] **Historical Parity**: Does `docs/lore/historical-background.md` reflect any fundamental mechanical additions to the state or underground economy?

---

## In-Universe Artifact Registry

| In-Game Artifact | Primary Code Implementation | Lore Reference Document |
|---|---|---|
| **Notice of Arrival (Form 1-A)** | [commands/firsthour.py](../../game/commands/firsthour.py) | [forms-and-notices.md](artifacts/forms-and-notices.md#form-1-a) |
| **Citizen Advisory (Form 2-B)** | [commands/firsthour.py](../../game/commands/firsthour.py) | [forms-and-notices.md](artifacts/forms-and-notices.md#form-2-b) |
| **Civic Reclassification (Form 9-A)** | [world/grades.py](../../game/world/grades.py) | [forms-and-notices.md](artifacts/forms-and-notices.md#form-9-a) |
| **Entitlements Notice (Form 12-D)** | [commands/detention.py](../../game/commands/detention.py) | [forms-and-notices.md](artifacts/forms-and-notices.md#form-12-d) |
| **Clearance Application (Form C-1)** | [world/form_c1.py](../../game/world/form_c1.py) | [forms-and-notices.md](artifacts/forms-and-notices.md#form-c-1) |
| **Employment Verification (Form 77)** | [world/form_c1.py](../../game/world/form_c1.py) | [forms-and-notices.md](artifacts/forms-and-notices.md#form-77) |
| **Confession Form (Section C)** | [commands/circles.py](../../game/commands/circles.py) | [forms-and-notices.md](artifacts/forms-and-notices.md#section-c) |
| **Tunnel B Chalk Marks** | [world/build.py](../../game/world/build.py#L562-L616) | [the-chalk-marks.md](artifacts/the-chalk-marks.md) |
| **Orientation Placards** | [world/build.py](../../game/world/build.py#L159-L257) | [historical-background.md](historical-background.md#ii-the-civic-machine) |
| **Surveillance Lenses & Sensors** | [typeclasses/objects.py](../../game/typeclasses/objects.py) | [apparatus-and-requisitions.md](artifacts/apparatus-and-requisitions.md#surveillance-apparatus) |
| **State Badges & Wellness Monitors** | [typeclasses/gear.py](../../game/typeclasses/gear.py) | [apparatus-and-requisitions.md](artifacts/apparatus-and-requisitions.md#state-issue-gear) |
| **Foil Coats & Dead-Man Pockets** | [typeclasses/gear.py](../../game/typeclasses/gear.py) | [apparatus-and-requisitions.md](artifacts/apparatus-and-requisitions.md#black-market-gear) |
