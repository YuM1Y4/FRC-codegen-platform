# FRC Java Architecture Principles

## Purpose

This document defines the stable project shape that should survive across seasons. Game logic can change every year, but the boundaries between lifecycle, container wiring, commands, subsystems, and constants should stay familiar.

## Stable vs Seasonal

Stable layers:

- `Robot`: WPILib lifecycle entrypoints and scheduler call only
- `RobotContainer`: subsystem construction, controller bindings, autonomous selection
- `subsystems`: hardware-facing state and actions
- `commands`: behavior orchestration and operator intent
- `constants`: ports, controller ids, tunables, and robot identity

Allowed exception:

- vendor-generated Phoenix Tuner swerve files may stay grouped together so regeneration stays low-friction; treat generated drivetrain constants as the source of truth instead of forcing them into `Ports`

Seasonal layers:

- scoring sequences
- field landmarks
- autonomous route selection
- superstructure state machines
- game-specific operator workflows

Keep seasonal logic out of `Robot` and keep reusable subsystem architecture out of season packs.

## Source Layout

Expected Java package layout:

```text
frc.robot
  Robot.java
  RobotContainer.java
  commands/
  subsystems/
  constants/
```

Add deeper packages only when the project grows enough to justify them, for example `commands/auto/` or `subsystems/vision/`.

## Class Responsibilities

### Robot

- instantiate `RobotContainer`
- call the command scheduler in `robotPeriodic()`
- keep autonomous orchestration declarative when possible instead of hand-scheduling from `autonomousInit()`
- reserve mode-specific lifecycle overrides for real robot concerns, not routine container wiring

`Robot` should not directly read joysticks, command actuators, or coordinate subsystem logic.

### RobotContainer

- own subsystem instances
- own controller objects
- declare trigger bindings
- configure autonomous selection or routine registration

If `RobotContainer` becomes crowded, extract helper methods, not global singletons.

For new repos, prefer a dedicated `AutoRoutines` layer configured during `RobotContainer`
construction instead of the older `getAutonomousCommand()` pattern.

### Subsystems

- represent hardware-backed capabilities
- expose high-level actions and state queries
- avoid knowing who called them

A subsystem should be reusable across driver bindings, autos, tests, and future season packs.

### Commands

- coordinate one behavior at a time
- express operator intent or autonomous steps
- declare subsystem requirements explicitly

Commands should not instantiate their own hardware.

### Constants

Split constants by concern instead of building one giant file:

- `OperatorConstants`
- `Ports`
- `<Mechanism>Constants`
- `RobotIdentity`

Exception:

- Phoenix Tuner generated swerve configs such as `TunerConstants` stay with the generated drivetrain code instead of being copied into `Ports`

## Reuse Rule

When deciding where new logic belongs, ask:

1. Is this still useful next season?
2. Does it depend on the current game objective?
3. Does it describe hardware structure or match strategy?

If it is cross-season and structural, keep it in the stable architecture. If it depends on the current game, isolate it.

## Assembly Rule

Use templates for starter code, references for policy and conventions, and scripts for repetitive deterministic edits. Do not make a skill body carry all implementation detail by itself.
