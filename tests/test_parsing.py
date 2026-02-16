"""Tests for parsing utilities."""

from pathlib import Path
from dashboard.parsing import (
    slugify,
    count_checklist,
    extract_task_subtasks,
    extract_overview,
    parse_plan,
    parse_artifact,
    scan_artifacts,
)
from dashboard.models import SubtaskInfo


class TestSlugify:
    def test_simple(self):
        assert slugify("Hello World") == "hello-world"

    def test_special_chars(self):
        assert slugify("Hello, World!") == "hello-world"

    def test_multiple_spaces(self):
        assert slugify("hello   world") == "hello-world"

    def test_hyphens(self):
        assert slugify("hello-world") == "hello-world"

    def test_mixed(self):
        assert slugify("Phase 1: Setup & Config") == "phase-1-setup-config"

    def test_trailing_hyphens(self):
        assert slugify("--hello--") == "hello"

    def test_empty(self):
        assert slugify("") == ""


class TestCountChecklist:
    def test_all_done(self):
        text = "- [x] one\n- [x] two\n- [x] three"
        done, total = count_checklist(text)
        assert done == 3
        assert total == 3

    def test_none_done(self):
        text = "- [ ] one\n- [ ] two"
        done, total = count_checklist(text)
        assert done == 0
        assert total == 2

    def test_mixed(self):
        text = "- [x] done\n- [ ] pending\n- [x] also done"
        done, total = count_checklist(text)
        assert done == 2
        assert total == 3

    def test_no_checklist(self):
        text = "Just some text without checkboxes."
        done, total = count_checklist(text)
        assert done == 0
        assert total == 0

    def test_case_insensitive(self):
        text = "- [X] uppercase"
        done, total = count_checklist(text)
        assert done == 1
        assert total == 1


class TestExtractTaskSubtasks:
    def test_found(self):
        body = """\
## 1.1: Install deps

- [x] Install Python
- [x] Install Node

## 1.2: Configure env

- [ ] Set up .env
"""
        result = extract_task_subtasks(body, "1.1")
        assert result.done == 2
        assert result.total == 2

    def test_not_found(self):
        body = "## 2.1: Something else\n- [x] done"
        result = extract_task_subtasks(body, "1.1")
        assert result.done == 0
        assert result.total == 0

    def test_last_section(self):
        body = """\
## 1.1: First

- [x] a

## 1.2: Last

- [x] b
- [ ] c
"""
        result = extract_task_subtasks(body, "1.2")
        assert result.done == 1
        assert result.total == 2


class TestExtractOverview:
    def test_simple(self):
        body = "# Title\n\nThis is the overview paragraph.\n\nMore content."
        assert extract_overview(body) == "This is the overview paragraph."

    def test_no_heading(self):
        body = "First paragraph here.\n\nSecond paragraph."
        assert extract_overview(body) == "First paragraph here."

    def test_empty(self):
        assert extract_overview("") == ""

    def test_heading_only(self):
        body = "# Just a heading\n\n"
        assert extract_overview(body) == ""

    def test_truncation(self):
        body = "A" * 500
        assert len(extract_overview(body)) == 300


class TestParsePlan:
    def test_valid_plan(self, plan_dir):
        plan_path = plan_dir / "Plans" / "TestPlan"
        plan = parse_plan(plan_path)
        assert plan is not None
        assert plan.title == "Test Plan"
        assert plan.status == "active"
        assert plan.slug == "testplan"
        assert len(plan.phases) == 2

    def test_phase_details(self, plan_dir):
        plan_path = plan_dir / "Plans" / "TestPlan"
        plan = parse_plan(plan_path)
        phase1 = plan.phases[0]
        assert phase1.id == 1
        assert phase1.title == "Setup"
        assert phase1.status == "complete"
        assert len(phase1.tasks) == 2

    def test_task_subtasks(self, plan_dir):
        plan_path = plan_dir / "Plans" / "TestPlan"
        plan = parse_plan(plan_path)
        # Phase 1, Task 1.1 should have 2/2 subtasks
        task = plan.phases[0].tasks[0]
        assert task.subtasks.done == 2
        assert task.subtasks.total == 2

    def test_phase_dependencies(self, plan_dir):
        plan_path = plan_dir / "Plans" / "TestPlan"
        plan = parse_plan(plan_path)
        phase2 = plan.phases[1]
        assert phase2.depends_on == [1]

    def test_missing_readme(self, tmp_path):
        plan_path = tmp_path / "EmptyPlan"
        plan_path.mkdir()
        assert parse_plan(plan_path) is None

    def test_non_plan_type(self, tmp_path):
        plan_path = tmp_path / "NotAPlan"
        plan_path.mkdir()
        (plan_path / "README.md").write_text("""\
---
title: Not a plan
type: spec
---
Content.
""")
        assert parse_plan(plan_path) is None

    def test_overview_extracted(self, plan_dir):
        plan_path = plan_dir / "Plans" / "TestPlan"
        plan = parse_plan(plan_path)
        assert "Overview" in plan.overview


class TestParseArtifact:
    def test_valid_artifact(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("""\
---
title: My Research
type: research
status: active
created: 2025-01-10
tags: [perf, caching]
---

Research content here.
""")
        art = parse_artifact(md, "Research")
        assert art is not None
        assert art.title == "My Research"
        assert art.type == "research"
        assert art.status == "active"
        assert art.tags == ["perf", "caching"]
        assert "Research content" in art.content

    def test_no_frontmatter(self, tmp_path):
        md = tmp_path / "bare.md"
        md.write_text("Just plain text, no frontmatter.")
        assert parse_artifact(md, "Research") is None

    def test_slug_from_filename(self, tmp_path):
        md = tmp_path / "My Research Notes.md"
        md.write_text("---\ntitle: Research\n---\nContent.")
        art = parse_artifact(md, "Research")
        assert art.slug == "my-research-notes"


class TestScanArtifacts:
    def test_flat_layout(self, artifacts_dir):
        arts = scan_artifacts(artifacts_dir, "Research")
        assert len(arts) == 1
        assert arts[0].title == "Caching Strategies"

    def test_subdirectory_layout(self, artifacts_dir):
        arts = scan_artifacts(artifacts_dir, "Specs")
        assert len(arts) == 1
        assert arts[0].title == "Authentication Spec"
        assert arts[0].slug == "authentication"

    def test_missing_directory(self, tmp_path):
        arts = scan_artifacts(tmp_path, "Nonexistent")
        assert arts == []
