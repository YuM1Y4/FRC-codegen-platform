#!/usr/bin/env python3
"""Insert binding or default-command snippets at a marker in RobotContainer.java."""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Insert a snippet before a marker comment.")
    parser.add_argument("--file", required=True, help="File to edit, usually RobotContainer.java.")
    parser.add_argument("--marker", required=True, help='Marker text, for example "__BINDINGS__".')
    parser.add_argument("--snippet", help="Inline snippet to insert.")
    parser.add_argument("--snippet-file", help="Path to a file that contains the snippet.")
    return parser.parse_args()


def load_snippet(args: argparse.Namespace) -> str:
    if args.snippet_file:
        return Path(args.snippet_file).read_text().rstrip()
    if args.snippet:
        return args.snippet.rstrip()
    raise ValueError("Provide either --snippet or --snippet-file.")


def main() -> int:
    args = parse_args()
    target = Path(args.file).expanduser().resolve()
    snippet = load_snippet(args)
    contents = target.read_text().splitlines()

    for index, line in enumerate(contents):
        if args.marker in line:
            indent = line[: len(line) - len(line.lstrip())]
            formatted = [f"{indent}{snippet_line}" if snippet_line else "" for snippet_line in snippet.splitlines()]
            contents[index:index] = formatted
            target.write_text("\n".join(contents) + "\n")
            print(f"Inserted snippet at marker {args.marker} in {target}")
            return 0

    raise ValueError(f"Marker not found in {target}: {args.marker}")


if __name__ == "__main__":
    raise SystemExit(main())
