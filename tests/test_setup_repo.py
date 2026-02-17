"""Tests for setup.repo — normal repository setup."""

import json
import platform
from pathlib import Path

import pytest

from setup.repo import main


@pytest.fixture
def repo(tmp_path):
    """Create a minimal directory to act as a repo target."""
    repo_dir = tmp_path / "my-project"
    repo_dir.mkdir()
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
            assert not link.exists()

    def test_nonexistent_repo_exits(self):
        with pytest.raises(SystemExit):
            main(["/no/such/directory"])

    def test_summary_output(self, repo, capsys):
        main([str(repo)])
        output = capsys.readouterr().out
        assert "Repo configured" in output
        assert str(repo) in output
