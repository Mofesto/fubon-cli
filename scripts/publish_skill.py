#!/usr/bin/env python3
"""Publish skill bundle to clawhub-compatible endpoint.

Environment variables:
- CLAWHUB_API_TOKEN (required unless --dry-run)
- CLAWHUB_BASE_URL (default: https://clawhub.ai)
- CLAWHUB_PUBLISH_ENDPOINT (default: /api/v1/skills/publish)
- CLAWHUB_SKILL_SLUG (default: fubon-cli)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


def resolve_endpoint(base_url: str, endpoint: str) -> str:
    if endpoint.startswith("http://") or endpoint.startswith("https://"):
        return endpoint
    return base_url.rstrip("/") + "/" + endpoint.lstrip("/")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish skill bundle to clawhub")
    parser.add_argument("--bundle-dir", default="dist/skill", help="Bundle directory path")
    parser.add_argument("--dry-run", action="store_true", help="Print payload only, do not publish")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    bundle_dir = Path(args.bundle_dir)
    manifest_path = bundle_dir / "skill.manifest.json"
    skill_path = bundle_dir / "SKILL.md"

    if not manifest_path.exists() or not skill_path.exists():
        print("Bundle is incomplete. Run scripts/build_skill_bundle.py first.")
        return 1

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    skill_md = skill_path.read_text(encoding="utf-8")

    payload = {
        "slug": os.getenv("CLAWHUB_SKILL_SLUG", manifest.get("slug", "fubon-cli")),
        "version": manifest.get("version", "0.0.0"),
        "manifest": manifest,
        "skill_md": skill_md,
    }

    if args.dry_run:
        print("Dry run payload:")
        print(json.dumps(payload, indent=2, ensure_ascii=False)[:2000])
        return 0

    token = os.getenv("CLAWHUB_API_TOKEN")
    if not token:
        print("Missing CLAWHUB_API_TOKEN")
        return 1

    # Resolve base URL and endpoint with validation. Accept full endpoint URLs.
    base_url_env = os.getenv("CLAWHUB_BASE_URL")
    endpoint_env = os.getenv("CLAWHUB_PUBLISH_ENDPOINT")

    base_url = base_url_env if base_url_env and base_url_env.strip() else "https://clawhub.ai"
    endpoint = endpoint_env if endpoint_env and endpoint_env.strip() else "/api/v1/skills/publish"

    url = resolve_endpoint(base_url, endpoint)

    # Validate the resolved URL looks like an absolute HTTP(S) URL
    if not (url.startswith("http://") or url.startswith("https://")):
        print("Invalid publish URL resolved:", repr(url))
        print(
            "Check CLAWHUB_BASE_URL and CLAWHUB_PUBLISH_ENDPOINT environment variables."
        )
        return 1

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "fubon-cli-skill-publisher/1.0",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            print(f"Published skill to: {url}")
            print(f"Status: {resp.status}")
            print(body[:4000])
            return 0
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"HTTP error during publish: {exc.code}")
        print(body[:4000])
        return 1
    except urllib.error.URLError as exc:
        print(f"Network error during publish: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
