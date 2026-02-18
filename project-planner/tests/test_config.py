"""Tests for configuration loading and helpers."""

import json
from dashboard.config import (
    load_config,
    get_repo_url,
    get_planning_repo_url,
    apply_config_to_plans,
)
from dashboard.models import PlanData


class TestLoadConfig:
    def test_missing_file(self, tmp_path):
        result = load_config(tmp_path / "nonexistent.json")
        assert result == {}

    def test_valid_json(self, tmp_path):
        cfg = tmp_path / "config.json"
        cfg.write_text(json.dumps({"title": "Test", "mode": "standalone"}))
        result = load_config(cfg)
        assert result["title"] == "Test"
        assert result["mode"] == "standalone"

    def test_invalid_json(self, tmp_path):
        cfg = tmp_path / "bad.json"
        cfg.write_text("not valid json {{{")
        result = load_config(cfg)
        assert result == {}

    def test_empty_file(self, tmp_path):
        cfg = tmp_path / "empty.json"
        cfg.write_text("")
        result = load_config(cfg)
        assert result == {}


class TestGetRepoUrl:
    def test_existing_key(self):
        config = {
            "repositories": {
                "ark": {"github": "user/ark"}
            }
        }
        assert get_repo_url(config, "ark") == "https://github.com/user/ark"

    def test_missing_key(self):
        config = {"repositories": {"ark": {"github": "user/ark"}}}
        assert get_repo_url(config, "nonexistent") == ""

    def test_no_github_field(self):
        config = {"repositories": {"ark": {"path": "/local"}}}
        assert get_repo_url(config, "ark") == ""

    def test_no_repositories(self):
        assert get_repo_url({}, "ark") == ""


class TestGetPlanningRepoUrl:
    def test_with_plan_repository(self):
        config = {
            "planRepository": "planning",
            "repositories": {
                "planning": {"github": "user/planning"}
            }
        }
        assert get_planning_repo_url(config) == "https://github.com/user/planning"

    def test_without_plan_repository(self):
        assert get_planning_repo_url({}) == ""

    def test_plan_repository_not_in_repos(self):
        config = {
            "planRepository": "planning",
            "repositories": {}
        }
        assert get_planning_repo_url(config) == ""


class TestApplyConfigToPlans:
    def test_mapping_present(self):
        plans = [PlanData(name="MyPlan")]
        config = {
            "planMapping": {
                "MyPlan": {"repo": "main-repo"}
            },
            "repositories": {
                "main-repo": {"github": "user/main-repo"}
            }
        }
        apply_config_to_plans(plans, config)
        assert plans[0].target_repo == "main-repo"
        assert plans[0].target_repo_url == "https://github.com/user/main-repo"

    def test_mapping_absent(self):
        plans = [PlanData(name="OtherPlan")]
        config = {
            "planMapping": {
                "MyPlan": {"repo": "main-repo"}
            },
            "repositories": {
                "main-repo": {"github": "user/main-repo"}
            }
        }
        apply_config_to_plans(plans, config)
        assert plans[0].target_repo == ""
        assert plans[0].target_repo_url == ""

    def test_no_mapping_config(self):
        plans = [PlanData(name="Plan")]
        apply_config_to_plans(plans, {})
        assert plans[0].target_repo == ""
