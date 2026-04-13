---
name: frc-season-assembler
description: Assemble a fresh FRC season codebase from this platform's WPILib Java starter overlay, architecture conventions, and selected module scaffolds. Use when a user wants to bootstrap a new season repo, start from the standard project layout, or compose the base robot structure before game-specific work begins.
---

# frc-season-assembler

Use this skill when the user wants a new season project, not when they only want to reorganize an existing repo.

## Responsibilities

- create or update the baseline `src/main/java/frc/robot` structure from `../../templates/wpilib-java-base/`
- stamp robot identity and starter files via `../../scripts/new_project.py`
- keep stable architecture separate from season-specific logic
- hand off subsystem-specific work to narrower capability skills once the base project exists
- finish with the checks in `../../references/validation-checklist.md`

## Boundaries

This skill owns:

- project bootstrap
- common folders, constants, container wiring markers, and starter autonomous shape
- the first pass of validation

This skill does not own:

- detailed mechanism behavior
- season scoring state machines
- field-specific autonomous strategy
- vendor library selection beyond what already exists in the target repo

## Workflow

1. Read `../../references/architecture-principles.md` and `../../references/naming-conventions.md`.
2. Inspect the target repo. If it already contains a WPILib project, treat `templates/wpilib-java-base/` as an overlay instead of replacing the whole repo.
3. Run `../../scripts/new_project.py --name <robot-name> --team-number <team-number> --target <repo-root>`.
4. Confirm the generated layout still leaves room for season packs under `commands`, `subsystems`, or future packages without leaking season logic into `Robot` or `RobotContainer`.
5. If the user requested extra capabilities, invoke the narrower skill or script for each capability instead of manually pasting repeated scaffolding.
6. Validate using `../../references/validation-checklist.md`.

## Required outputs

Leave the target project with:

- a clean `Robot` to `RobotContainer` control flow
- dedicated `commands`, `subsystems`, and `constants` packages
- a clear place for controller bindings and autonomous selection
- a short note about which pieces are still intentionally stubbed

## Notes

- The current starter template is an architecture overlay. Keep the existing GradleRIO or vendor setup from the target season repo unless the user explicitly asks to regenerate build tooling.
- Prefer deterministic edits via the bundled scripts over one-off hand assembly when the same pattern repeats.
