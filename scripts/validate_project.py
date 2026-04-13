#!/usr/bin/env python3
"""Run structural and Gradle-based sanity checks for a WPILib Java robot repo."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BUILD_TASK_CANDIDATES = ("build", "check")
SIM_TASK_CANDIDATES = (
    "simulateJava",
    "simulateExternalJava",
    "simulateJavaRelease",
    "simulateExternalJavaRelease",
)
PLACEHOLDER_TOKENS = (
    "TODO:",
    "__BINDINGS__",
    "__DEFAULT_COMMANDS__",
    "__COMMAND_IMPORTS__",
    "__SUBSYSTEM_IMPORTS__",
    "__SUBSYSTEM_FIELDS__",
)
STATUS_PRIORITY = {"PASS": 0, "SKIP": 1, "WARN": 2, "FAIL": 3}


@dataclass
class CheckResult:
    name: str
    status: str
    message: str
    command: str | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a WPILib Java robot repo for structure, build, and optional sim checks."
    )
    parser.add_argument("--project-root", required=True, help="Root of the robot repo to validate.")
    parser.add_argument(
        "--java-home",
        help="JAVA_HOME to use for Gradle validation, for example /Users/<user>/wpilib/2026/jdk.",
    )
    parser.add_argument(
        "--wpilib-vscode-root",
        help="Path to the WPILib VS Code install root so the script can use its shared gradlew when needed.",
    )
    parser.add_argument(
        "--skip-structure",
        action="store_true",
        help="Skip source-structure checks and only inspect build/sim entrypoints.",
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Skip Gradle build execution even if gradlew exists.",
    )
    parser.add_argument(
        "--run-sim",
        action="store_true",
        help="Run one detected desktop simulation task instead of only reporting its availability.",
    )
    parser.add_argument(
        "--sim-timeout-seconds",
        type=int,
        default=20,
        help="Timeout for the optional simulation task.",
    )
    return parser.parse_args()


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def resolve_java_home(java_home_arg: str | None) -> Path | None:
    candidate = java_home_arg or os.environ.get("JAVA_HOME")
    if not candidate:
        return None

    java_home = Path(candidate).expanduser().resolve()
    if not java_home.exists():
        raise FileNotFoundError(f"JAVA_HOME does not exist: {java_home}")

    java_bin = java_home / "bin" / "java"
    if not java_bin.exists():
        raise FileNotFoundError(f"JAVA_HOME does not contain bin/java: {java_bin}")

    return java_home


def resolve_wpilib_vscode_root(wpilib_vscode_root_arg: str | None) -> Path | None:
    if not wpilib_vscode_root_arg:
        return None

    wpilib_root = Path(wpilib_vscode_root_arg).expanduser().resolve()
    if not wpilib_root.exists():
        raise FileNotFoundError(f"WPILib VS Code root does not exist: {wpilib_root}")
    return wpilib_root


def infer_java_home_from_wpilib_root(wpilib_vscode_root: Path | None) -> Path | None:
    if wpilib_vscode_root is None:
        return None

    parent = wpilib_vscode_root.parent
    candidates = [parent / "jdk", *sorted(parent.glob("jdk*"))]
    for candidate in candidates:
        java_bin = candidate / "bin" / "java"
        if java_bin.exists():
            return candidate.resolve()

    return None


def build_command_env(java_home: Path | None) -> dict[str, str]:
    env = os.environ.copy()
    if java_home is None:
        return env

    env["JAVA_HOME"] = str(java_home)
    env["PATH"] = f"{java_home / 'bin'}:{env.get('PATH', '')}"
    return env


def run_command(
    command: list[str],
    cwd: Path,
    timeout_seconds: int,
    env: dict[str, str] | None = None,
) -> tuple[int, str, str, bool]:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
            env=env,
        )
        return completed.returncode, completed.stdout, completed.stderr, False
    except subprocess.TimeoutExpired as exc:
        return 124, exc.stdout or "", exc.stderr or "", True


def summarize_output(stdout: str, stderr: str, max_lines: int = 8) -> str:
    merged = [line.strip() for line in f"{stdout}\n{stderr}".splitlines() if line.strip()]
    if not merged:
        return "No output."
    return " | ".join(merged[-max_lines:])


def choose_first_available(tasks: set[str], candidates: tuple[str, ...]) -> str | None:
    for candidate in candidates:
        if candidate in tasks:
            return candidate
    return None


def find_shared_wpilib_gradlew(wpilib_vscode_root: Path | None) -> Path | None:
    if wpilib_vscode_root is None:
        return None

    direct_shared = wpilib_vscode_root / "resources" / "gradle" / "shared" / "gradlew"
    if direct_shared.exists():
        return direct_shared.resolve()

    vscode_shared_candidates = sorted(
        wpilib_vscode_root.glob(
            "code-portable-data/extensions/wpilibsuite.vscode-wpilib-*/resources/gradle/shared/gradlew"
        )
    )
    if vscode_shared_candidates:
        return vscode_shared_candidates[-1].resolve()

    return None


def validate_java_runtime(project_root: Path, java_home: Path | None) -> CheckResult:
    if java_home is None:
        return CheckResult(
            name="java-runtime",
            status="SKIP",
            message="JAVA_HOME not provided; using the shell environment if Gradle runs.",
        )

    java_bin = java_home / "bin" / "java"
    command = [str(java_bin), "-version"]
    returncode, stdout, stderr, timed_out = run_command(
        command,
        project_root,
        timeout_seconds=30,
        env=build_command_env(java_home),
    )

    if timed_out:
        return CheckResult(
            name="java-runtime",
            status="WARN",
            message=f"java -version timed out for JAVA_HOME={java_home}.",
            command=" ".join(command),
        )

    if returncode != 0:
        return CheckResult(
            name="java-runtime",
            status="FAIL",
            message=f"java -version failed for JAVA_HOME={java_home}: {summarize_output(stdout, stderr)}",
            command=" ".join(command),
        )

    summary = summarize_output(stdout, stderr, max_lines=3)
    return CheckResult(
        name="java-runtime",
        status="PASS",
        message=f"Using JAVA_HOME={java_home}. {summary}",
        command=" ".join(command),
    )


def discover_gradle_tasks(
    project_root: Path,
    gradlew_path: Path,
    command_env: dict[str, str] | None,
) -> tuple[set[str], CheckResult]:
    command = ["/bin/bash", str(gradlew_path), "tasks", "--all", "--console=plain"]
    returncode, stdout, stderr, timed_out = run_command(
        command,
        project_root,
        timeout_seconds=120,
        env=command_env,
    )

    if timed_out:
        return set(), CheckResult(
            name="gradle-task-discovery",
            status="WARN",
            message="Gradle task discovery timed out after 120s.",
            command=" ".join(command),
        )

    if returncode != 0:
        return set(), CheckResult(
            name="gradle-task-discovery",
            status="WARN",
            message=f"Could not list Gradle tasks: {summarize_output(stdout, stderr)}",
            command=" ".join(command),
        )

    task_names: set[str] = set()
    for line in stdout.splitlines():
        match = re.match(r"^([A-Za-z0-9:_-]+)\s+-\s+", line)
        if match:
            task_names.add(match.group(1))

    return task_names, CheckResult(
        name="gradle-task-discovery",
        status="PASS",
        message=f"Discovered {len(task_names)} Gradle task(s).",
        command=" ".join(command),
    )


def resolve_gradle_runner(
    project_root: Path,
    wpilib_vscode_root: Path | None,
) -> tuple[Path | None, CheckResult]:
    project_gradlew = project_root / "gradlew"
    if project_gradlew.exists():
        return project_gradlew, CheckResult(
            name="gradle-wrapper",
            status="PASS",
            message=f"Found project gradlew at {project_gradlew}.",
        )

    build_files = ("build.gradle", "build.gradle.kts")
    has_build_file = any((project_root / filename).exists() for filename in build_files)
    if not has_build_file:
        return None, CheckResult(
            name="gradle-wrapper",
            status="SKIP",
            message="No gradlew and no build.gradle/build.gradle.kts found; skipped Gradle validation.",
        )

    shared_gradlew = find_shared_wpilib_gradlew(wpilib_vscode_root)
    if shared_gradlew is not None:
        return shared_gradlew, CheckResult(
            name="gradle-wrapper",
            status="PASS",
            message=f"Using WPILib shared gradlew from {shared_gradlew}.",
        )

    if wpilib_vscode_root is not None:
        return None, CheckResult(
            name="gradle-wrapper",
            status="WARN",
            message=(
                "WPILib VS Code root was provided, but shared gradlew was not found there. "
                "Ask the user to confirm the WPILib VS Code install path."
            ),
        )

    return None, CheckResult(
        name="gradle-wrapper",
        status="SKIP",
        message=(
            "Project has build.gradle but no gradlew. Ask the user where WPILib VS Code is installed "
            "and rerun with --wpilib-vscode-root."
        ),
    )


def validate_structure(project_root: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    package_root = project_root / "src" / "main" / "java" / "frc" / "robot"
    robot_path = package_root / "Robot.java"
    container_path = package_root / "RobotContainer.java"
    commands_dir = package_root / "commands"
    auto_routines_path = commands_dir / "AutoRoutines.java"
    subsystems_dir = package_root / "subsystems"
    constants_dir = package_root / "constants"

    if not package_root.exists():
        return [
            CheckResult(
                name="source-layout",
                status="FAIL",
                message=f"Missing expected package root: {package_root}",
            )
        ]

    results.append(
        CheckResult(
            name="source-layout",
            status="PASS",
            message=f"Found source layout under {package_root}.",
        )
    )

    if robot_path.exists():
        results.append(
            CheckResult(name="robot-file", status="PASS", message="Found Robot.java.")
        )
        robot_text = load_text(robot_path)
    else:
        results.append(
            CheckResult(name="robot-file", status="FAIL", message="Missing Robot.java.")
        )
        robot_text = ""

    if container_path.exists():
        results.append(
            CheckResult(
                name="robot-container-file",
                status="PASS",
                message="Found RobotContainer.java.",
            )
        )
        container_text = load_text(container_path)
    else:
        results.append(
            CheckResult(
                name="robot-container-file",
                status="FAIL",
                message="Missing RobotContainer.java.",
            )
        )
        container_text = ""

    auto_routines_text = load_text(auto_routines_path) if auto_routines_path.exists() else ""
    has_declarative_auto = (
        "autoRoutines.configure()" in container_text
        and "RobotModeTriggers.autonomous()" in auto_routines_text
    )

    if robot_text:
        if "CommandScheduler.getInstance().run()" in robot_text:
            results.append(
                CheckResult(
                    name="robot-scheduler",
                    status="PASS",
                    message="Robot.java runs the command scheduler.",
                )
            )
        else:
            results.append(
                CheckResult(
                    name="robot-scheduler",
                    status="FAIL",
                    message="Robot.java does not appear to run the command scheduler.",
                )
            )

        if "RobotContainer" in robot_text:
            results.append(
                CheckResult(
                    name="robot-container-ownership",
                    status="PASS",
                    message="Robot.java references RobotContainer.",
                )
            )
        else:
            results.append(
                CheckResult(
                    name="robot-container-ownership",
                    status="FAIL",
                    message="Robot.java does not appear to own a RobotContainer.",
                )
            )

        direct_controller_tokens = (
            "CommandXboxController",
            "Joystick",
            "XboxController",
            "PS4Controller",
            "PS5Controller",
        )
        if any(token in robot_text for token in direct_controller_tokens):
            results.append(
                CheckResult(
                    name="robot-controller-leak",
                    status="WARN",
                    message="Robot.java appears to reference controller types directly.",
                )
            )
        else:
            results.append(
                CheckResult(
                    name="robot-controller-leak",
                    status="PASS",
                    message="Robot.java does not appear to own controller bindings.",
                )
            )

        if "teleopInit" in robot_text and ".cancel()" in robot_text:
            results.append(
                CheckResult(
                    name="autonomous-handoff",
                    status="PASS",
                    message="Robot.java appears to cancel or replace autonomous in teleop.",
                )
            )
        elif has_declarative_auto:
            results.append(
                CheckResult(
                    name="autonomous-handoff",
                    status="PASS",
                    message="Autonomous handoff appears to be managed declaratively through AutoRoutines.",
                )
            )
        else:
            results.append(
                CheckResult(
                    name="autonomous-handoff",
                    status="WARN",
                    message="Could not confirm autonomous handoff behavior in teleopInit().",
                )
            )

    if container_text:
        if "getAutonomousCommand(" in container_text:
            results.append(
                CheckResult(
                    name="autonomous-entrypoint",
                    status="PASS",
                    message="RobotContainer exposes getAutonomousCommand().",
                )
            )
        elif has_declarative_auto:
            results.append(
                CheckResult(
                    name="autonomous-entrypoint",
                    status="PASS",
                    message="RobotContainer configures declarative autonomous routines through AutoRoutines.",
                )
            )
        else:
            results.append(
                CheckResult(
                    name="autonomous-entrypoint",
                    status="WARN",
                    message="RobotContainer does not expose getAutonomousCommand().",
                )
            )

        if "configureBindings()" in container_text:
            results.append(
                CheckResult(
                    name="bindings-entrypoint",
                    status="PASS",
                    message="RobotContainer has a bindings configuration entrypoint.",
                )
            )
        else:
            results.append(
                CheckResult(
                    name="bindings-entrypoint",
                    status="WARN",
                    message="RobotContainer does not appear to configure bindings explicitly.",
                )
            )

    results.append(
        CheckResult(
            name="commands-package",
            status="PASS" if commands_dir.exists() else "WARN",
            message="Found commands package."
            if commands_dir.exists()
            else "Missing commands package.",
        )
    )
    results.append(
        CheckResult(
            name="subsystems-package",
            status="PASS" if subsystems_dir.exists() else "WARN",
            message="Found subsystems package."
            if subsystems_dir.exists()
            else "Missing subsystems package.",
        )
    )
    results.append(
        CheckResult(
            name="constants-package",
            status="PASS" if constants_dir.exists() else "WARN",
            message="Found constants package."
            if constants_dir.exists()
            else "Missing constants package.",
        )
    )

    placeholder_hits: list[str] = []
    for java_file in package_root.rglob("*.java"):
        text = load_text(java_file)
        hit_count = sum(text.count(token) for token in PLACEHOLDER_TOKENS)
        if hit_count:
            placeholder_hits.append(f"{java_file.relative_to(project_root)} ({hit_count})")

    if placeholder_hits:
        results.append(
            CheckResult(
                name="placeholders",
                status="WARN",
                message=(
                    "Found placeholder markers or TODOs in: "
                    + ", ".join(placeholder_hits[:5])
                    + (" ..." if len(placeholder_hits) > 5 else "")
                ),
            )
        )
    else:
        results.append(
            CheckResult(
                name="placeholders",
                status="PASS",
                message="No known generated placeholder markers were found.",
            )
        )

    return results


def validate_gradle(
    project_root: Path,
    java_home: Path | None,
    wpilib_vscode_root: Path | None,
    skip_build: bool,
    run_sim: bool,
    sim_timeout_seconds: int,
) -> list[CheckResult]:
    results: list[CheckResult] = []
    command_env = build_command_env(java_home)

    results.append(validate_java_runtime(project_root, java_home))
    gradlew_path, gradlew_result = resolve_gradle_runner(project_root, wpilib_vscode_root)
    results.append(gradlew_result)
    if gradlew_path is None:
        return results

    tasks, discovery_result = discover_gradle_tasks(project_root, gradlew_path, command_env)
    results.append(discovery_result)

    if skip_build:
        results.append(
            CheckResult(
                name="gradle-build",
                status="SKIP",
                message="Build execution was skipped by request.",
            )
        )
    else:
        build_task = choose_first_available(tasks, BUILD_TASK_CANDIDATES) or "build"
        command = ["/bin/bash", str(gradlew_path), build_task, "--console=plain"]
        returncode, stdout, stderr, timed_out = run_command(
            command,
            project_root,
            timeout_seconds=900,
            env=command_env,
        )

        if timed_out:
            results.append(
                CheckResult(
                    name="gradle-build",
                    status="FAIL",
                    message=f"{build_task} timed out after 900s.",
                    command=" ".join(command),
                )
            )
        elif returncode == 0:
            results.append(
                CheckResult(
                    name="gradle-build",
                    status="PASS",
                    message=f"{build_task} passed.",
                    command=" ".join(command),
                )
            )
        else:
            results.append(
                CheckResult(
                    name="gradle-build",
                    status="FAIL",
                    message=f"{build_task} failed: {summarize_output(stdout, stderr)}",
                    command=" ".join(command),
                )
            )

    sim_task = choose_first_available(tasks, SIM_TASK_CANDIDATES)
    if not sim_task:
        results.append(
            CheckResult(
                name="gradle-sim",
                status="SKIP",
                message="No known desktop simulation task was discovered.",
            )
        )
        return results

    if not run_sim:
        results.append(
            CheckResult(
                name="gradle-sim",
                status="SKIP",
                message=f"Simulation task available but not run by default: {sim_task}.",
            )
        )
        return results

    command = ["/bin/bash", str(gradlew_path), sim_task, "--console=plain"]
    returncode, stdout, stderr, timed_out = run_command(
        command,
        project_root,
        timeout_seconds=sim_timeout_seconds,
        env=command_env,
    )

    if timed_out:
        results.append(
            CheckResult(
                name="gradle-sim",
                status="WARN",
                message=f"{sim_task} timed out after {sim_timeout_seconds}s; inspect manually.",
                command=" ".join(command),
            )
        )
    elif returncode == 0:
        results.append(
            CheckResult(
                name="gradle-sim",
                status="PASS",
                message=f"{sim_task} completed successfully.",
                command=" ".join(command),
            )
        )
    else:
        results.append(
            CheckResult(
                name="gradle-sim",
                status="FAIL",
                message=f"{sim_task} failed: {summarize_output(stdout, stderr)}",
                command=" ".join(command),
            )
        )

    return results


def overall_status(results: list[CheckResult]) -> str:
    if not results:
        return "SKIP"
    return max(results, key=lambda result: STATUS_PRIORITY[result.status]).status


def print_report(project_root: Path, results: list[CheckResult]) -> None:
    print(f"Validation report for {project_root}")
    print()
    for result in results:
        print(f"[{result.status}] {result.name}: {result.message}")
        if result.command:
            print(f"  command: {result.command}")

    print()
    print(f"Overall status: {overall_status(results)}")


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).expanduser().resolve()
    wpilib_vscode_root = resolve_wpilib_vscode_root(args.wpilib_vscode_root)
    java_home = resolve_java_home(args.java_home)
    if java_home is None:
        java_home = infer_java_home_from_wpilib_root(wpilib_vscode_root)

    if not project_root.exists():
        raise FileNotFoundError(f"Project root does not exist: {project_root}")

    results: list[CheckResult] = []
    if args.skip_structure:
        results.append(
            CheckResult(
                name="structure-checks",
                status="SKIP",
                message="Structure validation was skipped by request.",
            )
        )
    else:
        results.extend(validate_structure(project_root))

    results.extend(
        validate_gradle(
            project_root,
            java_home,
            wpilib_vscode_root,
            skip_build=args.skip_build,
            run_sim=args.run_sim,
            sim_timeout_seconds=args.sim_timeout_seconds,
        )
    )

    print_report(project_root, results)
    return 1 if overall_status(results) == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
