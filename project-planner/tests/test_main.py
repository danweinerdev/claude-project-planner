"""Integration tests for the main dashboard generation."""

import json
from dashboard.main import main


class TestMainIntegration:
    def test_full_generation(self, planning_root):
        """Run main() against fixture data and verify output."""
        main(planning_root=planning_root)

        dashboard = planning_root / "Dashboard"
        assert dashboard.exists()
        assert (dashboard / "index.html").exists()
        assert (dashboard / "styles.css").exists()

        # Plan pages
        assert (dashboard / "testplan" / "index.html").exists()
        assert (dashboard / "testplan" / "setup.html").exists()
        assert (dashboard / "testplan" / "build.html").exists()

        # Knowledge page (from Research artifacts)
        assert (dashboard / "knowledge.html").exists()
        assert (dashboard / "knowledge" / "caching.html").exists()

        # Specs page
        assert (dashboard / "specs.html").exists()
        assert (dashboard / "specs" / "authentication.html").exists()

        # Retros page
        assert (dashboard / "retros.html").exists()
        assert (dashboard / "retros" / "2025-01-20-sprint-1.html").exists()

    def test_index_contains_plan_title(self, planning_root):
        main(planning_root=planning_root)
        index_html = (planning_root / "Dashboard" / "index.html").read_text()
        assert "Test Plan" in index_html
        assert "Test Project" in index_html

    def test_disabled_dashboard(self, tmp_path):
        """Dashboard generation should be skipped when disabled."""
        plans = tmp_path / "Plans"
        plans.mkdir()

        (tmp_path / "planning-config.json").write_text(
            json.dumps({"dashboard": False}))

        main(planning_root=tmp_path)
        assert not (tmp_path / "Dashboard").exists()

    def test_empty_plans(self, tmp_path):
        """Should handle empty Plans directory gracefully."""
        (tmp_path / "planning-config.json").write_text(json.dumps({}))

        main(planning_root=tmp_path)

        dashboard = tmp_path / "Dashboard"
        assert dashboard.exists()
        assert (dashboard / "index.html").exists()

    def test_no_plans_dir(self, tmp_path):
        """Should create Plans/ and generate dashboard with no plans."""
        (tmp_path / "planning-config.json").write_text(json.dumps({}))

        main(planning_root=tmp_path)

        assert (tmp_path / "Plans").exists()
        assert (tmp_path / "Dashboard" / "index.html").exists()

    def test_css_written(self, planning_root):
        main(planning_root=planning_root)
        css = (planning_root / "Dashboard" / "styles.css").read_text()
        assert ":root" in css
        assert "--bg:" in css

    def test_plan_page_has_phases(self, planning_root):
        main(planning_root=planning_root)
        plan_html = (planning_root / "Dashboard" / "testplan" / "index.html").read_text()
        assert "Setup" in plan_html
        assert "Build" in plan_html

    def test_phase_page_has_tasks(self, planning_root):
        main(planning_root=planning_root)
        phase_html = (planning_root / "Dashboard" / "testplan" / "build.html").read_text()
        assert "Write core" in phase_html
        assert "Write tests" in phase_html
