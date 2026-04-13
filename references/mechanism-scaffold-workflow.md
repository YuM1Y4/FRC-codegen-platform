# Mechanism Scaffold Workflow

## When to use this

Use this workflow when a user wants to add a new hardware-backed capability such as a shooter, intake, climber, wrist, pivot, or elevator to an existing WPILib Java project.

## Scripted entrypoint

Base command:

```bash
python3 scripts/add_mechanism.py --project-root /path/to/robot-repo --name "shooter pivot"
```

Useful options:

```bash
python3 scripts/add_mechanism.py \
  --project-root /path/to/robot-repo \
  --name "shooter pivot" \
  --motor-id 14 \
  --default-command \
  --bind-button a
```

## What the script creates

- `subsystems/<Mechanism>.java`
- `commands/Run<Mechanism>.java`
- `constants/<Mechanism>Constants.java`
- `Ports.<Mechanism>.MOTOR_ID`

## What the script updates

- `RobotContainer` subsystem imports and fields
- optional default command wiring
- optional driver-controller binding
- legacy starter placeholders if they are still present

## What still needs human follow-up

- replace placeholder motor output logic
- swap in real vendor motor controller code
- tune mechanism constants
- verify bindings and default-command behavior make sense for the real robot

## Recommended handoff

After scaffolding, report:

- which files were created
- whether `Ports.java` and `RobotContainer` were updated
- which options were used, such as `--motor-id`, `--default-command`, or `--bind-button`
- what is still stubbed and needs real mechanism implementation
