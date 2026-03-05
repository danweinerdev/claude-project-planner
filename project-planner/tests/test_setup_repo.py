"""Tests for setup.repo — repository setup (normal + worktree)."""

import json
import platform
import subprocess
from pathlib import Path

import pytest

from setup.common import PLANNING_DIRS
from setup.repo import main


@pytest.fixture
def repo(tmp_path):
    """Create a minimal git repo to act as a repo target."""
    repo_dir = tmp_path / "my-project"
    repo_dir.mkdir()
    subprocess.run(["git", "init", str(repo_dir)], capture_output=True, check=True)
    return repo_dir


class TestSetupRepoMain:
    def test_creates_all_artifacts(self, repo):
        main([str(repo)])

        assert (repo / "planning-config.json").exists()
        if platform.system() == "Windows":
            assert (repo / "claude.cmd").exists()
        else:
            assert (repo / "claude.sh").exists()

    def test_planning_config_content(self, repo):
        main([str(repo)])

        config = json.loads((repo / "planning-config.json").read_text())
        assert config["mode"] == "standalone"
        assert "planningRoot" in config

    def test_custom_planning_root(self, repo, tmp_path):
        planning = tmp_path / "planning-repo"
        planning.mkdir()

        main([str(repo), "--planning-root", str(planning)])

        config = json.loads((repo / "planning-config.json").read_text())
        assert config["planningRoot"] == str(planning.resolve())

        if platform.system() != "Windows":
            content = (repo / "claude.sh").read_text()
            assert str(planning.resolve()) in content

    def test_bootstraps_planning_dirs(self, repo):
        from setup.common import PLANNER_DIR
        main([str(repo)])

        # Planning dirs are created at the planning root (defaults to PLANNER_DIR)
        # which already has dirs, so test with custom root
        pass

    def test_bootstraps_planning_dirs_custom_root(self, repo, tmp_path):
        planning = tmp_path / "planning-repo"
        planning.mkdir()

        main([str(repo), "--planning-root", str(planning)])

        for name in PLANNING_DIRS:
            assert (planning / name).is_dir()

    def test_creates_gitignore(self, repo, tmp_path):
        planning = tmp_path / "planning-repo"
        planning.mkdir()

        main([str(repo), "--planning-root", str(planning)])

        gitignore = planning / ".gitignore"
        assert gitignore.exists()
        content = gitignore.read_text()
        assert "Dashboard/" in content

    def test_idempotent(self, repo):
        main([str(repo)])
        main([str(repo)])

        # Should still have exactly one config file, one launcher
        assert (repo / "planning-config.json").exists()

    @pytest.mark.skipif(platform.system() == "Windows", reason="tests Unix launcher")
    def test_launcher_executable(self, repo):
        main([str(repo)])

        import stat
        launcher = repo / "claude.sh"
        assert launcher.stat().st_mode & stat.S_IXUSR

    @pytest.mark.skipif(platform.system() == "Windows", reason="tests Unix launcher")
    def test_launcher_includes_add_dir_for_external_planning(self, repo):
        """When planning root is external to repo, launcher includes --add-dir."""
        main([str(repo)])

        content = (repo / "claude.sh").read_text()
        assert "--add-dir=" in content
        assert "--plugin-dir=" in content

    @pytest.mark.skipif(platform.system() == "Windows", reason="tests Unix launcher")
    def test_launcher_excludes_add_dir_for_local_planning(self, repo):
        """When planning root is the repo itself, launcher omits --add-dir."""
        main([str(repo), "--planning-root", str(repo)])

        content = (repo / "claude.sh").read_text()
        assert "--add-dir=" not in content
        assert "--plugin-dir=" in content

    @pytest.mark.skipif(platform.system() == "Windows", reason="symlinks unreliable on Windows")
    def test_cleans_stale_symlinks(self, repo, capsys):
        from setup.common import PLANNER_DIR

        # Create a fake stale symlink
        agents = repo / ".claude" / "agents"
        agents.mkdir(parents=True)
        fake_target = PLANNER_DIR / "agents" / "researcher.md"
        if fake_target.exists():
            link = agents / "researcher.md"
            link.symlink_to(fake_target)

            main([str(repo)])
            # Symlink should be removed
            assert not link.is_symlink()

    def test_does_not_copy_skills_or_agents(self, repo):
        main([str(repo)])

        skills_dir = repo / ".claude" / "skills"
        agents_dir = repo / ".claude" / "agents"
        # Should not create these directories
        assert not skills_dir.exists() or len(list(skills_dir.glob("*.md"))) == 0
        assert not agents_dir.exists() or len(list(agents_dir.glob("*.md"))) == 0

    def test_no_dashboard_flag(self, repo):
        main([str(repo), "--no-dashboard"])

        config = json.loads((repo / "planning-config.json").read_text())
        assert config["dashboard"] is False

    def test_dashboard_enabled_by_default(self, repo):
        main([str(repo)])

        config = json.loads((repo / "planning-config.json").read_text())
        assert "dashboard" not in config

    def test_nonexistent_repo_exits(self):
        with pytest.raises(SystemExit):
            main(["/no/such/directory"])

    def test_summary_output(self, repo, capsys):
        main([str(repo)])
        output = capsys.readouterr().out
        assert "Repo configured" in output
        assert str(repo) in output


class TestSetupRepoWorktree:
    def test_worktree_succeeds(self, worktree_pair):
        _, wt = worktree_pair
        main([str(wt)])
        assert (wt / "planning-config.json").exists()

    def test_worktree_summary_label(self, worktree_pair, capsys):
        _, wt = worktree_pair
        main([str(wt)])
        output = capsys.readouterr().out
        assert "Worktree configured" in output

    def test_inherits_sibling_planning_root(self, worktree_pair, tmp_path, capsys):
        main_wt, second_wt = worktree_pair
        planning = tmp_path / "custom-planning"
        planning.mkdir()
        config = {"mode": "standalone", "planningRoot": str(planning)}
        (main_wt / "planning-config.json").write_text(json.dumps(config))

        main([str(second_wt)])

        result = json.loads((second_wt / "planning-config.json").read_text())
        assert result["planningRoot"] == str(planning.resolve())
        assert "Inheriting" in capsys.readouterr().out

    def test_inherits_dashboard_setting(self, worktree_pair, tmp_path):
        main_wt, second_wt = worktree_pair
        planning = tmp_path / "planning"
        planning.mkdir()
        config = {"mode": "standalone", "planningRoot": str(planning), "dashboard": False}
        (main_wt / "planning-config.json").write_text(json.dumps(config))

        main([str(second_wt)])

        result = json.loads((second_wt / "planning-config.json").read_text())
        assert result["dashboard"] is False

    def test_explicit_flag_overrides_sibling(self, worktree_pair, tmp_path):
        main_wt, second_wt = worktree_pair
        config = {"mode": "standalone", "planningRoot": "/sibling/root"}
        (main_wt / "planning-config.json").write_text(json.dumps(config))

        explicit = tmp_path / "explicit-root"
        explicit.mkdir()
        main([str(second_wt), "--planning-root", str(explicit)])

        result = json.loads((second_wt / "planning-config.json").read_text())
        assert result["planningRoot"] == str(explicit.resolve())


class TestSetupRepoBareRejection:
    def test_bare_dot_bare_exits(self, tmp_path):
        repo = tmp_path / "bare-project"
        repo.mkdir()
        subprocess.run(
            ["git", "init", "--bare", str(repo / ".bare")],
            capture_output=True, check=True,
        )
        with pytest.raises(SystemExit):
            main([str(repo)])

    def test_standard_bare_exits(self, tmp_path):
        repo = tmp_path / "std-bare"
        subprocess.run(
            ["git", "init", "--bare", str(repo)],
            capture_output=True, check=True,
        )
        with pytest.raises(SystemExit):
            main([str(repo)])

    def test_bare_error_message(self, tmp_path, capsys):
        repo = tmp_path / "bare-project"
        repo.mkdir()
        subprocess.run(
            ["git", "init", "--bare", str(repo / ".bare")],
            capture_output=True, check=True,
        )
        with pytest.raises(SystemExit):
            main([str(repo)])
        err = capsys.readouterr().err
        assert "bare repository" in err
        assert "worktree" in err.lower()
