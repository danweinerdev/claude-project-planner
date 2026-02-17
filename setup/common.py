"""Shared utilities for repository setup tools.

Provides config loading, path resolution, planning config management,
symlink cleanup, and launcher script generation.
"""

import json
import os
import platform
import stat
import sys
from pathlib import Path

# Auto-detect project-planner directory (setup/ -> project-planner/)
PLANNER_DIR = Path(__file__).resolve().parent.parent


def load_json(path: Path) -> dict:
    """Load a JSON file, returning {} on any error."""
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, IOError):
        return {}


def resolve_repo_path(repo_arg: str, planner_dir: Path = PLANNER_DIR) -> Path:
    """Resolve a repo argument to an absolute path.

    If repo_arg is an existing directory, use it directly.
    Otherwise, look it up as a key in planning-config.local.json.
    """
    candidate = Path(repo_arg).resolve()
    if candidate.is_dir():
        return candidate

    local_cfg = load_json(planner_dir / "planning-config.local.json")
    repos = local_cfg.get("repositories", {})
    if repo_arg in repos:
        repo_info = repos[repo_arg]
        path_str = repo_info.get("path", "") if isinstance(repo_info, dict) else repo_info
        if path_str:
            resolved = Path(path_str).resolve()
            if resolved.is_dir():
                return resolved
            print(f"Error: configured path for '{repo_arg}' does not exist: {path_str}", file=sys.stderr)
            sys.exit(1)

    print(f"Error: '{repo_arg}' is not a directory and was not found in planning-config.local.json", file=sys.stderr)
    sys.exit(1)


def setup_planning_config(target_path: Path, planning_root: Path) -> None:
    """Write or overwrite planning-config.json in the target directory."""
    config_file = target_path / "planning-config.json"
    expected = {"mode": "standalone", "planningRoot": str(planning_root)}

    if config_file.exists():
        try:
            existing = json.loads(config_file.read_text())
            if existing.get("planningRoot") == str(planning_root):
                print("planning-config.json: OK")
                return
            print(f"Overwriting planning-config.json (was: {existing.get('planningRoot', '')})")
        except (json.JSONDecodeError, IOError):
            print("Overwriting planning-config.json (was corrupt)")
    else:
        print("Creating planning-config.json")

    config_file.write_text(json.dumps(expected, indent=2) + "\n")


def clean_stale_symlinks(target_path: Path, planner_dir: Path) -> int:
    """Remove symlinks that point into the planner directory (legacy setup)."""
    cleaned = 0
    for subdir in ("skills", "agents"):
        dir_path = target_path / ".claude" / subdir
        if not dir_path.is_dir():
            continue
        for link in dir_path.glob("*.md"):
            if link.is_symlink():
                try:
                    target = Path(os.readlink(str(link)))
                    if str(target).startswith(str(planner_dir)):
                        link.unlink()
                        cleaned += 1
                except OSError:
                    pass
    return cleaned


def write_launcher(target_path: Path, planning_root: Path, planner_dir: Path) -> None:
    """Write a cross-platform Claude launcher script. Overwrites any existing launcher."""
    is_windows = platform.system() == "Windows"
    launcher = target_path / ("claude.cmd" if is_windows else "claude.sh")
    existed = launcher.exists()

    if is_windows:
        lines = [
            "@echo off",
            f'claude --add-dir="{planning_root}" --plugin-dir="{planner_dir}" %*',
            "",
        ]
        launcher.write_text("\r\n".join(lines))
    else:
        lines = [
            "#!/usr/bin/env bash",
            "# Launch Claude Code with planning context and planner plugin",
            "exec claude \\",
            f'    --add-dir="{planning_root}" \\',
            f'    --plugin-dir="{planner_dir}" \\',
            '    "$@"',
            "",
        ]
        launcher.write_text("\n".join(lines))
        mode = launcher.stat().st_mode
        launcher.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    print(f"{launcher.name}: {'overwritten' if existed else 'written'}")
