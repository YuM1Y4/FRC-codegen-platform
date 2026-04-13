# FRC Codegen Platform Context

## Goal

Build a cross-season FRC codegen platform that can assemble a complete WPILib Java robot codebase from reusable skills, templates, scripts, and references.

This project is not for maintaining a single competition repository. It is for building a reusable system that helps generate and extend future season codebases faster and more consistently.

## Core Idea

Use four layers together:

- `skills/` for workflows, rules, and trigger descriptions
- `assets/` for starter repos, code templates, and scaffolds
- `scripts/` for deterministic assembly and file rewriting
- `references/` for team architecture conventions and implementation guides

The platform should support composing multiple skills into one complete robot project rather than relying on one giant monolithic skill.

## Design Principles

- Separate cross-season architecture from season-specific game logic.
- Encode team-specific conventions, not generic FRC knowledge.
- Keep each skill narrow enough to be reusable, but broad enough to remove repeated setup work.
- Prefer lean `SKILL.md` files and move details into `references/`.
- Use `scripts/` when the same code transformation would otherwise be rewritten repeatedly.
- Use `assets/` for starter code and module templates that should be copied or adapted.

## Recommended Skill System

### Foundation Skills

- `frc-season-assembler`
  Create a new season project and compose the chosen modules into a starting codebase.
- `frc-java-architecture`
  Define the team's standard WPILib command-based project structure and coding patterns.
- `frc-match-validation`
  Run build, sim, and sanity checks before code is considered ready.

### Capability Skills

- `frc-swerve-drive`
  Provide drivetrain structure, tuning surfaces, and control conventions.
- `frc-mechanism-scaffold`
  Add a new mechanism with standard subsystem, commands, constants, and ports wiring.
- `frc-vision-limelight`
  Integrate Limelight-based aiming, targeting, and pose estimation patterns.
- `frc-auto-choreo`
  Integrate Choreo files, auto routine wiring, and path naming conventions.

### Season Packs

- `frc-2026-gamepack`
- `frc-2027-gamepack`

Each gamepack should only contain season-specific scoring logic, field landmarks, state machines, and autonomous strategy patterns.

## Stable vs Seasonal Split

### Stable Across Seasons

- WPILib Java project structure
- command/subsystem/container boundaries
- constants and ports organization
- swerve architecture
- controller binding patterns
- validation workflow
- logging and debug conventions

### Seasonal

- game mechanism behavior
- scoring workflows
- field geometry and landmarks
- autonomous routines and strategy
- season-specific superstructure state machines

## Initial Scope

Start with these two skills first:

1. `frc-season-assembler`
2. `frc-java-architecture`

Do not try to fully build all capability skills at once. First prove that a new project can be assembled with the standard architecture and validation flow. Then split out the more specialized skills.

## Suggested Repository Layout

```text
FRC-codegen-platform/
  PROJECT_CONTEXT.md
  skills/
    frc-season-assembler/
    frc-java-architecture/
    frc-match-validation/
    frc-swerve-drive/
    frc-mechanism-scaffold/
    frc-vision-limelight/
    frc-auto-choreo/
    frc-2026-gamepack/
  templates/
    wpilib-java-base/
    modules/
  scripts/
    new_project.py
    add_mechanism.py
    wire_bindings.py
  references/
    architecture-principles.md
    naming-conventions.md
    validation-checklist.md
```

## First Deliverables

- Define the boundary and responsibility of `frc-season-assembler`.
- Define the boundary and responsibility of `frc-java-architecture`.
- Decide what belongs in `templates/` versus `skills/`.
- Draft the first starter project template.
- Draft one sample mechanism scaffold.
- Define the minimum validation workflow for generated codebases.

## Examples of Desired User Requests

- "Use $frc-season-assembler to create a new WPILib Java robot project with our standard architecture."
- "Use $frc-java-architecture to reorganize this robot repo into our command-based structure."
- "Use $frc-mechanism-scaffold to add a shooter subsystem with commands, constants, and ports."
- "Use $frc-auto-choreo to wire a new Choreo auto into the project."
- "Use $frc-match-validation to sanity check the generated project before we continue."

## Suggested Next Conversation Prompt

Use this prompt in a new thread opened from this directory:

```text
We are building a cross-season FRC codegen platform rather than maintaining a single-season robot repo. Start by designing the first two skills, frc-season-assembler and frc-java-architecture, including their responsibilities, folder layout, and what should live in skills, templates, scripts, and references.
```
