"""Parsing utilities for plans and artifacts."""

import re
from pathlib import Path
from typing import Optional

from .frontmatter import parse_frontmatter
from .models import SubtaskInfo, TaskData, PhaseData, PlanData, Artifact


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text).strip('-')
    return text


def count_checklist(text: str) -> tuple[int, int]:
    done = len(re.findall(r'\[x\]', text, re.IGNORECASE))
    undone = len(re.findall(r'\[ \]', text))
    return done, done + undone


def extract_task_subtasks(body: str, task_id: str) -> SubtaskInfo:
    """Extract subtask checklist counts for a specific task from phase body."""
    # Find the section for this task ID (e.g., ## 1.1: Task Title)
    pattern = rf'^##\s+{re.escape(task_id)}[:\s]'
    match = re.search(pattern, body, re.MULTILINE)
    if not match:
        return SubtaskInfo()

    # Get text from this heading to the next ## heading
    start = match.start()
    next_heading = re.search(r'^##\s', body[start + 1:], re.MULTILINE)
    if next_heading:
        section = body[start:start + 1 + next_heading.start()]
    else:
        section = body[start:]

    done, total = count_checklist(section)
    return SubtaskInfo(done=done, total=total)


def extract_overview(body: str) -> str:
    """Extract first meaningful paragraph from body."""
    lines = body.split('\n')
    para_lines = []
    in_para = False

    for line in lines:
        if line.startswith('#'):
            if in_para:
                break
            continue
        if not line.strip():
            if in_para:
                break
            continue
        in_para = True
        para_lines.append(line.strip())

    return ' '.join(para_lines)[:300]


def parse_plan(plan_dir: Path) -> Optional[PlanData]:
    """Parse a plan directory into PlanData."""
    readme = plan_dir / "README.md"
    if not readme.exists():
        return None

    text = readme.read_text()
    meta, body = parse_frontmatter(text)

    if meta.get("type") and meta["type"] != "plan":
        return None

    plan = PlanData(
        name=plan_dir.name,
        title=meta.get("title", plan_dir.name),
        status=meta.get("status", "draft"),
        created=str(meta.get("created", "")),
        updated=str(meta.get("updated", "")),
        tags=meta.get("tags", []),
        related=meta.get("related", []),
        path=plan_dir,
        slug=slugify(plan_dir.name),
        overview=extract_overview(body),
    )

    # Parse phases from frontmatter
    for phase_meta in meta.get("phases", []):
        if not isinstance(phase_meta, dict):
            continue

        phase = PhaseData(
            id=int(phase_meta.get("id", 0)),
            title=str(phase_meta.get("title", "")),
            status=str(phase_meta.get("status", "planned")),
            doc=str(phase_meta.get("doc", "")),
            slug=slugify(str(phase_meta.get("title", ""))),
        )

        deps = phase_meta.get("depends_on", [])
        if isinstance(deps, list):
            phase.depends_on = [int(d) for d in deps if d]

        # Parse phase doc for tasks
        if phase.doc:
            phase_path = plan_dir / phase.doc
            if phase_path.exists():
                phase_text = phase_path.read_text()
                phase_meta_inner, phase_body = parse_frontmatter(phase_text)
                phase.content = phase_body
                phase.deliverable = str(phase_meta_inner.get("deliverable", ""))

                for task_meta in phase_meta_inner.get("tasks", []):
                    if not isinstance(task_meta, dict):
                        continue
                    task = TaskData(
                        id=str(task_meta.get("id", "")),
                        title=str(task_meta.get("title", "")),
                        status=str(task_meta.get("status", "planned")),
                    )
                    deps = task_meta.get("depends_on", [])
                    if isinstance(deps, list):
                        task.depends_on = [str(d) for d in deps]

                    # Extract subtask counts from body
                    task.subtasks = extract_task_subtasks(phase_body, task.id)
                    phase.tasks.append(task)

        plan.phases.append(phase)

    return plan


def parse_artifact(file_path: Path, category: str) -> Optional[Artifact]:
    """Parse a markdown file with frontmatter into an Artifact."""
    text = file_path.read_text()
    meta, body = parse_frontmatter(text)

    if not meta:
        return None

    return Artifact(
        title=str(meta.get("title", file_path.stem)),
        type=str(meta.get("type", category.lower())),
        status=str(meta.get("status", "draft")),
        created=str(meta.get("created", "")),
        updated=str(meta.get("updated", "")),
        tags=meta.get("tags", []) or [],
        related=meta.get("related", []) or [],
        path=file_path,
        slug=slugify(file_path.stem),
        content=body,
        category=category,
    )


def scan_artifacts(base_dir: Path, category: str) -> list[Artifact]:
    """Scan a directory for markdown artifacts. Handles both flat and subdirectory layouts."""
    artifacts = []
    cat_dir = base_dir / category

    if not cat_dir.exists():
        return artifacts

    # Flat layout: Research/topic.md
    for md in sorted(cat_dir.glob("*.md")):
        art = parse_artifact(md, category)
        if art:
            artifacts.append(art)

    # Subdirectory layout: Specs/Feature/README.md
    for sub in sorted(cat_dir.iterdir()):
        if sub.is_dir():
            readme = sub / "README.md"
            if readme.exists():
                art = parse_artifact(readme, category)
                if art:
                    art.slug = slugify(sub.name)
                    artifacts.append(art)

    return artifacts
