"""Tests for progress calculations."""

from dashboard.progress import plan_progress, phase_progress, overall_plan_status
from dashboard.models import PlanData, PhaseData, TaskData


class TestPlanProgress:
    def test_empty(self):
        plan = PlanData()
        assert plan_progress(plan) == (0, 0, 0)

    def test_all_complete(self):
        plan = PlanData(phases=[
            PhaseData(status="complete"),
            PhaseData(status="complete"),
        ])
        assert plan_progress(plan) == (2, 0, 2)

    def test_mixed(self):
        plan = PlanData(phases=[
            PhaseData(status="complete"),
            PhaseData(status="in-progress"),
            PhaseData(status="planned"),
        ])
        assert plan_progress(plan) == (1, 1, 3)

    def test_all_planned(self):
        plan = PlanData(phases=[
            PhaseData(status="planned"),
            PhaseData(status="planned"),
        ])
        assert plan_progress(plan) == (0, 0, 2)


class TestPhaseProgress:
    def test_empty(self):
        phase = PhaseData()
        assert phase_progress(phase) == (0, 0, 0)

    def test_all_complete(self):
        phase = PhaseData(tasks=[
            TaskData(status="complete"),
            TaskData(status="complete"),
        ])
        assert phase_progress(phase) == (2, 0, 2)

    def test_mixed(self):
        phase = PhaseData(tasks=[
            TaskData(status="complete"),
            TaskData(status="in-progress"),
            TaskData(status="planned"),
        ])
        assert phase_progress(phase) == (1, 1, 3)


class TestOverallPlanStatus:
    def test_explicit_complete(self):
        plan = PlanData(status="complete")
        assert overall_plan_status(plan) == "complete"

    def test_explicit_archived(self):
        plan = PlanData(status="archived")
        assert overall_plan_status(plan) == "archived"

    def test_no_phases(self):
        plan = PlanData(status="draft")
        assert overall_plan_status(plan) == "draft"

    def test_all_phases_complete(self):
        plan = PlanData(status="active", phases=[
            PhaseData(status="complete"),
            PhaseData(status="complete"),
        ])
        assert overall_plan_status(plan) == "complete"

    def test_some_in_progress(self):
        plan = PlanData(status="active", phases=[
            PhaseData(status="complete"),
            PhaseData(status="in-progress"),
        ])
        assert overall_plan_status(plan) == "in-progress"

    def test_some_complete_rest_planned(self):
        plan = PlanData(status="active", phases=[
            PhaseData(status="complete"),
            PhaseData(status="planned"),
        ])
        assert overall_plan_status(plan) == "in-progress"

    def test_all_planned(self):
        plan = PlanData(status="active", phases=[
            PhaseData(status="planned"),
            PhaseData(status="planned"),
        ])
        assert overall_plan_status(plan) == "planned"
