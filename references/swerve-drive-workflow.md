# Swerve Drive Workflow

## Purpose

This workflow defines how `frc-swerve-drive` should integrate a Phoenix 6 swerve drivetrain into the platform's standard WPILib Java architecture.

## Official Phoenix Tuner X Notes

As of 2026-04-14, the official CTR Phoenix 6 docs describe this as the preferred Java swerve workflow for v6-compatible drivetrains:

- Phoenix 6 introduced a Java Swerve API and Tuner X project generator in the 2024 release stream.
- Tuner X can generate a full robot project or regenerate only `TunerConstants` for an existing project.
- The official example wiring uses `CommandSwerveDrivetrain drivetrain = TunerConstants.DriveTrain`.
- The generated project is minimum viable control, not a fully tuned final drivetrain.
- All required swerve devices need to be Phoenix 6 compatible for this workflow to fit cleanly.

This means the platform should not default to hand-writing a generic `Swerve.java` or copying drivetrain ids into `Ports.java` when the robot is already using the Phoenix 6 swerve stack.

## When This Workflow Applies

Use this workflow when:

- the robot uses Talon FX drive motors
- the robot uses Talon FX steer motors
- the robot uses CANcoders for module azimuth sensing
- the robot uses a Pigeon 2 gyro
- the team is using Phoenix 6 and Phoenix Tuner X

If the robot is mixed-vendor or the user explicitly wants a non-Tuner path, say so clearly and treat that as a different implementation path.

## Integration Rule

Treat the generated drivetrain cluster as vendor-generated code:

- preserve generated files as the source of truth for drivetrain hardware ids, offsets, gearing, geometry, and baseline gains
- keep edits inside generated files minimal so regeneration remains practical
- move team-specific bindings, season logic, auto selection, and match behavior into normal project files

## Preferred Project Shape

The exact generated package may vary, but the integration should end up with three clear layers:

1. Generated Phoenix swerve files kept together in one dedicated package or folder.
2. Team-owned `RobotContainer` bindings and higher-level drive commands outside the generated files.
3. Season-specific autonomous, targeting, and game behavior outside the drivetrain implementation.

## RobotContainer Expectations

When integrating generated Phoenix swerve code:

- instantiate or reference the drivetrain from `TunerConstants`
- set a readable default field-centric drive request in `RobotContainer`
- wire only baseline controls here, such as brake, point wheels, heading reset, or seed field-relative pose, when the user wants them
- keep autonomous selection in `RobotContainer` or an auto-specific layer, not inside the low-level generated drivetrain constructor

## Validation Expectations

After integration:

- run `frc-match-validation`
- include build validation whenever the repo can expose Gradle
- include sim validation when the generated drivetrain already supports it and the user wants that check
- call out whether `TunerConstants` still contains placeholder or untuned gains that need on-robot characterization

## Handoff Guidance

- use `frc-auto-choreo` or another auto skill for trajectory following and autonomous routine composition
- use `frc-vision-limelight` or another vision skill for pose fusion and targeting workflows
- do not bury game-specific operator behavior inside the generated Phoenix drivetrain files
