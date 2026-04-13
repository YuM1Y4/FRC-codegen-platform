# Validation Checklist

## Goal

Generated or refactored robot code should pass a lightweight sanity review before more features are added.

## Structure checks

- `Robot` only owns lifecycle and scheduling
- `RobotContainer` owns subsystem construction and bindings
- subsystem files do not instantiate controllers directly
- hardware ids and operator ports live in constants packages
- season-specific logic is isolated from stable architecture

## Build checks

- run the repo's normal Gradle build
- run tests if the repo defines them
- run desktop simulation if the repo already supports it

Use the tasks already present in the target project instead of inventing new tooling during a structural change.

## Behavioral checks

- autonomous command can still be selected and scheduled
- teleop init cancels or replaces autonomous intentionally
- default commands are assigned where expected
- new bindings have an obvious owner and trigger location

## Review checks

- every new mechanism has a subsystem, command entrypoints, and constants home
- generated placeholders are clearly marked and easy to replace
- no repeated boilerplate was pasted where a script or template should exist instead

## Before handoff

Leave a short note covering:

- what was scaffolded
- what is still a stub
- which validation steps were actually run
