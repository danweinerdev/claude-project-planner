"""Tests for setup.worktree — worktree-add.sh generator."""

import json
import os
import platform
import stat
import subprocess
from pathlib import Path

import pytest

from setup.worktree import find_git_dir, generate_script, main


@pytest.fixture
def bare_repo(tmp_path):
    """Create a minimal bare repo with .bare directory and one commit."""
    repo = tmp_path / "bare-project"
    repo.mkdir()
    bare_dir = repo / ".bare"

    subprocess.run(["git", "init", "--bare", str(bare_dir)], capture_output=True, check=True)

    # Create a temporary clone, make a commit, push, then remove
    work = tmp_path / "_work"
    subprocess.run(["git", "clone", str(bare_dir), str(work)], capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "init"],
        cwd=str(work), capture_output=True, check=True,
    )
    subprocess.run(
        ["git", "push", "origin", "main"],
        cwd=str(work), capture_output=True, check=True,
    )
    # Clean up work clone
    import shutil
    shutil.rmtree(work)

    return repo


@pytest.fixture
def standard_bare_repo(tmp_path):
    """Create a standard bare repo (no .bare, just bare init)."""
    repo = tmp_path / "std-bare"
    subprocess.run(["git", "init", "--bare", str(repo)], capture_output=True, check=True)
    return repo


class TestFindGitDir:
    def test_bare_dir(self, bare_repo):
        result = find_git_dir(bare_repo)
        assert result == bare_repo / ".bare"
        assert result.is_dir()

    def test_standard_bare(self, standard_bare_repo):
        result = find_git_dir(standard_bare_repo)
        assert result == standard_bare_repo

    def test_not_bare(self, tmp_path):
        normal = tmp_path / "normal"
        normal.mkdir()
        subprocess.run(["git", "init", str(normal)], capture_output=True, check=True)
        result = find_git_dir(normal)
        assert result is None

    def test_not_a_repo(self, tmp_path):
        plain = tmp_path / "plain"
        plain.mkdir()
        result = find_git_dir(plain)
        assert result is None


class TestGenerateScript:
    def test_contains_shebang(self):
        script = generate_script(Path("/planning"), Path("/planner"))
        assert script.startswith("#!/usr/bin/env bash")

    def test_contains_set_euo(self):
        script = generate_script(Path("/planning"), Path("/planner"))
        assert "set -euo pipefail" in script

    def test_bakes_in_planning_root(self):
        script = generate_script(Path("/my/planning"), Path("/planner"))
        assert 'PLANNING_ROOT="/my/planning"' in script

    def test_bakes_in_planner_dir(self):
        script = generate_script(Path("/planning"), Path("/my/planner"))
        assert 'PLANNER_DIR="/my/planner"' in script

    def test_launcher_uses_correct_paths(self):
        script = generate_script(Path("/planning"), Path("/planner"))
        assert '--add-dir="/planning"' in script
        assert '--plugin-dir="/planner"' in script

    def test_contains_usage_function(self):
        script = generate_script(Path("/p"), Path("/d"))
        assert "usage()" in script

    def test_contains_all_steps(self):
        script = generate_script(Path("/p"), Path("/d"))
        assert "Step 1" in script  # Create worktree
        assert "Step 2" in script  # Remote tracking
        assert "Step 3" in script  # planning-config.json
        assert "Step 4" in script  # Stale symlinks
        assert "Step 5" in script  # claude.sh

    def test_handles_branch_creation(self):
        script = generate_script(Path("/p"), Path("/d"))
        assert "does not exist. Creating new branch" in script

    def test_handles_existing_worktree(self):
        script = generate_script(Path("/p"), Path("/d"))
        assert "repairing setup" in script

    def test_regenerate_comment(self):
        script = generate_script(Path("/p"), Path("/my/planner"))
        assert "setup-worktree.py" in script
        assert "/my/planner" in script


class TestMainCLI:
    def test_generates_script_file(self, bare_repo):
        main([str(bare_repo)])

        script = bare_repo / "worktree-add.sh"
        assert script.exists()

    @pytest.mark.skipif(platform.system() == "Windows", reason="no chmod on Windows")
    def test_script_is_executable(self, bare_repo):
        main([str(bare_repo)])

        script = bare_repo / "worktree-add.sh"
        assert script.stat().st_mode & stat.S_IXUSR

    def test_script_has_correct_paths(self, bare_repo):
        main([str(bare_repo)])

        content = (bare_repo / "worktree-add.sh").read_text()
        from setup.common import PLANNER_DIR
        assert str(PLANNER_DIR) in content

    def test_custom_planning_root(self, bare_repo, tmp_path):
        planning = tmp_path / "my-planning"
        planning.mkdir()

        main([str(bare_repo), "--planning-root", str(planning)])

        content = (bare_repo / "worktree-add.sh").read_text()
        assert str(planning.resolve()) in content

    def test_rejects_non_bare_repo(self, tmp_path):
        normal = tmp_path / "normal"
        normal.mkdir()
        subprocess.run(["git", "init", str(normal)], capture_output=True, check=True)

        with pytest.raises(SystemExit):
            main([str(normal)])

    def test_rejects_plain_directory(self, tmp_path):
        plain = tmp_path / "plain"
        plain.mkdir()
        with pytest.raises(SystemExit):
            main([str(plain)])

    def test_output_message(self, bare_repo, capsys):
        main([str(bare_repo)])
        output = capsys.readouterr().out
        assert "Generated" in output
        assert "worktree-add.sh" in output

    def test_overwrites_existing_script(self, bare_repo):
        script = bare_repo / "worktree-add.sh"
        script.write_text("old content")

        main([str(bare_repo)])
        assert "old content" not in script.read_text()
        assert "#!/usr/bin/env bash" in script.read_text()


@pytest.mark.skipif(platform.system() == "Windows", reason="bash not available")
class TestGeneratedScriptExecution:
    """Integration tests that actually run the generated script."""

    def test_create_worktree(self, bare_repo):
        main([str(bare_repo)])

        result = subprocess.run(
            [str(bare_repo / "worktree-add.sh"), "main"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "Worktree ready" in result.stdout

        wt = bare_repo / "main"
        assert wt.is_dir()
        assert (wt / ".git").exists()
        assert (wt / "planning-config.json").exists()
        assert (wt / "claude.sh").exists()

    def test_create_new_branch(self, bare_repo):
        main([str(bare_repo)])

        result = subprocess.run(
            [str(bare_repo / "worktree-add.sh"), "feature/test"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert (bare_repo / "feature" / "test").is_dir()

    def test_rerun_existing_worktree(self, bare_repo):
        main([str(bare_repo)])

        # First run
        subprocess.run(
            [str(bare_repo / "worktree-add.sh"), "main"],
            capture_output=True, check=True,
        )
        # Second run — should repair, not fail
        result = subprocess.run(
            [str(bare_repo / "worktree-add.sh"), "main"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "repairing setup" in result.stdout

    def test_worktree_planning_config_correct(self, bare_repo):
        main([str(bare_repo)])

        subprocess.run(
            [str(bare_repo / "worktree-add.sh"), "main"],
            capture_output=True, check=True,
        )

        config = json.loads((bare_repo / "main" / "planning-config.json").read_text())
        assert config["mode"] == "standalone"
        from setup.common import PLANNER_DIR
        assert config["planningRoot"] == str(PLANNER_DIR)

    def test_worktree_launcher_content(self, bare_repo):
        main([str(bare_repo)])

        subprocess.run(
            [str(bare_repo / "worktree-add.sh"), "main"],
            capture_output=True, check=True,
        )

        launcher = (bare_repo / "main" / "claude.sh").read_text()
        assert "--add-dir=" in launcher
        assert "--plugin-dir=" in launcher

    def test_usage_on_no_args(self, bare_repo):
        main([str(bare_repo)])

        result = subprocess.run(
            [str(bare_repo / "worktree-add.sh")],
            capture_output=True, text=True,
        )
        assert result.returncode != 0
        assert "Usage" in result.stdout or "Usage" in result.stderr
