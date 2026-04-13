#!/usr/bin/env python3
"""Apply the base robot architecture overlay to a target project."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


TEXT_EXTENSIONS = {".java", ".md", ".txt", ".gradle", ".json", ".properties", ".xml", ".yml"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy the base FRC Java architecture overlay into a target repo."
    )
    parser.add_argument("--name", required=True, help="Robot or project name.")
    parser.add_argument("--team-number", required=True, type=int, help="FRC team number.")
    parser.add_argument(
        "--target",
        required=True,
        help="Target project root. The script will merge the template into this directory.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing files in the target tree when a path already exists.",
    )
    return parser.parse_args()


def is_text_file(path: Path) -> bool:
    return path.suffix in TEXT_EXTENSIONS


def replace_tokens(contents: str, robot_name: str, team_number: int) -> str:
    return (
        contents.replace("__ROBOT_NAME__", robot_name).replace("__TEAM_NUMBER__", str(team_number))
    )


def copy_tree(
    template_root: Path,
    target_root: Path,
    robot_name: str,
    team_number: int,
    overwrite: bool,
) -> None:
    for source in template_root.rglob("*"):
        if source.is_dir():
            continue

        relative_path = source.relative_to(template_root)
        destination = target_root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)

        if destination.exists() and not overwrite:
            raise FileExistsError(
                f"Refusing to overwrite existing file without --overwrite: {destination}"
            )

        if is_text_file(source):
            text = source.read_text(encoding="utf-8")
            destination.write_text(
                replace_tokens(text, robot_name, team_number),
                encoding="utf-8",
            )
        else:
            shutil.copy2(source, destination)


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    template_root = repo_root / "templates" / "wpilib-java-base"
    target_root = Path(args.target).expanduser().resolve()

    if not template_root.exists():
        raise FileNotFoundError(f"Missing template root: {template_root}")

    target_root.mkdir(parents=True, exist_ok=True)
    copy_tree(template_root, target_root, args.name, args.team_number, args.overwrite)

    print(f"Applied starter architecture to {target_root}")
    print("Next steps:")
    print("  1. Merge or verify GradleRIO and vendor dependencies in the target repo.")
    print("  2. Add your first real mechanism with scripts/add_mechanism.py.")
    print("  3. Register your first real auto routine in src/main/java/frc/robot/commands/AutoRoutines.java.")
    print("  4. Run the validation checklist in references/validation-checklist.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
