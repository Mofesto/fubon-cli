#!/usr/bin/env python3
"""Build skill bundle artifacts for publication.

Outputs:
- dist/skill/SKILL.md
- dist/skill/skill.manifest.json
- dist/skill/fubon-cli-skill-<version>.zip
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def get_git_commit() -> str:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
        return out.decode("utf-8").strip()
    except Exception:
        return "unknown"


def get_version(explicit: str | None) -> str:
    if explicit:
        return explicit

    ref_name = os.getenv("GITHUB_REF_NAME", "")
    if ref_name.startswith("v") and len(ref_name) > 1:
        return ref_name[1:]

    try:
        from fubon_cli import __version__  # pylint: disable=import-outside-toplevel

        return __version__
    except Exception:
        return "0.0.0"


def sha256sum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build fubon-cli skill bundle")
    parser.add_argument("--skill-file", default="SKILL.md", help="Skill markdown file path")
    parser.add_argument("--output-dir", default="dist/skill", help="Bundle output directory")
    parser.add_argument("--version", default=None, help="Override skill version")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    skill_file = Path(args.skill_file)
    out_dir = Path(args.output_dir)

    if not skill_file.exists():
        print(f"Skill file not found: {skill_file}")
        return 1

    version = get_version(args.version)
    commit = get_git_commit()

    out_dir.mkdir(parents=True, exist_ok=True)

    skill_copy = out_dir / "SKILL.md"
    shutil.copy2(skill_file, skill_copy)

    manifest = {
        "name": "fubon-cli",
        "slug": "fubon-cli",
        "version": version,
        "description": "AI-agent-friendly CLI skill for Fubon Neo trading workflows",
        "entrypoint": "fubon",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": {
            "repository": "https://github.com/Mofesto/fubon-cli",
            "commit": commit,
        },
        "artifacts": {
            "skill_md": "SKILL.md",
            "skill_md_sha256": sha256sum(skill_copy),
        },
    }

    manifest_path = out_dir / "skill.manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    zip_path = out_dir / f"fubon-cli-skill-{version}.zip"
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zf:
        zf.write(skill_copy, arcname="SKILL.md")
        zf.write(manifest_path, arcname="skill.manifest.json")

    print(f"Skill bundle built: {out_dir}")
    print(f"- {skill_copy}")
    print(f"- {manifest_path}")
    print(f"- {zip_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
