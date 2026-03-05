"""Tests for setup.common shared utilities."""

import json
import os
import platform
import stat
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from setup.common import (
    GITIGNORE_ENTRIES_BASE,
    GITIGNORE_ENTRIES_DASHBOARD,
    PLANNER_DIR,
    PLANNING_DIRS,
    clean_stale_symlinks,
    create_planning_dirs,
    detect_repo_type,
    find_sibling_config,
    load_json,
    resolve_repo_path,
    setup_gitignore,
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

    def test_dashboard_enabled_by_default(self, tmp_path):
        setup_planning_config(tmp_path, Path("/root"))
        config = json.loads((tmp_path / "planning-config.json").read_text())
        assert "dashboard" not in config

    def test_dashboard_disabled(self, tmp_path):
        setup_planning_config(tmp_path, Path("/root"), dashboard=False)
        config = json.loads((tmp_path / "planning-config.json").read_text())
        assert config["dashboard"] is False

    def test_dashboard_change_triggers_overwrite(self, tmp_path, capsys):
        planning_root = Path("/root")
        setup_planning_config(tmp_path, planning_root, dashboard=True)
        capsys.readouterr()  # clear

        setup_planning_config(tmp_path, planning_root, dashboard=False)
        config = json.loads((tmp_path / "planning-config.json").read_text())
        assert config["dashboard"] is False
        assert "Overwriting" in capsys.readouterr().out


class TestCreatePlanningDirs:
    def test_creates_all_dirs(self, tmp_path):
        created = create_planning_dirs(tmp_path)
        assert set(created) == set(PLANNING_DIRS)
        for name in PLANNING_DIRS:
            assert (tmp_path / name).is_dir()

    def test_skips_existing_dirs(self, tmp_path):
        (tmp_path / "Plans").mkdir()
        (tmp_path / "Research").mkdir()
        created = create_planning_dirs(tmp_path)
        assert "Plans" not in created
        assert "Research" not in created
        assert len(created) == len(PLANNING_DIRS) - 2

    def test_idempotent(self, tmp_path):
        create_planning_dirs(tmp_path)
        created = create_planning_dirs(tmp_path)
        assert created == []

    def test_returns_created_names(self, tmp_path):
        created = create_planning_dirs(tmp_path)
        for name in created:
            assert name in PLANNING_DIRS


class TestSetupGitignore:
    def test_creates_new_gitignore(self, tmp_path):
        modified = setup_gitignore(tmp_path)
        assert modified is True
        content = (tmp_path / ".gitignore").read_text()
        assert "Dashboard/" in content
        assert "planning-config.local.json" in content
        assert "__pycache__/" in content

    def test_appends_to_existing(self, tmp_path):
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("node_modules/\n")
        modified = setup_gitignore(tmp_path)
        assert modified is True
        content = gitignore.read_text()
        assert "node_modules/" in content
        assert "Dashboard/" in content

    def test_no_op_when_complete(self, tmp_path):
        setup_gitignore(tmp_path)
        modified = setup_gitignore(tmp_path)
        assert modified is False

    def test_preserves_existing_content(self, tmp_path):
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("*.log\n.env\n")
        setup_gitignore(tmp_path)
        content = gitignore.read_text()
        assert "*.log" in content
        assert ".env" in content

    def test_no_dashboard_skips_dashboard_entry(self, tmp_path):
        setup_gitignore(tmp_path, dashboard=False)
        content = (tmp_path / ".gitignore").read_text()
        assert "Dashboard/" not in content
        assert "planning-config.local.json" in content
        assert "__pycache__/" in content

    def test_dashboard_includes_dashboard_entry(self, tmp_path):
        setup_gitignore(tmp_path, dashboard=True)
        content = (tmp_path / ".gitignore").read_text()
        assert "Dashboard/" in content


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


class TestDetectRepoType:
    def test_normal_repo(self, tmp_path):
        repo = tmp_path / "normal"
        repo.mkdir()
        subprocess.run(["git", "init", str(repo)], capture_output=True, check=True)
        assert detect_repo_type(repo) == "normal"

    def test_worktree(self, worktree_pair):
        _, wt = worktree_pair
        assert detect_repo_type(wt) == "worktree"

    def test_bare_with_dot_bare(self, tmp_path):
        repo = tmp_path / "bare-project"
        repo.mkdir()
        bare_dir = repo / ".bare"
        subprocess.run(["git", "init", "--bare", str(bare_dir)], capture_output=True, check=True)
        assert detect_repo_type(repo) == "bare"

    def test_standard_bare(self, tmp_path):
        repo = tmp_path / "std-bare"
        subprocess.run(["git", "init", "--bare", str(repo)], capture_output=True, check=True)
        assert detect_repo_type(repo) == "bare"

    def test_not_a_repo(self, tmp_path):
        plain = tmp_path / "plain"
        plain.mkdir()
        with pytest.raises(ValueError, match="Not a git repository"):
            detect_repo_type(plain)


class TestFindSiblingConfig:
    def test_finds_sibling_config(self, worktree_pair):
        main_wt, second_wt = worktree_pair
        # Write config in the main worktree
        config = {"mode": "standalone", "planningRoot": "/my/planning"}
        (main_wt / "planning-config.json").write_text(json.dumps(config))

        result = find_sibling_config(second_wt)
        assert result is not None
        assert result["planningRoot"] == "/my/planning"
        assert result["dashboard"] is True
        assert result["source"] == str(main_wt)

    def test_returns_none_when_no_config(self, worktree_pair):
        _, second_wt = worktree_pair
        result = find_sibling_config(second_wt)
        assert result is None

    def test_skips_own_config(self, worktree_pair):
        main_wt, second_wt = worktree_pair
        # Only write config in the second worktree (self), not siblings
        config = {"mode": "standalone", "planningRoot": "/my/planning"}
        (second_wt / "planning-config.json").write_text(json.dumps(config))

        result = find_sibling_config(second_wt)
        # Should not find its own config — only main_wt is a sibling
        assert result is None

    def test_includes_dashboard_setting(self, worktree_pair):
        main_wt, second_wt = worktree_pair
        config = {"mode": "standalone", "planningRoot": "/p", "dashboard": False}
        (main_wt / "planning-config.json").write_text(json.dumps(config))

        result = find_sibling_config(second_wt)
        assert result is not None
        assert result["dashboard"] is False
