"""Configure a git repository for project-planner integration."""

import argparse
import platform
import sys
from pathlib import Path

from .common import (
    PLANNER_DIR,
    clean_stale_symlinks,
    create_planning_dirs,
    detect_repo_type,
    find_sibling_config,
    resolve_repo_path,
    setup_gitignore,
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
    parser.add_argument(
        "--no-dashboard",
        action="store_true",
        default=False,
        help="disable dashboard generation in planning-config.json",
    )

    args = parser.parse_args(argv)

    repo_path = resolve_repo_path(args.repo)

    # Detect repo type
    try:
        repo_type = detect_repo_type(repo_path)
    except ValueError:
        print(f"Error: {repo_path} is not a git repository.", file=sys.stderr)
        sys.exit(1)

    if repo_type == "bare":
        print(f"Error: {repo_path} is a bare repository.", file=sys.stderr)
        print("  Run setup on individual worktrees instead.", file=sys.stderr)
        print("  Example: python3 setup-repo.py /path/to/worktree", file=sys.stderr)
        sys.exit(1)

    # Resolve config: explicit CLI flags > sibling discovery > defaults
    sibling = None
    if repo_type == "worktree" and args.planning_root is None:
        sibling = find_sibling_config(repo_path)

    if args.planning_root is not None:
        planning_root = args.planning_root.resolve()
    elif sibling:
        planning_root = Path(sibling["planningRoot"]).resolve()
        print(f"Inheriting planningRoot from sibling: {sibling['source']}")
    else:
        planning_root = PLANNER_DIR.resolve()

    if args.no_dashboard:
        dashboard = False
    elif sibling:
        dashboard = sibling["dashboard"]
    else:
        dashboard = True

    # 1. Planning config
    setup_planning_config(repo_path, planning_root, dashboard=dashboard)

    # 2. Bootstrap planning directories
    created_dirs = create_planning_dirs(planning_root)
    if created_dirs:
        print(f"Created directories: {', '.join(created_dirs)}")

    # 3. Set up .gitignore
    if setup_gitignore(planning_root, dashboard=dashboard):
        print(".gitignore: updated")

    # 4. Clean stale symlinks (legacy migration)
    cleaned = clean_stale_symlinks(repo_path, PLANNER_DIR)
    if cleaned:
        print(f"Cleaned {cleaned} stale planner symlinks")

    # 5. Launcher script
    write_launcher(repo_path, planning_root, PLANNER_DIR)

    # Summary
    label = "Worktree configured" if repo_type == "worktree" else "Repo configured"
    print()
    print(f"=== {label}: {repo_path.name} ===")
    print(f"  Path:     {repo_path}")
    print(f"  Planning: {planning_root}")
    print(f"  Plugin:   {PLANNER_DIR}")
    print()
    launcher = "claude.cmd" if platform.system() == "Windows" else "./claude.sh"
    print(f"  cd {repo_path} && {launcher}")
