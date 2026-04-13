#!/usr/bin/env python3
"""Scaffold a mechanism subsystem, command, constants, and RobotContainer wiring."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


SUPPORTED_BINDINGS = {
    "a",
    "b",
    "back",
    "leftBumper",
    "leftTrigger",
    "povDown",
    "povLeft",
    "povRight",
    "povUp",
    "rightBumper",
    "rightTrigger",
    "start",
    "x",
    "y",
}

LEGACY_AUTOS_SNIPPETS = (
    "import frc.robot.subsystems.ExampleSubsystem;",
    "public static Command exampleAuto(ExampleSubsystem exampleSubsystem) {",
    "return new ExampleCommand(exampleSubsystem);",
)

NEUTRAL_AUTOS_TEMPLATE = """package frc.robot.commands;

import edu.wpi.first.wpilibj2.command.Command;
import edu.wpi.first.wpilibj2.command.Commands;

public final class Autos {
  private Autos() {}

  public static Command none() {
    return Commands.none();
  }
}
"""

LEGACY_EXAMPLE_COMMAND_TEMPLATE = """package frc.robot.commands;

import edu.wpi.first.wpilibj2.command.Command;
import frc.robot.subsystems.ExampleSubsystem;

public class ExampleCommand extends Command {
  private final ExampleSubsystem subsystem;

  public ExampleCommand(ExampleSubsystem subsystem) {
    this.subsystem = subsystem;
    addRequirements(subsystem);
  }

  @Override
  public void execute() {
    subsystem.runExample();
  }

  @Override
  public void end(boolean interrupted) {
    subsystem.stop();
  }

  @Override
  public boolean isFinished() {
    return false;
  }
}
"""

LEGACY_EXAMPLE_SUBSYSTEM_TEMPLATE = """package frc.robot.subsystems;

import edu.wpi.first.wpilibj2.command.Command;
import edu.wpi.first.wpilibj2.command.SubsystemBase;

public class ExampleSubsystem extends SubsystemBase {
  public ExampleSubsystem() {}

  public void runExample() {
    // TODO: replace the example action with a real mechanism behavior.
  }

  public void stop() {
    // TODO: stop outputs here once real hardware is connected.
  }

  public Command holdCommand() {
    return run(this::runExample);
  }

  public boolean exampleCondition() {
    return false;
  }
}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Add a basic mechanism scaffold to a robot repo.")
    parser.add_argument("--project-root", required=True, help="Root of the target robot repo.")
    parser.add_argument("--name", required=True, help='Mechanism name, for example "shooter pivot".')
    parser.add_argument(
        "--default-command",
        action="store_true",
        help="Set <mechanism>.holdCommand() as the subsystem's default command.",
    )
    parser.add_argument(
        "--bind-button",
        choices=sorted(SUPPORTED_BINDINGS),
        help="Add a driver-controller binding like a(), b(), leftBumper(), or povUp().",
    )
    return parser.parse_args()


def to_pascal_case(value: str) -> str:
    parts = re.findall(r"[A-Za-z0-9]+", value)
    if not parts:
        raise ValueError("Mechanism name must contain at least one alphanumeric token.")
    return "".join(part[:1].upper() + part[1:] for part in parts)


def to_camel_case(value: str) -> str:
    return value[:1].lower() + value[1:]


def write_from_template(
    template_path: Path, destination: Path, replacements: dict[str, str]
) -> None:
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing mechanism file: {destination}")

    text = template_path.read_text(encoding="utf-8")
    for key, value in replacements.items():
        text = text.replace(key, value)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def find_marker_index(lines: list[str], marker: str) -> int | None:
    for index, line in enumerate(lines):
        if marker in line:
            return index
    return None


def insert_import(
    lines: list[str], marker: str, insertion: str, same_group_prefix: str
) -> bool:
    if insertion in lines:
        return False

    marker_index = find_marker_index(lines, marker)
    if marker_index is not None:
        lines.insert(marker_index, insertion)
        return True

    same_group_indexes = [
        index for index, line in enumerate(lines) if line.startswith(same_group_prefix)
    ]
    if same_group_indexes:
        lines.insert(same_group_indexes[-1] + 1, insertion)
        return True

    import_indexes = [index for index, line in enumerate(lines) if line.startswith("import ")]
    if import_indexes:
        lines.insert(import_indexes[-1] + 1, insertion)
        return True

    package_indexes = [index for index, line in enumerate(lines) if line.startswith("package ")]
    if package_indexes:
        lines.insert(package_indexes[-1] + 1, "")
        lines.insert(package_indexes[-1] + 2, insertion)
        return True

    lines.insert(0, insertion)
    return True


def remove_exact_line(lines: list[str], exact_line: str) -> bool:
    removed = False
    while exact_line in lines:
        lines.remove(exact_line)
        removed = True
    return removed


def insert_before_marker_or_before_constructor(
    lines: list[str], marker: str, insertion: str
) -> bool:
    if insertion in lines:
        return False

    marker_index = find_marker_index(lines, marker)
    if marker_index is not None:
        lines.insert(marker_index, insertion)
        return True

    for index, line in enumerate(lines):
        if line.strip().startswith("private final CommandXboxController "):
            lines.insert(index, insertion)
            return True

    for index, line in enumerate(lines):
        if line.strip().startswith("public RobotContainer()"):
            lines.insert(index, insertion)
            return True

    raise ValueError("Could not find a place to insert subsystem fields in RobotContainer.java.")


def find_method_block(lines: list[str], signature: str) -> tuple[int, int]:
    start_index = next(
        (index for index, line in enumerate(lines) if signature in line),
        None,
    )
    if start_index is None:
        raise ValueError(f"Could not find method signature in RobotContainer.java: {signature}")

    brace_depth = 0
    for index in range(start_index, len(lines)):
        brace_depth += lines[index].count("{")
        brace_depth -= lines[index].count("}")
        if brace_depth == 0 and index > start_index:
            return start_index, index

    raise ValueError(f"Could not find the end of method block: {signature}")


def insert_in_method(lines: list[str], signature: str, marker: str, insertion: str) -> bool:
    if insertion in lines:
        return False

    marker_index = find_marker_index(lines, marker)
    if marker_index is not None:
        lines.insert(marker_index, insertion)
        return True

    _, end_index = find_method_block(lines, signature)
    lines.insert(end_index, insertion)
    return True


def collapse_blank_runs(lines: list[str]) -> list[str]:
    collapsed: list[str] = []
    previous_blank = False
    for line in lines:
        is_blank = line == ""
        if is_blank and previous_blank:
            continue
        collapsed.append(line)
        previous_blank = is_blank
    return collapsed


def trim_blank_line_before_marker(lines: list[str], marker: str) -> bool:
    marker_index = find_marker_index(lines, marker)
    if marker_index is None or marker_index == 0:
        return False
    if lines[marker_index - 1] != "":
        return False
    del lines[marker_index - 1]
    return True


def cleanup_legacy_robot_container(robot_container_path: Path) -> list[str]:
    lines = robot_container_path.read_text(encoding="utf-8").splitlines()
    changes: list[str] = []

    cleanup_lines = (
        "import edu.wpi.first.wpilibj2.command.button.Trigger;",
        "import frc.robot.commands.ExampleCommand;",
        "import frc.robot.subsystems.ExampleSubsystem;",
        "  private final ExampleSubsystem exampleSubsystem = new ExampleSubsystem();",
        "    new Trigger(exampleSubsystem::exampleCondition)",
        "        .onTrue(new ExampleCommand(exampleSubsystem));",
    )
    labels = (
        "removed legacy Trigger import",
        "removed ExampleCommand import",
        "removed ExampleSubsystem import",
        "removed ExampleSubsystem field",
        "removed example binding start",
        "removed example binding finish",
    )

    for exact_line, label in zip(cleanup_lines, labels):
        if remove_exact_line(lines, exact_line):
            changes.append(label)

    for index, line in enumerate(lines):
        if line == "    return Autos.exampleAuto(exampleSubsystem);":
            lines[index] = "    return Autos.none();"
            changes.append("updated autonomous return to Autos.none()")

    if trim_blank_line_before_marker(lines, "__BINDINGS__"):
        changes.append("removed blank line before bindings marker")
    if trim_blank_line_before_marker(lines, "__DEFAULT_COMMANDS__"):
        changes.append("removed blank line before default command marker")

    normalized = collapse_blank_runs(lines)
    if normalized != lines:
        lines = normalized

    if changes:
        robot_container_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return changes


def cleanup_legacy_autos(autos_path: Path) -> list[str]:
    if not autos_path.exists():
        return []

    contents = autos_path.read_text(encoding="utf-8")
    if not all(snippet in contents for snippet in LEGACY_AUTOS_SNIPPETS):
        return []

    autos_path.write_text(NEUTRAL_AUTOS_TEMPLATE, encoding="utf-8")
    return ["rewrote Autos.java to neutral placeholder"]


def delete_if_matches(path: Path, expected_contents: str) -> bool:
    if not path.exists():
        return False
    if path.read_text(encoding="utf-8") != expected_contents:
        return False
    path.unlink()
    return True


def cleanup_legacy_example_files(package_root: Path) -> list[str]:
    changes: list[str] = []
    if delete_if_matches(
        package_root / "commands" / "ExampleCommand.java",
        LEGACY_EXAMPLE_COMMAND_TEMPLATE,
    ):
        changes.append("deleted legacy ExampleCommand.java")

    if delete_if_matches(
        package_root / "subsystems" / "ExampleSubsystem.java",
        LEGACY_EXAMPLE_SUBSYSTEM_TEMPLATE,
    ):
        changes.append("deleted legacy ExampleSubsystem.java")

    return changes


def cleanup_legacy_starter(package_root: Path, robot_container_path: Path) -> list[str]:
    changes: list[str] = []
    changes.extend(cleanup_legacy_robot_container(robot_container_path))
    changes.extend(cleanup_legacy_autos(package_root / "commands" / "Autos.java"))
    changes.extend(cleanup_legacy_example_files(package_root))
    return changes


def update_robot_container(
    robot_container_path: Path,
    mechanism_class: str,
    command_class: str,
    default_command: bool,
    bind_button: str | None,
) -> list[str]:
    field_name = to_camel_case(mechanism_class)
    lines = robot_container_path.read_text(encoding="utf-8").splitlines()
    changes: list[str] = []

    subsystem_import = f"import frc.robot.subsystems.{mechanism_class};"
    if insert_import(
        lines,
        "__SUBSYSTEM_IMPORTS__",
        subsystem_import,
        "import frc.robot.subsystems.",
    ):
        changes.append(f"subsystem import: {mechanism_class}")

    subsystem_field = f"  private final {mechanism_class} {field_name} = new {mechanism_class}();"
    if insert_before_marker_or_before_constructor(lines, "__SUBSYSTEM_FIELDS__", subsystem_field):
        changes.append(f"subsystem field: {field_name}")

    if default_command:
        default_command_line = f"    {field_name}.setDefaultCommand({field_name}.holdCommand());"
        if insert_in_method(
            lines,
            "private void configureDefaultCommands()",
            "__DEFAULT_COMMANDS__",
            default_command_line,
        ):
            changes.append(f"default command: {field_name}.holdCommand()")

    if bind_button:
        command_import = f"import frc.robot.commands.{command_class};"
        if insert_import(
            lines,
            "__COMMAND_IMPORTS__",
            command_import,
            "import frc.robot.commands.",
        ):
            changes.append(f"command import: {command_class}")

        binding_line = (
            f"    driverController.{bind_button}().whileTrue(new {command_class}({field_name}));"
        )
        if insert_in_method(
            lines,
            "private void configureBindings()",
            "__BINDINGS__",
            binding_line,
        ):
            changes.append(f"binding: driverController.{bind_button}()")

    robot_container_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return changes


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    project_root = Path(args.project_root).expanduser().resolve()
    package_root = project_root / "src" / "main" / "java" / "frc" / "robot"
    templates_root = repo_root / "templates" / "modules" / "basic-mechanism"
    robot_container_path = package_root / "RobotContainer.java"

    if not package_root.exists():
        raise FileNotFoundError(
            f"Expected WPILib Java package root at {package_root}. "
            "Run scripts/new_project.py first or point to an existing robot repo."
        )
    if not robot_container_path.exists():
        raise FileNotFoundError(f"Expected RobotContainer.java at {robot_container_path}")

    mechanism_class = to_pascal_case(args.name)
    field_name = to_camel_case(mechanism_class)
    command_class = f"Run{mechanism_class}"
    replacements = {
        "__MECHANISM_CLASS__": mechanism_class,
        "__MECHANISM_NAME__": args.name,
        "__COMMAND_CLASS__": command_class,
    }

    write_from_template(
        templates_root / "Subsystem.java.tmpl",
        package_root / "subsystems" / f"{mechanism_class}.java",
        replacements,
    )
    write_from_template(
        templates_root / "Command.java.tmpl",
        package_root / "commands" / f"{command_class}.java",
        replacements,
    )
    write_from_template(
        templates_root / "Constants.java.tmpl",
        package_root / "constants" / f"{mechanism_class}Constants.java",
        replacements,
    )
    cleanup_changes = cleanup_legacy_starter(package_root, robot_container_path)
    container_changes = update_robot_container(
        robot_container_path,
        mechanism_class,
        command_class,
        args.default_command,
        args.bind_button,
    )

    print(f"Scaffolded mechanism: {mechanism_class}")
    print(f"RobotContainer wiring target: {field_name}")
    if cleanup_changes:
        print("Cleaned legacy starter placeholders:")
        for change in cleanup_changes:
            print(f"  - {change}")
    if container_changes:
        print("Applied RobotContainer updates:")
        for change in container_changes:
            print(f"  - {change}")
    else:
        print("RobotContainer was already up to date for the requested wiring.")
    print("Next steps:")
    print("  1. Replace placeholder motor ids and mechanism behavior.")
    print("  2. Tune or replace the generated binding/default command as needed.")
    print("  3. Run the validation checklist before building on top of the scaffold.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
