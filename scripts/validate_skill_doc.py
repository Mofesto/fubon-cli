#!/usr/bin/env python3
"""Validate SKILL.md quality and CLI coverage.

This script keeps the skill document tightly bound to the actual CLI surface.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED_TOKENS = [
    "fubon login",
    "fubon stock",
    "fubon account",
    "fubon market",
    "fubon realtime",
    "fubon futopt",
    "fubon condition",
    "fubon ask",
    "fubon chat",
    "fubon config",
]

REQUIRED_SECTIONS = [
    "# fubon-cli Skill",
    "## Command Surface",
    "## Output Contract",
    "## Version Binding",
]


def validate_skill_file(path: Path) -> list[str]:
    errors: list[str] = []

    if not path.exists():
        return [f"Missing file: {path}"]

    content = path.read_text(encoding="utf-8")

    for section in REQUIRED_SECTIONS:
        if section not in content:
            errors.append(f"Missing required section: {section}")

    for token in REQUIRED_TOKENS:
        pattern = rf"\b{re.escape(token)}\b"
        if not re.search(pattern, content):
            errors.append(f"Missing CLI coverage token: {token}")

    if "\"success\"" not in content or "\"error\"" not in content:
        errors.append("Output contract examples must include success/error keys")

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate SKILL.md format and CLI coverage")
    parser.add_argument(
        "--skill-file",
        default="SKILL.md",
        help="Path to skill markdown file (default: SKILL.md)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    skill_path = Path(args.skill_file)

    errors = validate_skill_file(skill_path)
    if errors:
        print("Skill validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    print(f"Skill validation passed: {skill_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
