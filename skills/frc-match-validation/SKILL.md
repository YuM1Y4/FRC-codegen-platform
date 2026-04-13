---
name: frc-match-validation
description: Run structural, build, and targeted sanity checks against a WPILib Java robot project before more work continues. Use when a user wants to validate a generated or refactored repo, confirm it is safe to build on, or get a concise pass/warn/fail handoff after scaffold or architecture changes.
---

# frc-match-validation

Use this skill after `frc-season-assembler`, `frc-java-architecture`, or mechanism/autonomous integration work.

## Responsibilities

- validate the repo against the shared architecture and handoff checklist
- run the standard scripted checks from `../../scripts/validate_project.py`
- report what passed, what was skipped, and what still looks stubbed
- stop on real blockers before more codegen or refactoring continues

## Boundaries

This skill owns:

- structural sanity checks
- Gradle task discovery and safe build validation
- optional desktop sim validation when the repo supports it and the user wants it
- concise validation reporting

This skill does not own:

- fixing every failing issue automatically
- inventing new build tasks that the target repo does not already have
- running long-lived simulation tasks by default

## Workflow

1. Read `../../references/validation-checklist.md`.
2. If you need task-selection details or reporting expectations, read `../../references/validation-workflow.md`.
3. If build validation matters and the repo does not carry its own `gradlew`, ask the user where WPILib VS Code is installed.
4. Run `python3 ../../scripts/validate_project.py --project-root <repo-root>`.
5. If the user gave a WPILib VS Code path, add `--wpilib-vscode-root <path>` so the script can use the shared `gradlew`.
6. Add `--run-sim` only when the target repo exposes a safe desktop sim task and the user wants that check.
7. Summarize the result as pass, warn, or fail, including:
   - checks actually run
   - checks skipped and why
   - placeholders or stubs still present
   - the next unblocker if validation failed

## Output expectations

Leave the user with a short validation handoff that answers:

- Is the repo structurally aligned with the platform?
- Did the normal build entrypoint pass?
- Was simulation checked, skipped, or unavailable?
- What should be fixed before more generation work continues?

## Notes

- Prefer the shared script over ad hoc shell sequences so validation stays repeatable.
- If the repo has no `gradlew`, do not guess. Ask for the WPILib VS Code install path and use its shared `gradlew`, or report build validation as skipped.
