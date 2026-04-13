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
- schedule the autonomous command in `autonomousInit()`
- cancel or replace autonomous on teleop start

`Robot` should not directly read joysticks, command actuators, or coordinate subsystem logic.

### RobotContainer

- own subsystem instances
- own controller objects
- declare trigger bindings
- expose the selected autonomous command

If `RobotContainer` becomes crowded, extract helper methods, not global singletons.

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

## Reuse Rule

When deciding where new logic belongs, ask:

1. Is this still useful next season?
2. Does it depend on the current game objective?
3. Does it describe hardware structure or match strategy?

If it is cross-season and structural, keep it in the stable architecture. If it depends on the current game, isolate it.

## Assembly Rule

Use templates for starter code, references for policy and conventions, and scripts for repetitive deterministic edits. Do not make a skill body carry all implementation detail by itself.
