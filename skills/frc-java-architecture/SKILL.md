---
name: frc-java-architecture
description: Establish or refactor a WPILib Java command-based project into the team's standard architecture. Use when a user wants to clean up project structure, separate robot control flow from subsystem logic, or move an existing repo toward the shared cross-season layout.
---

# frc-java-architecture

Use this skill when the user wants structure, boundaries, and consistency inside an existing or newly created Java robot project.

## Responsibilities

- keep `Robot` thin and scheduler-focused
- centralize subsystem ownership and trigger wiring in `RobotContainer`
- organize domain code under `commands`, `subsystems`, and `constants`
- preserve the stable vs seasonal split from `../../references/architecture-principles.md`
- apply naming and folder conventions from `../../references/naming-conventions.md`

## Boundaries

This skill owns:

- package layout and file placement
- command/subsystem/container responsibilities
- constants and ports organization
- migration planning for architecture cleanup

This skill does not own:

- deciding match strategy unless required for a refactor
- inventing new mechanism behavior without a separate request
- replacing validated subsystem algorithms just to fit a prettier layout

## Workflow

1. Inspect the current repo before editing. Identify where `Robot`, bindings, commands, constants, and hardware access are mixed together.
2. Read `../../references/architecture-principles.md` and `../../references/naming-conventions.md`.
3. Use `../../templates/wpilib-java-base/` as the target shape and `../../templates/modules/basic-mechanism/` as the pattern for new mechanisms.
4. Move code incrementally so behavior is preserved:
   - `Robot` keeps lifecycle and scheduler calls
   - `RobotContainer` owns subsystem instances, controller setup, and autonomous selection
   - `subsystems` expose actions/state, while `commands` coordinate behavior
   - `constants` holds hardware ids, operator ports, and tunables
5. Keep season-specific state machines or scoring logic isolated from the base architecture so they can be swapped per year.
6. Run the checklist in `../../references/validation-checklist.md`.

## Refactor guardrails

- Do not make subsystems globally accessible.
- Prefer dependency injection from `RobotContainer` into commands.
- Do not hide season-specific behavior inside generic helper classes.
- If a repo already has working build tooling, preserve it while improving source layout.

## Output expectations

After this skill runs, another contributor should be able to answer these questions quickly:

- Where is hardware instantiated?
- Where are controller bindings declared?
- Which commands own mechanism behavior?
- Which files are safe to reuse next season?
