"""Tests for data models."""

from pathlib import Path
from dashboard.models import SubtaskInfo, TaskData, PhaseData, PlanData, Artifact


class TestSubtaskInfo:
    def test_defaults(self):
        s = SubtaskInfo()
        assert s.done == 0
        assert s.total == 0

    def test_construction(self):
        s = SubtaskInfo(done=3, total=5)
        assert s.done == 3
        assert s.total == 5


class TestTaskData:
    def test_defaults(self):
        t = TaskData()
        assert t.id == ""
        assert t.title == ""
        assert t.status == "planned"
        assert t.depends_on == []
        assert t.subtasks.done == 0
        assert t.subtasks.total == 0

    def test_construction(self):
        t = TaskData(id="1.1", title="Setup", status="complete")
        assert t.id == "1.1"
        assert t.status == "complete"

    def test_independent_defaults(self):
        """Ensure default factory creates independent lists."""
        t1 = TaskData()
        t2 = TaskData()
        t1.depends_on.append("x")
        assert t2.depends_on == []


class TestPhaseData:
    def test_defaults(self):
        p = PhaseData()
        assert p.id == 0
        assert p.title == ""
        assert p.status == "planned"
        assert p.tasks == []
        assert p.slug == ""

    def test_construction(self):
        p = PhaseData(id=1, title="Setup", status="complete", slug="setup")
        assert p.id == 1
        assert p.slug == "setup"


class TestPlanData:
    def test_defaults(self):
        p = PlanData()
        assert p.name == ""
        assert p.status == "draft"
        assert p.tags == []
        assert p.phases == []
        assert p.path == Path()
        assert p.target_repo == ""
        assert p.target_repo_url == ""

    def test_construction(self):
        p = PlanData(name="TestPlan", title="Test", status="active")
        assert p.name == "TestPlan"
        assert p.title == "Test"


class TestArtifact:
    def test_defaults(self):
        a = Artifact()
        assert a.title == ""
        assert a.type == ""
        assert a.status == "draft"
        assert a.tags == []
        assert a.content == ""
        assert a.category == ""

    def test_construction(self):
        a = Artifact(title="Research Notes", type="research", status="active",
                     category="Research")
        assert a.title == "Research Notes"
        assert a.type == "research"
        assert a.category == "Research"
