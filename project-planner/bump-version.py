#!/usr/bin/env python3
"""Bump the plugin version in both marketplace.json and plugin.json."""

import json
import sys
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parent
MARKETPLACE_JSON = PLUGIN_DIR.parent / ".claude-plugin" / "marketplace.json"
PLUGIN_JSON = PLUGIN_DIR / ".claude-plugin" / "plugin.json"


def bump(version: str, part: str) -> str:
    major, minor, patch = (int(x) for x in version.split("."))
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    if part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise ValueError(f"Unknown part: {part}")


def update_json(path: Path, new_version: str) -> None:
    data = json.loads(path.read_text())
    if "plugins" in data:
        data["plugins"][0]["version"] = new_version
    else:
        data["version"] = new_version
    path.write_text(json.dumps(data, indent=2) + "\n")


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in ("patch", "minor", "major"):
        print("Usage: bump-version.py <patch|minor|major>", file=sys.stderr)
        sys.exit(1)

    part = sys.argv[1]
    current = json.loads(PLUGIN_JSON.read_text())["version"]
    new_version = bump(current, part)

    update_json(PLUGIN_JSON, new_version)
    update_json(MARKETPLACE_JSON, new_version)

    print(new_version)


if __name__ == "__main__":
    main()
