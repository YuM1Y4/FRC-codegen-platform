# Validation Checklist

## Goal

Generated or refactored robot code should pass a lightweight sanity review before more features are added.

Recommended scripted entrypoint:

```bash
python3 scripts/validate_project.py --project-root /path/to/robot-repo
```

If the repo does not carry its own `gradlew`, ask the user where WPILib VS Code is installed and prefer:

```bash
python3 scripts/validate_project.py --project-root /path/to/robot-repo --wpilib-vscode-root /path/to/wpilib/vscode
```

Use `--run-sim` only when the target repo exposes a safe desktop simulation task and you explicitly want that check.

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

- autonomous can still be selected and scheduled, either through a legacy command getter or a declarative auto routine layer
- autonomous stop or handoff behavior is intentional when the robot leaves autonomous
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
