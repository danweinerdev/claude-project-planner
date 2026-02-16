"""Progress calculation utilities."""

from .models import PlanData, PhaseData


def plan_progress(plan: PlanData) -> tuple[int, int, int]:
    """Return (complete, in_progress, total) phase counts."""
    if not plan.phases:
        return 0, 0, 0
    complete = sum(1 for p in plan.phases if p.status == "complete")
    in_progress = sum(1 for p in plan.phases if p.status == "in-progress")
    return complete, in_progress, len(plan.phases)


def phase_progress(phase: PhaseData) -> tuple[int, int, int]:
    """Return (complete, in_progress, total) task counts."""
    if not phase.tasks:
        return 0, 0, 0
    complete = sum(1 for t in phase.tasks if t.status == "complete")
    in_progress = sum(1 for t in phase.tasks if t.status == "in-progress")
    return complete, in_progress, len(phase.tasks)


def overall_plan_status(plan: PlanData) -> str:
    """Determine visual status for a plan."""
    if plan.status in ("complete", "archived"):
        return plan.status
    if not plan.phases:
        return plan.status
    statuses = [p.status for p in plan.phases]
    if all(s == "complete" for s in statuses):
        return "complete"
    if any(s in ("complete", "in-progress") for s in statuses):
        return "in-progress"
    return "planned"
