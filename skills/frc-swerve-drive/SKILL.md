---
name: frc-swerve-drive
description: Integrate a Phoenix 6 and Phoenix Tuner X generated swerve drivetrain into the platform's WPILib Java architecture. Use when a user wants to wire generated TunerConstants and CommandSwerveDrivetrain code into RobotContainer, preserve Phoenix-generated drivetrain constants, or prepare the repo for higher-level auto and vision skills without hand-writing generic swerve boilerplate.
---

# frc-swerve-drive

Use this skill when the target robot has a Phoenix 6 compatible CTRE swerve stack or the user already has Phoenix Tuner X generated drivetrain files.

## Responsibilities

- treat Phoenix Tuner X generated swerve files as the source of truth for drivetrain construction and constants
- integrate the generated drivetrain into the shared `Robot` and `RobotContainer` architecture
- wire readable default driving behavior and baseline operator bindings
- keep season logic and autonomous composition outside the low-level drivetrain implementation
- hand off validation to `frc-match-validation`

## Boundaries

This skill owns:

- deciding when Phoenix Tuner X generation should replace hand-written drivetrain boilerplate
- package placement and integration of generated `TunerConstants`, `CommandSwerveDrivetrain`, and related helper classes
- `RobotContainer` level drive requests, baseline bindings, and autonomous handoff points

This skill does not own:

- manually recreating module ids, offsets, gearing, or geometry that Tuner X can generate
- full drivetrain characterization and gain tuning
- mixed-vendor or non-Phoenix swerve architectures unless the user explicitly wants a custom path
- season-specific autonomous logic

## Workflow

1. Read `../../references/architecture-principles.md` and `../../references/naming-conventions.md`.
2. Read `../../references/swerve-drive-workflow.md`.
3. Confirm whether the drivetrain is fully Phoenix 6 and Tuner X compatible.
4. If it is compatible, prefer a generated Phoenix project or regenerated `TunerConstants` over hand-written `Swerve.java` style scaffolding.
5. Preserve the generated drivetrain files together and keep edits inside them minimal.
6. Integrate the drivetrain through `RobotContainer`, including:
   - a default field-centric drive request
   - only the baseline driver bindings the user actually wants
   - a clear autonomous handoff surface for `frc-auto-choreo` or another auto layer
7. Validate with `frc-match-validation`, including sim only when the repo already supports it and the user wants that check.

## Guardrails

- Treat generated `TunerConstants` as drivetrain hardware and geometry source of truth.
- Do not copy Phoenix-generated swerve ids or offsets into `Ports.java`.
- If the user only has physical measurements and not generated code yet, direct them to Phoenix Tuner X first.
- Keep game-specific commands and scoring logic outside the generated drivetrain files.

## Output expectations

Leave the repo with:

- generated Phoenix swerve files preserved and clearly located
- `RobotContainer` owning readable drive bindings
- a drivetrain integration that is ready for follow-on auto and vision skills
- a short note about any remaining tuning or generation steps still needed
