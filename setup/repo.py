"""Configure a normal git repository for project-planner integration."""

import argparse
import platform
from pathlib import Path

from .common import (
    PLANNER_DIR,
    clean_stale_symlinks,
    resolve_repo_path,
    setup_planning_config,
    write_launcher,
)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Configure a git repository for use with Claude project-planner.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  %(prog)s /path/to/my-project\n"
            "  %(prog)s /path/to/my-project --planning-root /path/to/planning-repo\n"
            "  %(prog)s my-project   # repo key from planning-config.local.json\n"
        ),
    )
    parser.add_argument(
        "repo",
        help="path to target git repository, or a key from planning-config.local.json",
    )
    parser.add_argument(
        "--planning-root",
        type=Path,
        default=None,
        help="path to planning artifacts (defaults to project-planner directory)",
    )

    args = parser.parse_args(argv)

    repo_path = resolve_repo_path(args.repo)
    planning_root = (args.planning_root or PLANNER_DIR).resolve()

    # 1. Planning config
    setup_planning_config(repo_path, planning_root)

    # 2. Clean stale symlinks
    cleaned = clean_stale_symlinks(repo_path, PLANNER_DIR)
    if cleaned:
        print(f"Cleaned {cleaned} stale planner symlinks (now using --add-dir)")

    # 3. Launcher script
    write_launcher(repo_path, planning_root, PLANNER_DIR)

    # Summary
    print()
    print(f"=== Repo configured: {repo_path.name} ===")
    print(f"  Path:     {repo_path}")
    print(f"  Planning: {planning_root}")
    print(f"  Plugin:   {PLANNER_DIR}")
    print()
    launcher = "claude.cmd" if platform.system() == "Windows" else "./claude.sh"
    print(f"  cd {repo_path} && {launcher}")
