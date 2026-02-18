"""Data models for dashboard artifacts."""

from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class SubtaskInfo:
    done: int = 0
    total: int = 0

@dataclass
class TaskData:
    id: str = ""
    title: str = ""
    status: str = "planned"
    depends_on: list[str] = field(default_factory=list)
    subtasks: SubtaskInfo = field(default_factory=SubtaskInfo)

@dataclass
class PhaseData:
    id: int = 0
    title: str = ""
    status: str = "planned"
    doc: str = ""
    depends_on: list[int] = field(default_factory=list)
    deliverable: str = ""
    tasks: list[TaskData] = field(default_factory=list)
    content: str = ""
    slug: str = ""

@dataclass
class PlanData:
    name: str = ""
    title: str = ""
    status: str = "draft"
    created: str = ""
    updated: str = ""
    tags: list[str] = field(default_factory=list)
    related: list[str] = field(default_factory=list)
    phases: list[PhaseData] = field(default_factory=list)
    path: Path = field(default_factory=Path)
    slug: str = ""
    overview: str = ""
    target_repo: str = ""
    target_repo_url: str = ""

@dataclass
class Artifact:
    """Generic artifact: research, brainstorm, spec, design, debrief, retro."""
    title: str = ""
    type: str = ""          # research, brainstorm, spec, design, debrief, retro
    status: str = "draft"
    created: str = ""
    updated: str = ""
    tags: list[str] = field(default_factory=list)
    related: list[str] = field(default_factory=list)
    path: Path = field(default_factory=Path)
    slug: str = ""
    content: str = ""
    category: str = ""      # directory name (Research, Brainstorm, etc.)
