# FRC Naming Conventions

## Packages

- base package: `frc.robot`
- subsystems live in `frc.robot.subsystems`
- commands live in `frc.robot.commands`
- constants live in `frc.robot.constants`

Only add nested packages when they help navigation for a real cluster of files.

## Classes

- subsystem classes use nouns: `Shooter`, `IntakePivot`, `Climber`
- command classes use verb phrases: `RunShooter`, `StowIntake`, `ZeroElevator`
- autonomous helpers live under `Autos` or `commands.auto`
- constant holders use descriptive names: `Ports`, `OperatorConstants`, `ShooterConstants`

Prefer full words over short abbreviations unless the team already uses an established short name.

## Fields and Methods

- use descriptive camelCase field names
- avoid global mutable state
- boolean queries should read like predicates: `hasPiece()`, `atGoal()`, `isZeroed()`
- command factory methods should end with `Command` when they return a WPILib command

## Files

- one top-level public class per file
- file names should exactly match the class name
- mechanism scaffold output should be predictable so scripts can target it safely

## Constants

- hardware ids go in `Ports`
- controller ports go in `OperatorConstants`
- tunables belong in a mechanism-specific constants file
- keep units in the constant name when ambiguity is possible

Examples:

- `MAX_SPEED_METERS_PER_SECOND`
- `ARM_STOW_ANGLE_DEGREES`
- `DRIVER_CONTROLLER_PORT`

## Seasonal Naming

Use season-specific names only for season-specific code. Avoid leaking game vocabulary into reusable architecture classes unless the class truly belongs to that year's game pack.
