"""Tests for setup.repo — normal repository setup."""

import json
import platform
import subprocess
from pathlib import Path

import pytest

from setup.repo import main


@pytest.fixture
def repo(tmp_path):
    """Create a minimal git repository to act as a repo target."""
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
        # planningRoot should point to the project-planner directory
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
            # Symlink should be removed (no longer replaced by a copy)
            assert not link.is_symlink()
            assert not link.exists()

    def test_cleans_stale_copies(self, repo, capsys):
        from setup.common import PLANNER_DIR

        # Create stale file copies matching planner filenames
        skills = repo / ".claude" / "skills"
        skills.mkdir(parents=True)
        (skills / "research.md").write_text("old copy")

        main([str(repo)])
        output = capsys.readouterr().out
        assert "stale planner file copies" in output
        assert not (skills / "research.md").exists()

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
        _main_wt, second_wt = worktree_pair
        main([str(second_wt)])

        assert (second_wt / "planning-config.json").exists()

    def test_worktree_label(self, worktree_pair, capsys):
        _main_wt, second_wt = worktree_pair
        main([str(second_wt)])
        output = capsys.readouterr().out
        assert "Worktree configured" in output

    def test_inherits_sibling_planning_root(self, worktree_pair, tmp_path, capsys):
        main_wt, second_wt = worktree_pair
        planning_root = tmp_path / "custom-planning"
        planning_root.mkdir()

        # Set up config in main worktree
        config = {"mode": "standalone", "planningRoot": str(planning_root)}
        (main_wt / "planning-config.json").write_text(json.dumps(config))

        main([str(second_wt)])

        second_config = json.loads((second_wt / "planning-config.json").read_text())
        assert second_config["planningRoot"] == str(planning_root)
        assert "Inheriting" in capsys.readouterr().out

    def test_explicit_flag_overrides_sibling(self, worktree_pair, tmp_path):
        main_wt, second_wt = worktree_pair
        sibling_root = tmp_path / "sibling-planning"
        sibling_root.mkdir()
        explicit_root = tmp_path / "explicit-planning"
        explicit_root.mkdir()

        # Set up config in main worktree with one path
        config = {"mode": "standalone", "planningRoot": str(sibling_root)}
        (main_wt / "planning-config.json").write_text(json.dumps(config))

        # Explicit flag should override
        main([str(second_wt), "--planning-root", str(explicit_root)])

        second_config = json.loads((second_wt / "planning-config.json").read_text())
        assert second_config["planningRoot"] == str(explicit_root.resolve())

    def test_worktree_creates_launcher(self, worktree_pair):
        _main_wt, second_wt = worktree_pair
        main([str(second_wt)])

        if platform.system() == "Windows":
            assert (second_wt / "claude.cmd").exists()
        else:
            assert (second_wt / "claude.sh").exists()


class TestSetupRepoBareRejection:
    def test_bare_with_dot_bare(self, tmp_path):
        repo = tmp_path / "bare-project"
        repo.mkdir()
        bare_dir = repo / ".bare"
        subprocess.run(["git", "init", "--bare", str(bare_dir)], capture_output=True, check=True)

        with pytest.raises(SystemExit):
            main([str(repo)])

    def test_standard_bare(self, tmp_path):
        repo = tmp_path / "std-bare"
        subprocess.run(["git", "init", "--bare", str(repo)], capture_output=True, check=True)

        with pytest.raises(SystemExit):
            main([str(repo)])

    def test_bare_error_message(self, tmp_path, capsys):
        repo = tmp_path / "bare-project"
        repo.mkdir()
        (repo / ".bare").mkdir()
        subprocess.run(
            ["git", "init", "--bare", str(repo / ".bare")],
            capture_output=True, check=True,
        )

        with pytest.raises(SystemExit):
            main([str(repo)])

        err = capsys.readouterr().err
        assert "bare repository" in err
        assert "worktree" in err.lower()
