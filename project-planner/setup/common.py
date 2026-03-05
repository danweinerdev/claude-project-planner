"""Shared utilities for repository setup tools.

Provides config loading, path resolution, planning config management,
symlink cleanup, and launcher script generation.
"""

import json
import os
import platform
import stat
import subprocess
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


def detect_repo_type(repo_path: Path) -> str:
    """Detect whether a path is a normal repo, worktree, or bare repo.

    Returns "normal", "worktree", or "bare".
    Raises ValueError if the path is not a git repository.
    """
    # .git is a file → worktree
    git_path = repo_path / ".git"
    if git_path.is_file():
        return "worktree"

    # .bare/ directory → bare (convention used by worktree setups)
    if (repo_path / ".bare").is_dir():
        return "bare"

    # Check via git if it's a bare repo
    result = subprocess.run(
        ["git", "-C", str(repo_path), "rev-parse", "--is-bare-repository"],
        capture_output=True, text=True,
    )
    if result.returncode == 0 and result.stdout.strip() == "true":
        return "bare"

    # .git is a directory → normal repo
    if git_path.is_dir():
        return "normal"

    raise ValueError(f"Not a git repository: {repo_path}")


def find_sibling_config(repo_path: Path) -> dict | None:
    """Search sibling worktrees for an existing planning-config.json.

    Returns {"planningRoot": str, "dashboard": bool, "source": str} or None.
    """
    result = subprocess.run(
        ["git", "-C", str(repo_path), "worktree", "list", "--porcelain"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return None

    own_path = repo_path.resolve()
    siblings = []
    for line in result.stdout.splitlines():
        if line.startswith("worktree "):
            wt_path = Path(line.split(" ", 1)[1])
            if wt_path.resolve() != own_path:
                siblings.append(wt_path)

    for wt in siblings:
        config_file = wt / "planning-config.json"
        if config_file.is_file():
            try:
                data = json.loads(config_file.read_text())
                return {
                    "planningRoot": data.get("planningRoot", ""),
                    "dashboard": data.get("dashboard", True),
                    "source": str(wt),
                }
            except (json.JSONDecodeError, IOError):
                continue

    return None


def setup_planning_config(
    target_path: Path,
    planning_root: Path,
    *,
    dashboard: bool = True,
) -> None:
    """Write or overwrite planning-config.json in the target directory."""
    config_file = target_path / "planning-config.json"
    expected = {"mode": "standalone", "planningRoot": str(planning_root)}
    if not dashboard:
        expected["dashboard"] = False

    if config_file.exists():
        try:
            existing = json.loads(config_file.read_text())
            if (
                existing.get("planningRoot") == str(planning_root)
                and existing.get("dashboard", True) == dashboard
            ):
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


PLANNING_DIRS = ["Plans", "Research", "Brainstorm", "Specs", "Designs", "Retro", "Shared"]

GITIGNORE_ENTRIES_DASHBOARD = [
    "# Generated dashboard",
    "Dashboard/",
    "",
]

GITIGNORE_ENTRIES_BASE = [
    "# Local config (paths, not committed)",
    "planning-config.local.json",
    "",
    "# Python",
    "__pycache__/",
    "*.py[cod]",
]


def create_planning_dirs(planning_root: Path) -> list[str]:
    """Create artifact directories under planning_root if they don't exist.

    Returns list of directory names that were created.
    """
    created = []
    for name in PLANNING_DIRS:
        dir_path = planning_root / name
        if not dir_path.is_dir():
            dir_path.mkdir(parents=True, exist_ok=True)
            created.append(name)
    return created


def setup_gitignore(planning_root: Path, *, dashboard: bool = True) -> bool:
    """Ensure planning-related entries are in .gitignore.

    Appends missing entries to an existing .gitignore or creates a new one.
    Returns True if the file was modified.
    """
    entries = (GITIGNORE_ENTRIES_DASHBOARD if dashboard else []) + GITIGNORE_ENTRIES_BASE
    gitignore = planning_root / ".gitignore"
    existing = gitignore.read_text() if gitignore.is_file() else ""
    existing_lines = existing.splitlines()

    missing = []
    for entry in entries:
        if entry and entry not in existing_lines:
            missing.append(entry)

    if not missing:
        return False

    separator = "\n" if existing and not existing.endswith("\n") else ""
    prefix = "\n" if existing.strip() else ""
    gitignore.write_text(existing + separator + prefix + "\n".join(entries) + "\n")
    return True


def is_external_path(child: Path, parent: Path) -> bool:
    """Check if child is outside parent (i.e. not equal to or under parent)."""
    try:
        child.resolve().relative_to(parent.resolve())
        return False
    except ValueError:
        return True


def write_launcher(target_path: Path, planning_root: Path, planner_dir: Path) -> None:
    """Write a cross-platform Claude launcher script. Overwrites any existing launcher.

    Only includes --add-dir for the planning root if it is external to the
    target repo (i.e. planning artifacts live outside the repository).
    """
    is_windows = platform.system() == "Windows"
    launcher = target_path / ("claude.cmd" if is_windows else "claude.sh")
    existed = launcher.exists()
    needs_add_dir = is_external_path(planning_root, target_path)

    if is_windows:
        parts = ["claude"]
        if needs_add_dir:
            parts.append(f'--add-dir="{planning_root}"')
        parts.append(f'--plugin-dir="{planner_dir}"')
        parts.append("%*")
        lines = ["@echo off", " ".join(parts), ""]
        launcher.write_text("\r\n".join(lines))
    else:
        lines = [
            "#!/usr/bin/env bash",
            "# Launch Claude Code with planner plugin",
            "exec claude \\",
        ]
        if needs_add_dir:
            lines.append(f'    --add-dir="{planning_root}" \\')
        lines.append(f'    --plugin-dir="{planner_dir}" \\')
        lines.append('    "$@"')
        lines.append("")
        launcher.write_text("\n".join(lines))
        mode = launcher.stat().st_mode
        launcher.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    print(f"{launcher.name}: {'overwritten' if existed else 'written'}")
