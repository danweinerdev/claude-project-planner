"""Configure a git repository (normal or worktree) for project-planner integration."""

import argparse
import platform
import sys
from pathlib import Path

from .common import (
    PLANNER_DIR,
    clean_stale_copies,
    clean_stale_symlinks,
    detect_repo_type,
    find_sibling_config,
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

    # Detect repo type
    try:
        repo_type = detect_repo_type(repo_path)
    except ValueError:
        print(f"Error: {repo_path} is not a git repository", file=sys.stderr)
        sys.exit(1)

    if repo_type == "bare":
        print(f"Error: {repo_path} is a bare repository.", file=sys.stderr)
        print("  Run setup on individual worktrees instead:", file=sys.stderr)
        print(f"  e.g., python3 {PLANNER_DIR}/setup-repo.py {repo_path}/<worktree>", file=sys.stderr)
        sys.exit(1)

    # Resolve planning root: explicit flag > sibling config > default
    if args.planning_root:
        planning_root = args.planning_root.resolve()
    elif repo_type == "worktree":
        sibling = find_sibling_config(repo_path)
        if sibling and sibling["planningRoot"]:
            planning_root = Path(sibling["planningRoot"])
            if not planning_root.is_absolute():
                planning_root = planning_root.resolve()
            print(f"Inheriting planningRoot from sibling worktree: {sibling['source']}")
        else:
            planning_root = PLANNER_DIR.resolve()
    else:
        planning_root = PLANNER_DIR.resolve()

    # 1. Planning config
    setup_planning_config(repo_path, planning_root)

    # 2. Clean stale symlinks
    cleaned = clean_stale_symlinks(repo_path, PLANNER_DIR)
    if cleaned:
        print(f"Cleaned {cleaned} stale planner symlinks")

    # 3. Clean stale skill/agent copies
    removed = clean_stale_copies(repo_path, PLANNER_DIR)
    if removed:
        print(f"Cleaned {removed} stale planner file copies (now provided by marketplace plugin)")

    # 4. Launcher script
    write_launcher(repo_path, planning_root)

    # Summary
    label = "Worktree configured" if repo_type == "worktree" else "Repo configured"
    print()
    print(f"=== {label}: {repo_path.name} ===")
    print(f"  Path:     {repo_path}")
    print(f"  Planning: {planning_root}")
    print()
    launcher = "claude.cmd" if platform.system() == "Windows" else "./claude.sh"
    print(f"  cd {repo_path} && {launcher}")
