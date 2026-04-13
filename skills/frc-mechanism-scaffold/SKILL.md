---
name: frc-mechanism-scaffold
description: Add a new FRC robot mechanism using the platform's standard subsystem, command, constants, Ports wiring, and RobotContainer conventions. Use when a user wants to scaffold a shooter, intake, climber, pivot, elevator, or similar mechanism into an existing WPILib Java project without hand-writing the repeated project plumbing.
---

# frc-mechanism-scaffold

Use this skill when the user wants a new mechanism added to a robot project that already follows, or is being moved toward, the shared Java architecture.

## Responsibilities

- create the mechanism subsystem, command, and mechanism-specific constants files
- add hardware id placeholders to `Ports.java`
- wire the mechanism into `RobotContainer`
- optionally add a default command and a driver-controller button binding
- clean legacy starter placeholders when they would otherwise pollute the generated project

## Boundaries

This skill owns:

- structural scaffolding for a new mechanism
- predictable file naming and package placement
- standard open-loop placeholders
- container and ports plumbing

This skill does not own:

- real hardware API selection or vendor motor controller code
- closed-loop control logic, feedforward, or tuning
- season-specific scoring routines
- autonomous strategy beyond basic command wiring

## Workflow

1. Read `../../references/architecture-principles.md` and `../../references/naming-conventions.md`.
2. If you need flag guidance or output expectations, read `../../references/mechanism-scaffold-workflow.md`.
3. Run `python3 ../../scripts/add_mechanism.py --project-root <repo-root> --name "<mechanism-name>"`.
4. Add `--motor-id <id>` when the user already knows the hardware id.
5. Add `--default-command` or `--bind-button <button>` only when the user explicitly wants those wiring choices, or when the existing project pattern makes the right default obvious.
6. After scaffolding, validate with `../../references/validation-checklist.md` or `frc-match-validation`.

## Output expectations

Leave the repo with:

- a new subsystem under `subsystems/`
- a new command under `commands/`
- mechanism-specific tunables under `constants/`
- a new `Ports.<Mechanism>.MOTOR_ID` entry
- matching `RobotContainer` wiring when requested

## Notes

- Prefer the script over manual edits so the output stays predictable and repeatable.
- If the target repo has already diverged heavily from the standard package layout, use `frc-java-architecture` first or be explicit about the risk before scaffolding.
