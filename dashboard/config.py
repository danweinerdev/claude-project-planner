"""Configuration loading and repository URL helpers."""

import json
from pathlib import Path

from .models import PlanData


def load_config(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, IOError):
        return {}


def get_repo_url(config: dict, repo_key: str) -> str:
    """Get GitHub URL for a repository by key."""
    repos = config.get("repositories", {})
    if repo_key in repos:
        github = repos[repo_key].get("github", "")
        if github:
            return f"https://github.com/{github}"
    return ""


def get_planning_repo_url(config: dict) -> str:
    """Get the GitHub URL for the planning repository."""
    plan_repo = config.get("planRepository", "")
    if not plan_repo:
        return ""
    return get_repo_url(config, plan_repo)


def apply_config_to_plans(plans: list[PlanData], config: dict) -> None:
    """Apply configuration to plans (target repos, etc.)."""
    plan_mapping = config.get("planMapping", {})

    for plan in plans:
        if plan.name in plan_mapping:
            mapping = plan_mapping[plan.name]
            repo_key = mapping.get("repo", "")
            if repo_key:
                plan.target_repo = repo_key
                plan.target_repo_url = get_repo_url(config, repo_key)
