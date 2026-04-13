# Validation Workflow

## When to use this

Use this workflow after bootstrapping a new robot repo, after architecture refactors, and after adding mechanisms or autonomous wiring that could break the project shape.

## Scripted entrypoint

Recommended command:

```bash
python3 scripts/validate_project.py --project-root /path/to/robot-repo
```

If the repo does not carry its own `gradlew`, first ask the user where WPILib VS Code is installed, then run:

```bash
python3 scripts/validate_project.py --project-root /path/to/robot-repo --wpilib-vscode-root /path/to/wpilib/vscode
```

Optional desktop simulation check:

```bash
python3 scripts/validate_project.py --project-root /path/to/robot-repo --wpilib-vscode-root /path/to/wpilib/vscode --run-sim
```

Simulation is opt-in because some Gradle sim tasks launch long-running desktop processes.

## What the script checks

### Structure

- expected `src/main/java/frc/robot` layout
- `Robot` ownership of scheduler and a clean lifecycle surface
- either a legacy `getAutonomousCommand()` path or a declarative `AutoRoutines` autonomous entrypoint
- presence of `commands`, `subsystems`, and `constants`
- placeholder markers or TODOs that still remain in generated code

### Build

- whether `gradlew` exists
- whether the script fell back to WPILib VS Code's shared `gradlew`
- which Java runtime is being used when `--java-home`, `JAVA_HOME`, or the WPILib install implies one
- which Gradle tasks are available
- the normal build entrypoint, usually `build` or `check`

### Simulation

- whether a known desktop sim task is available
- whether it was skipped, passed, failed, or timed out

## Reporting format

At handoff, summarize:

- overall status: pass, warn, or fail
- checks executed
- checks skipped and why
- blockers that must be fixed before more skill composition continues
- any remaining stubs or placeholders
