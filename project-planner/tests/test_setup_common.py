"""Tests for setup.common shared utilities."""

import json
import os
import platform
import stat
from pathlib import Path
from unittest.mock import patch

import pytest

from setup.common import (
    PLANNER_DIR,
    clean_stale_symlinks,
    load_json,
    resolve_repo_path,
    setup_planning_config,
    write_launcher,
)


class TestPlannerDir:
    def test_points_to_project_root(self):
        assert (PLANNER_DIR / "setup" / "common.py").is_file()
        assert (PLANNER_DIR / "planning-config.json").is_file()


class TestLoadJson:
    def test_valid_json(self, tmp_path):
        f = tmp_path / "test.json"
        f.write_text(json.dumps({"key": "value"}))
        assert load_json(f) == {"key": "value"}

    def test_missing_file(self, tmp_path):
        assert load_json(tmp_path / "nope.json") == {}

    def test_invalid_json(self, tmp_path):
        f = tmp_path / "bad.json"
        f.write_text("{not valid")
        assert load_json(f) == {}

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.json"
        f.write_text("")
        assert load_json(f) == {}

    def test_directory_not_file(self, tmp_path):
        assert load_json(tmp_path) == {}


class TestResolveRepoPath:
    def test_existing_directory(self, tmp_path):
        result = resolve_repo_path(str(tmp_path))
        assert result == tmp_path.resolve()

    def test_config_key_lookup(self, tmp_path):
        repo_dir = tmp_path / "my-repo"
        repo_dir.mkdir()

        planner = tmp_path / "planner"
        planner.mkdir()
        local_cfg = planner / "planning-config.local.json"
        local_cfg.write_text(json.dumps({
            "repositories": {
                "my-repo": {"path": str(repo_dir)}
            }
        }))

        result = resolve_repo_path("my-repo", planner_dir=planner)
        assert result == repo_dir.resolve()

    def test_config_key_string_value(self, tmp_path):
        """Support plain string values in repositories map."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()

        planner = tmp_path / "planner"
        planner.mkdir()
        local_cfg = planner / "planning-config.local.json"
        # String value instead of dict — should still resolve via .get("path", "")
        # which returns "" for strings, so this won't resolve
        local_cfg.write_text(json.dumps({
            "repositories": {
                "repo": str(repo_dir)
            }
        }))

        # String value gets treated as repo_info directly; isinstance check
        # routes to the else branch which treats it as a path string
        result = resolve_repo_path("repo", planner_dir=planner)
        assert result == repo_dir.resolve()

    def test_nonexistent_path_no_config(self, tmp_path):
        planner = tmp_path / "planner"
        planner.mkdir()
        with pytest.raises(SystemExit):
            resolve_repo_path("/nonexistent/path", planner_dir=planner)

    def test_config_key_path_missing(self, tmp_path):
        planner = tmp_path / "planner"
        planner.mkdir()
        local_cfg = planner / "planning-config.local.json"
        local_cfg.write_text(json.dumps({
            "repositories": {
                "gone": {"path": "/no/such/dir"}
            }
        }))
        with pytest.raises(SystemExit):
            resolve_repo_path("gone", planner_dir=planner)

    def test_unknown_key_no_config_file(self, tmp_path):
        planner = tmp_path / "planner"
        planner.mkdir()
        with pytest.raises(SystemExit):
            resolve_repo_path("unknown-key", planner_dir=planner)


class TestSetupPlanningConfig:
    def test_creates_new_config(self, tmp_path):
        planning_root = Path("/some/planning/root")
        setup_planning_config(tmp_path, planning_root)

        config = json.loads((tmp_path / "planning-config.json").read_text())
        assert config["mode"] == "standalone"
        assert config["planningRoot"] == str(planning_root)

    def test_existing_config_correct(self, tmp_path, capsys):
        planning_root = Path("/my/root")
        config_file = tmp_path / "planning-config.json"
        config_file.write_text(json.dumps({
            "mode": "standalone",
            "planningRoot": str(planning_root),
        }))

        setup_planning_config(tmp_path, planning_root)
        assert "OK" in capsys.readouterr().out

    def test_existing_config_wrong_root(self, tmp_path, capsys):
        planning_root = Path("/correct/root")
        config_file = tmp_path / "planning-config.json"
        config_file.write_text(json.dumps({
            "mode": "standalone",
            "planningRoot": "/wrong/root",
        }))

        setup_planning_config(tmp_path, planning_root)

        config = json.loads(config_file.read_text())
        assert config["planningRoot"] == str(planning_root)
        assert "Overwriting" in capsys.readouterr().out

    def test_existing_config_corrupt(self, tmp_path):
        (tmp_path / "planning-config.json").write_text("{bad json")
        planning_root = Path("/root")
        setup_planning_config(tmp_path, planning_root)

        config = json.loads((tmp_path / "planning-config.json").read_text())
        assert config["planningRoot"] == str(planning_root)


class TestCleanStaleSymlinks:
    def test_no_claude_dir(self, tmp_path):
        assert clean_stale_symlinks(tmp_path, Path("/planner")) == 0

    def test_no_symlinks(self, tmp_path):
        skills = tmp_path / ".claude" / "skills"
        skills.mkdir(parents=True)
        (skills / "local.md").write_text("not a symlink")
        assert clean_stale_symlinks(tmp_path, Path("/planner")) == 0

    @pytest.mark.skipif(platform.system() == "Windows", reason="symlinks unreliable on Windows")
    def test_removes_planner_symlinks(self, tmp_path):
        planner = tmp_path / "planner"
        planner.mkdir()
        agent_file = planner / "researcher.md"
        agent_file.write_text("agent content")

        agents = tmp_path / "repo" / ".claude" / "agents"
        agents.mkdir(parents=True)
        link = agents / "researcher.md"
        link.symlink_to(agent_file)

        cleaned = clean_stale_symlinks(tmp_path / "repo", planner)
        assert cleaned == 1
        assert not link.exists()

    @pytest.mark.skipif(platform.system() == "Windows", reason="symlinks unreliable on Windows")
    def test_keeps_non_planner_symlinks(self, tmp_path):
        other = tmp_path / "other"
        other.mkdir()
        other_file = other / "skill.md"
        other_file.write_text("other content")

        skills = tmp_path / "repo" / ".claude" / "skills"
        skills.mkdir(parents=True)
        link = skills / "skill.md"
        link.symlink_to(other_file)

        cleaned = clean_stale_symlinks(tmp_path / "repo", tmp_path / "planner")
        assert cleaned == 0
        assert link.exists()


class TestWriteLauncher:
    @pytest.mark.skipif(platform.system() == "Windows", reason="tests Unix launcher")
    def test_unix_launcher(self, tmp_path):
        planning_root = Path("/planning")
        planner_dir = Path("/planner")

        write_launcher(tmp_path, planning_root, planner_dir)

        launcher = tmp_path / "claude.sh"
        assert launcher.exists()
        content = launcher.read_text()
        assert "#!/usr/bin/env bash" in content
        assert '--add-dir="/planning"' in content
        assert '--plugin-dir="/planner"' in content
        assert '"$@"' in content
        # Check executable
        assert launcher.stat().st_mode & stat.S_IXUSR

    @patch("setup.common.platform")
    def test_windows_launcher(self, mock_platform, tmp_path):
        mock_platform.system.return_value = "Windows"

        planning_root = Path("C:\\planning")
        planner_dir = Path("C:\\planner")

        write_launcher(tmp_path, planning_root, planner_dir)

        launcher = tmp_path / "claude.cmd"
        assert launcher.exists()
        content = launcher.read_text()
        assert "@echo off" in content
        assert "claude" in content
        assert "%*" in content

    def test_overwrites_existing(self, tmp_path):
        launcher = tmp_path / "claude.sh"
        launcher.write_text("old content")

        write_launcher(tmp_path, Path("/new"), Path("/planner"))

        assert "old content" not in launcher.read_text()
        assert "--add-dir" in launcher.read_text()

    @pytest.mark.skipif(platform.system() == "Windows", reason="tests Unix launcher")
    def test_reports_written_on_fresh(self, tmp_path, capsys):
        write_launcher(tmp_path, Path("/p"), Path("/d"))
        assert "written" in capsys.readouterr().out

    @pytest.mark.skipif(platform.system() == "Windows", reason="tests Unix launcher")
    def test_reports_overwritten_on_existing(self, tmp_path, capsys):
        (tmp_path / "claude.sh").write_text("old")
        write_launcher(tmp_path, Path("/p"), Path("/d"))
        assert "overwritten" in capsys.readouterr().out
