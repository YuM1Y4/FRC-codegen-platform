# FRC Codegen Platform

Build FRC robot codebases faster by composing reusable skills, templates, scripts, and references instead of copying last year's repo and hand-editing everything again.

This repository is a cross-season platform for generating and extending WPILib Java robot projects. It is designed for agent-assisted workflows such as Codex, but the bundled scripts and templates are also useful on their own.

## What This Is

Most FRC teams repeat the same work every season:

- recreate the command-based project structure
- rewrite subsystem and command scaffolding
- reconnect controller bindings
- rebuild drivetrain and auto wiring
- re-check the same architecture mistakes

This repo turns those repeated steps into reusable building blocks.

Instead of one giant prompt or one giant template, the platform uses four layers:

- `skills/`: focused workflows such as season assembly, mechanism scaffolding, or validation
- `templates/`: starter Java project files and reusable module templates
- `scripts/`: deterministic code generation and file-rewrite tools
- `references/`: architecture rules, naming conventions, and workflow guidance

## What It Does

Today, the platform can already help with:

- bootstrapping a new WPILib Java project overlay
- enforcing a shared command-based architecture
- scaffolding new mechanisms with subsystem, command, constants, and `RobotContainer` wiring
- validating project structure and build entrypoints
- defining a Phoenix Tuner X first path for modern CTRE swerve projects
- starting from a 2026-style declarative autonomous skeleton built around `AutoRoutines`

## Why This Is Useful

### 1. Stable Architecture Across Seasons

The repo separates reusable robot architecture from season-specific game logic. That makes it easier to carry forward what should stay stable and replace what should change.

### 2. Less Boilerplate

Common edits such as adding a new mechanism or wiring container bindings become scripted and repeatable instead of manual and error-prone.

### 3. Cleaner AI Collaboration

Skills keep the workflow narrow and explicit. Instead of asking an AI to "make the robot code good," you can ask for a specific, bounded capability.

### 4. Better Regeneration Story

For modern CTRE swerve projects, the platform treats Phoenix Tuner X generated drivetrain code as the source of truth instead of forcing teams to rewrite generated constants by hand.

### 5. Faster Onboarding

New students and mentors can understand the project shape more quickly when `Robot`, `RobotContainer`, `commands`, `subsystems`, and constants follow one predictable pattern.

## Current Skill Set

Implemented now:

- `frc-season-assembler`
- `frc-java-architecture`
- `frc-match-validation`
- `frc-mechanism-scaffold`
- `frc-swerve-drive`

Planned next:

- `frc-vision-limelight`
- `frc-auto-choreo`
- `frc-2026-gamepack`
- `frc-2027-gamepack`

## How The Platform Works

Typical flow:

1. Start a new project with the base WPILib Java overlay.
2. Add mechanisms through scaffolding instead of hand-writing repetitive structure.
3. Integrate drivetrain and autonomous layers as separate capabilities.
4. Validate structure and build health before continuing.
5. Add season-specific game logic as isolated gamepack code later.

## Quick Start

## Suggested Workflow With Codex

Example requests:

- "Use `frc-season-assembler` to create a new WPILib Java project with our standard architecture."
- "Use `frc-mechanism-scaffold` to add a shooter subsystem and bind it to the driver controller."
- "Use `frc-swerve-drive` to integrate Phoenix Tuner X generated drivetrain code into this repo."
- "Use `frc-match-validation` to sanity check the project before we continue."

### 1. Create a Starter Project Overlay

```bash
python3 scripts/new_project.py --name "MyRobot" --team-number 9999 --target /path/to/robot-repo
```

### 2. Add a Mechanism

```bash
python3 scripts/add_mechanism.py --project-root /path/to/robot-repo --name "shooter pivot" --motor-id 14 --default-command --bind-button a
```

### 3. Validate the Result

```bash
python3 scripts/validate_project.py --project-root /path/to/robot-repo
```

If the repo does not include its own `gradlew`, provide your WPILib VS Code install path:

```bash
python3 scripts/validate_project.py --project-root /path/to/robot-repo --wpilib-vscode-root /path/to/wpilib/vscode
```

## Swerve Note

The `frc-swerve-drive` path is intentionally not based on hand-writing a generic `Swerve.java` for every team.

For Phoenix 6 compatible CTRE swerve stacks, this platform assumes:

- Phoenix Tuner X generated code should be preferred
- generated `TunerConstants` stays the source of truth
- `CommandSwerveDrivetrain` integration belongs in the architecture
- team-specific bindings, auto logic, and game logic stay outside the generated drivetrain core

## Autonomous Note

The starter template now follows a declarative autonomous structure inspired by this year's example code:

- `Robot` stays thin
- `RobotContainer` configures autos during construction
- `commands/AutoRoutines.java` owns chooser registration
- autonomous starts from mode triggers instead of only the older `getAutonomousCommand()` pattern

This keeps the base template closer to current Choreo-oriented FRC workflows without forcing full Choreo dependency setup into every generated starter.

## Repository Layout

```text
FRC-codegen-platform/
  README.md
  PROJECT_CONTEXT.md
  skills/
  templates/
  scripts/
  references/
```

## Best Use Cases

This repo is a good fit if you want to:

- create a repeatable architecture for multiple seasons
- reduce setup time for new robot repos
- use AI tools with tighter guardrails and clearer workflows
- keep mechanism scaffolding and validation deterministic
- avoid mixing reusable architecture with game-specific code too early

## Limitations

This is still an actively evolving platform, not a finished one-click robot generator.

You should expect to:

- keep your real GradleRIO and vendor dependency setup in the target season repo
- tune mechanisms and drivetrain behavior manually
- add season-specific commands and scoring logic yourself or through future skills
- extend the platform as your team's conventions become clearer



## Project Context

See [`PROJECT_CONTEXT.md`](./PROJECT_CONTEXT.md) for the evolving scope, progress tracker, and planned capability roadmap.
