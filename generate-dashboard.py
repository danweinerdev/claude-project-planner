#!/usr/bin/env python3
"""
Project Planner Dashboard Generator

Generates a static HTML dashboard from plan artifacts with YAML frontmatter.
Reads phase/task status from frontmatter, subtask checklists from markdown body.

Data flow:
  1. Parse plan README frontmatter -> phase list with statuses
  2. Parse each phase doc frontmatter -> task list with statuses
  3. Parse phase body -> subtask checklists (count [x] vs [ ])
  4. Aggregate -> progress percentages
  5. Generate HTML pages

Python 3, stdlib only (no external dependencies).
"""

import re
import html
import json
import shutil
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# ---------------------------------------------------------------------------
# YAML frontmatter parser (stdlib only, no PyYAML)
# ---------------------------------------------------------------------------

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from markdown text.

    Returns (metadata_dict, body_text). If no frontmatter found,
    returns ({}, full_text).

    Handles: scalars, lists (inline [...] and block - items),
    nested mappings (for phases/tasks arrays of objects).
    """
    if not text.startswith("---"):
        return {}, text

    end = text.find("\n---", 3)
    if end == -1:
        return {}, text

    yaml_str = text[4:end].strip()
    body = text[end + 4:].strip()

    meta = _parse_yaml_block(yaml_str)
    return meta, body


def _parse_yaml_block(text: str) -> dict:
    """Parse a simple YAML block into a dict."""
    result = {}
    lines = text.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        # Skip empty lines and comments
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue

        # Key-value pair
        m = re.match(r'^(\w[\w_-]*)\s*:\s*(.*)', line)
        if not m:
            i += 1
            continue

        key = m.group(1)
        value_str = m.group(2).strip()

        # Inline list: [item1, item2]
        if value_str.startswith("["):
            result[key] = _parse_inline_list(value_str)
            i += 1

        # Block list starting on next line
        elif value_str == "" and i + 1 < len(lines) and lines[i + 1].strip().startswith("- "):
            items, i = _parse_block_list(lines, i + 1)
            result[key] = items

        # Quoted string
        elif value_str.startswith('"') and value_str.endswith('"'):
            result[key] = value_str[1:-1]
            i += 1

        # Unquoted scalar
        else:
            result[key] = _parse_scalar(value_str)
            i += 1

    return result


def _parse_inline_list(text: str) -> list:
    """Parse an inline YAML list: [item1, item2, ...]."""
    inner = text.strip("[] \t")
    if not inner:
        return []
    items = []
    for item in re.split(r',\s*', inner):
        item = item.strip().strip('"').strip("'")
        if item:
            items.append(_parse_scalar(item))
    return items


def _parse_block_list(lines: list[str], start: int) -> tuple[list, int]:
    """Parse a block-style YAML list starting at `start`.

    Handles both simple items (- value) and object items (- key: value).
    Returns (items, next_line_index).
    """
    items = []
    i = start
    base_indent = len(lines[i]) - len(lines[i].lstrip())

    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue

        indent = len(line) - len(line.lstrip())
        if indent < base_indent:
            break

        stripped = line.strip()
        if not stripped.startswith("- "):
            if indent <= base_indent:
                break
            # Continuation of previous object item
            if items and isinstance(items[-1], dict):
                m = re.match(r'\s+(\w[\w_-]*)\s*:\s*(.*)', line)
                if m:
                    k, v = m.group(1), m.group(2).strip()
                    if v.startswith("["):
                        items[-1][k] = _parse_inline_list(v)
                    elif v.startswith('"') and v.endswith('"'):
                        items[-1][k] = v[1:-1]
                    else:
                        items[-1][k] = _parse_scalar(v)
            i += 1
            continue

        # Remove the "- " prefix
        content = stripped[2:].strip()

        # Check if this is an object item (- key: value)
        m = re.match(r'(\w[\w_-]*)\s*:\s*(.*)', content)
        if m:
            obj = {}
            k, v = m.group(1), m.group(2).strip()
            if v.startswith("["):
                obj[k] = _parse_inline_list(v)
            elif v.startswith('"') and v.endswith('"'):
                obj[k] = v[1:-1]
            else:
                obj[k] = _parse_scalar(v)

            # Read continuation lines for this object
            i += 1
            while i < len(lines):
                next_line = lines[i]
                if not next_line.strip():
                    i += 1
                    continue
                next_indent = len(next_line) - len(next_line.lstrip())
                if next_indent <= base_indent:
                    break
                next_stripped = next_line.strip()
                if next_stripped.startswith("- "):
                    break
                cm = re.match(r'(\w[\w_-]*)\s*:\s*(.*)', next_stripped)
                if cm:
                    ck, cv = cm.group(1), cm.group(2).strip()
                    if cv.startswith("["):
                        obj[ck] = _parse_inline_list(cv)
                    elif cv.startswith('"') and cv.endswith('"'):
                        obj[ck] = cv[1:-1]
                    else:
                        obj[ck] = _parse_scalar(cv)
                i += 1

            items.append(obj)
        else:
            # Simple list item
            if content.startswith('"') and content.endswith('"'):
                items.append(content[1:-1])
            else:
                items.append(_parse_scalar(content))
            i += 1

    return items, i


def _parse_scalar(text: str) -> object:
    """Parse a YAML scalar value."""
    text = text.strip()
    if text.lower() in ("true", "yes"):
        return True
    if text.lower() in ("false", "no"):
        return False
    if text.lower() in ("null", "~", ""):
        return None
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        pass
    # Strip quotes
    if (text.startswith('"') and text.endswith('"')) or \
       (text.startswith("'") and text.endswith("'")):
        return text[1:-1]
    return text


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Progress calculations
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Markdown to HTML (minimal)
# ---------------------------------------------------------------------------

def format_inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    return text


def md_to_html(content: str) -> str:
    lines = content.split('\n')
    out = []
    in_code = False
    in_list = False

    for line in lines:
        if line.startswith('```'):
            if in_code:
                out.append('</code></pre>')
                in_code = False
            else:
                lang = line[3:].strip() or 'text'
                out.append(f'<pre><code class="language-{lang}">')
                in_code = True
            continue

        if in_code:
            out.append(html.escape(line))
            continue

        if in_list and not line.strip().startswith(('-', '*', '+')) and line.strip():
            out.append('</ul>')
            in_list = False

        if line.startswith('#### '):
            out.append(f'<h4>{format_inline(line[5:].strip())}</h4>')
        elif line.startswith('### '):
            out.append(f'<h3>{format_inline(line[4:].strip())}</h3>')
        elif line.startswith('## '):
            out.append(f'<h2>{format_inline(line[3:].strip())}</h2>')
        elif line.startswith('# '):
            out.append(f'<h1>{format_inline(line[2:].strip())}</h1>')
        elif line.strip().startswith(('-', '*', '+')) and len(line.strip()) > 1:
            if not in_list:
                out.append('<ul>')
                in_list = True
            item = line.strip()[2:].strip() if line.strip()[:2] in ('- ', '* ', '+ ') else line.strip()[1:].strip()
            item = re.sub(r'\[x\]', '<input type="checkbox" checked disabled>', item, flags=re.IGNORECASE)
            item = re.sub(r'\[ \]', '<input type="checkbox" disabled>', item)
            out.append(f'<li>{format_inline(item)}</li>')
        elif not line.strip():
            if in_list:
                out.append('</ul>')
                in_list = False
            out.append('')
        else:
            out.append(f'<p>{format_inline(line)}</p>')

    if in_list:
        out.append('</ul>')
    if in_code:
        out.append('</code></pre>')

    return '\n'.join(out)


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

CSS = """\
:root {
    --bg: #0d1117;
    --bg-secondary: #161b22;
    --bg-tertiary: #21262d;
    --border: #30363d;
    --text: #e6edf3;
    --text-muted: #8b949e;
    --accent: #58a6ff;
    --green: #3fb950;
    --yellow: #d29922;
    --orange: #db6d28;
    --red: #f85149;
    --purple: #a371f7;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
}

.container { max-width: 1400px; margin: 0 auto; padding: 2rem; }

a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }

/* Navigation */
.nav {
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border);
    padding: 0.75rem 2rem;
    position: sticky;
    top: 0;
    z-index: 100;
}
.nav-content {
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.nav-brand { font-weight: 600; color: var(--text); }
.nav-sep { color: var(--text-muted); }
.breadcrumb { display: flex; align-items: center; gap: 0.5rem; }

/* Header */
header {
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border);
}
h1 { font-size: 1.75rem; font-weight: 600; margin-bottom: 0.5rem; }
.subtitle { color: var(--text-muted); }

/* Stats bar */
.stats { display: flex; gap: 2rem; margin-top: 1rem; flex-wrap: wrap; }
.stat { display: flex; align-items: baseline; gap: 0.5rem; }
.stat-value { font-size: 1.5rem; font-weight: 600; }
.stat-label { color: var(--text-muted); }
.stat-complete .stat-value { color: var(--green); }
.stat-progress .stat-value { color: var(--yellow); }
.stat-planned .stat-value { color: var(--text-muted); }

/* Sections */
section { margin-bottom: 2rem; }
h2 { font-size: 1.25rem; font-weight: 600; margin-bottom: 1rem; }

/* Cards */
.card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.25rem;
}

/* In-progress section */
.in-progress-section { margin-bottom: 2rem; }
.work-list { display: flex; flex-direction: column; gap: 0.75rem; }
.work-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.75rem;
    background: var(--bg-tertiary);
    border-radius: 6px;
    text-decoration: none;
    color: var(--text);
}
.work-item:hover { border: 1px solid var(--accent); margin: -1px; text-decoration: none; }
.work-plan {
    background: var(--yellow);
    color: var(--bg);
    padding: 0.125rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    white-space: nowrap;
}
.work-phase { font-weight: 500; }
.work-progress { color: var(--text-muted); font-size: 0.875rem; margin-left: auto; }

/* Plans grid */
.plans-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
    gap: 1rem;
}

.plan-card { transition: border-color 0.2s; }
.plan-card:hover { border-color: var(--accent); }
.plan-card.status-in-progress { border-left: 3px solid var(--yellow); }
.plan-card.status-complete { border-left: 3px solid var(--green); }
.plan-card.status-planned, .plan-card.status-draft { border-left: 3px solid var(--text-muted); }
.plan-card.status-blocked { border-left: 3px solid var(--red); }
.plan-card.status-deferred, .plan-card.status-archived { border-left: 3px solid var(--orange); }

.plan-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
}
.plan-header h3 { font-size: 1.1rem; font-weight: 600; }
.plan-header a { color: var(--text); }
.plan-header a:hover { color: var(--accent); text-decoration: none; }

/* Badges */
.badge {
    font-size: 0.7rem;
    font-weight: 600;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    text-transform: uppercase;
    white-space: nowrap;
}
.badge-complete, .badge-approved, .badge-implemented { background: var(--green); color: var(--bg); }
.badge-in-progress, .badge-active, .badge-review { background: var(--yellow); color: var(--bg); }
.badge-planned, .badge-draft { background: var(--bg-tertiary); color: var(--text-muted); }
.badge-blocked { background: var(--red); color: var(--bg); }
.badge-deferred, .badge-archived, .badge-superseded { background: var(--orange); color: var(--bg); }

/* Progress bar */
.progress-bar {
    height: 6px;
    background: var(--bg-tertiary);
    border-radius: 3px;
    display: flex;
    overflow: hidden;
    margin-bottom: 0.25rem;
}
.progress-complete { background: var(--green); }
.progress-active { background: var(--yellow); }
.progress-text {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-bottom: 0.75rem;
}

/* Phase / task list in cards */
.phase-list { margin-bottom: 0.75rem; }
.phase-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    border-bottom: 1px solid var(--border);
    font-size: 0.875rem;
}
.phase-item:last-child { border-bottom: none; }
.phase-item:hover { background: var(--bg-tertiary); }
.phase-icon { flex-shrink: 0; }
.phase-name { flex: 1; }
.phase-name a { color: var(--text); }
.phase-name a:hover { color: var(--accent); }
.phase-progress-text { color: var(--text-muted); font-size: 0.75rem; }

.plan-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.75rem;
    color: var(--text-muted);
    padding-top: 0.5rem;
    border-top: 1px solid var(--border);
}

/* Plan detail page */
.plan-detail-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.5rem;
}

/* Phase detail page */
.task-table { width: 100%; border-collapse: collapse; }
.task-table th {
    text-align: left;
    padding: 0.75rem;
    border-bottom: 2px solid var(--border);
    font-size: 0.75rem;
    text-transform: uppercase;
    color: var(--text-muted);
}
.task-table td {
    padding: 0.75rem;
    border-bottom: 1px solid var(--border);
}
.task-table tr:hover { background: var(--bg-tertiary); }

/* Checklist progress */
.checklist-bar {
    width: 80px;
    height: 6px;
    background: var(--bg-tertiary);
    border-radius: 3px;
    overflow: hidden;
    display: inline-block;
    vertical-align: middle;
    margin-right: 0.5rem;
}
.checklist-fill { height: 100%; background: var(--green); display: block; }

/* Content area */
.content {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.5rem;
}
.content h1, .content h2, .content h3, .content h4 {
    margin-top: 1.5rem;
    margin-bottom: 0.75rem;
}
.content h1:first-child, .content h2:first-child { margin-top: 0; }
.content p { margin-bottom: 0.75rem; }
.content ul, .content ol {
    margin-bottom: 0.75rem;
    padding-left: 1.5rem;
}
.content li { margin-bottom: 0.25rem; }
.content pre {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1rem;
    overflow-x: auto;
    margin-bottom: 1rem;
}
.content code {
    font-family: 'SF Mono', Consolas, monospace;
    font-size: 0.875rem;
}
.content p code, .content li code {
    background: var(--bg-tertiary);
    padding: 0.125rem 0.375rem;
    border-radius: 3px;
}
.content input[type="checkbox"] { margin-right: 0.5rem; }

/* Tags */
.tags { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.5rem; }
.tag {
    font-size: 0.7rem;
    padding: 0.125rem 0.5rem;
    border-radius: 12px;
    background: var(--bg-tertiary);
    color: var(--text-muted);
}

/* Meta grid */
.meta-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.meta-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1rem;
}
.meta-card h4 {
    font-size: 0.75rem;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.5rem;
}

.generated {
    margin-top: 2rem;
    text-align: center;
    color: var(--text-muted);
    font-size: 0.75rem;
}
"""


# ---------------------------------------------------------------------------
# HTML generation helpers
# ---------------------------------------------------------------------------

def load_config(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, IOError):
        return {}


def status_icon(status: str) -> str:
    return {
        "complete": "&#x2705;",       # green check
        "in-progress": "&#x1F504;",   # arrows
        "planned": "&#x1F4CB;",       # clipboard
        "blocked": "&#x1F6D1;",       # stop sign
        "deferred": "&#x23F8;&#xFE0F;",  # pause
        "draft": "&#x1F4DD;",         # memo
        "active": "&#x1F504;",
        "approved": "&#x2705;",
        "archived": "&#x1F4E6;",
    }.get(status, "&#x1F4CB;")


def badge_html(status: str) -> str:
    label = status.replace("-", " ").replace("_", " ").title()
    return f'<span class="badge badge-{status}">{label}</span>'


def nav_html(config: dict, breadcrumbs: list[tuple[str, str]]) -> str:
    title = config.get("title", "Project Planner")
    crumbs = []
    for name, url in breadcrumbs:
        if url:
            crumbs.append(f'<a href="{url}">{html.escape(name)}</a>')
        else:
            crumbs.append(f'<span>{html.escape(name)}</span>')

    return f'''<nav class="nav">
    <div class="nav-content">
        <span class="nav-brand">{html.escape(title)}</span>
        <span class="nav-sep">/</span>
        <div class="breadcrumb">
            {' <span class="nav-sep">/</span> '.join(crumbs)}
        </div>
    </div>
</nav>'''


def page_html(title: str, body: str, config: dict,
              breadcrumbs: list[tuple[str, str]], depth: int = 0) -> str:
    css_path = "../" * depth + "styles.css"
    site_title = config.get("title", "Project Planner")
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)} - {html.escape(site_title)}</title>
    <link rel="stylesheet" href="{css_path}">
</head>
<body>
    {nav_html(config, breadcrumbs)}
    <div class="container">
        {body}
        <p class="generated">Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>'''


# ---------------------------------------------------------------------------
# Page generators
# ---------------------------------------------------------------------------

def generate_index(plans: list[PlanData], config: dict) -> str:
    """Main dashboard index page."""

    # Sort: in-progress first, then planned, then complete
    order = {"in-progress": 0, "active": 0, "approved": 1, "draft": 1,
             "planned": 1, "complete": 2, "archived": 3, "deferred": 3}
    plans = sorted(plans, key=lambda p: (order.get(overall_plan_status(p), 4), p.name))

    # Aggregate stats
    total_phases = sum(len(p.phases) for p in plans)
    complete_phases = sum(1 for p in plans for ph in p.phases if ph.status == "complete")
    ip_phases = sum(1 for p in plans for ph in p.phases if ph.status == "in-progress")
    planned_phases = total_phases - complete_phases - ip_phases

    # In-progress section
    ip_items = []
    for plan in plans:
        for phase in plan.phases:
            if phase.status == "in-progress":
                tc, tip, tt = phase_progress(phase)
                progress_text = f"{tc}/{tt} tasks" if tt > 0 else ""
                ip_items.append(f'''
                    <a href="{plan.slug}/{phase.slug}.html" class="work-item">
                        <span class="work-plan">{html.escape(plan.title)}</span>
                        <span class="work-phase">Phase {phase.id}: {html.escape(phase.title)}</span>
                        <span class="work-progress">{progress_text}</span>
                    </a>''')

    ip_section = ""
    if ip_items:
        ip_section = f'''
        <section class="in-progress-section card">
            <h2>In Progress</h2>
            <div class="work-list">{''.join(ip_items)}</div>
        </section>'''

    # Plan cards
    cards = []
    for plan in plans:
        status = overall_plan_status(plan)
        pc, pip, pt = plan_progress(plan)

        if pt > 0:
            cpct = (pc / pt) * 100
            ipct = (pip / pt) * 100
            progress = f'''
                <div class="progress-bar">
                    <div class="progress-complete" style="width:{cpct}%"></div>
                    <div class="progress-active" style="width:{ipct}%"></div>
                </div>
                <div class="progress-text">{pc}/{pt} phases complete</div>'''
        else:
            progress = '<div class="progress-text">No phases defined</div>'

        phase_items = []
        for phase in plan.phases[:5]:
            icon = status_icon(phase.status)
            phase_items.append(f'''
                <div class="phase-item">
                    <span class="phase-icon">{icon}</span>
                    <span class="phase-name"><a href="{plan.slug}/{phase.slug}.html">{html.escape(phase.title)}</a></span>
                    <span class="phase-progress-text">{badge_html(phase.status)}</span>
                </div>''')
        if len(plan.phases) > 5:
            phase_items.append(f'<div class="phase-item"><a href="{plan.slug}/">+{len(plan.phases) - 5} more</a></div>')

        phases_html = f'<div class="phase-list">{"".join(phase_items)}</div>' if phase_items else ""

        tags_html = ""
        if plan.tags:
            tag_spans = "".join(f'<span class="tag">{html.escape(str(t))}</span>' for t in plan.tags)
            tags_html = f'<div class="tags">{tag_spans}</div>'

        cards.append(f'''
            <div class="plan-card card status-{status}">
                <div class="plan-header">
                    <h3><a href="{plan.slug}/">{html.escape(plan.title)}</a></h3>
                    {badge_html(status)}
                </div>
                {f'<div class="subtitle">{html.escape(plan.overview)}</div>' if plan.overview else ''}
                {tags_html}
                {progress}
                {phases_html}
                <div class="plan-footer">
                    <span>{len(plan.phases)} phases</span>
                    {f'<span>Updated {plan.updated}</span>' if plan.updated else ''}
                </div>
            </div>''')

    desc = html.escape(config.get("description", ""))

    body = f'''
    <header>
        <h1>{html.escape(config.get("title", "Project Planner"))}</h1>
        {f'<p class="subtitle">{desc}</p>' if desc else ''}
        <div class="stats">
            <div class="stat stat-complete">
                <span class="stat-value">{complete_phases}</span>
                <span class="stat-label">phases complete</span>
            </div>
            <div class="stat stat-progress">
                <span class="stat-value">{ip_phases}</span>
                <span class="stat-label">in progress</span>
            </div>
            <div class="stat stat-planned">
                <span class="stat-value">{planned_phases}</span>
                <span class="stat-label">planned</span>
            </div>
            <div class="stat">
                <span class="stat-value">{len(plans)}</span>
                <span class="stat-label">plans</span>
            </div>
        </div>
    </header>

    {ip_section}

    <section>
        <h2>All Plans</h2>
        <div class="plans-grid">{''.join(cards)}</div>
    </section>'''

    return page_html("Dashboard", body, config,
                     [("Dashboard", None)], depth=0)


def generate_plan_page(plan: PlanData, config: dict) -> str:
    """Plan detail page with phase table."""
    status = overall_plan_status(plan)
    pc, pip, pt = plan_progress(plan)

    if pt > 0:
        cpct = (pc / pt) * 100
        progress_html = f'''
            <div class="progress-bar" style="height:10px;margin-bottom:0.5rem">
                <div class="progress-complete" style="width:{cpct}%"></div>
            </div>
            <div class="progress-text" style="font-size:0.875rem">{pc}/{pt} phases complete ({cpct:.0f}%)</div>'''
    else:
        progress_html = ""

    tags_html = ""
    if plan.tags:
        tag_spans = "".join(f'<span class="tag">{html.escape(str(t))}</span>' for t in plan.tags)
        tags_html = f'<div class="tags">{tag_spans}</div>'

    # Phase table
    rows = []
    for phase in plan.phases:
        tc, tip, tt = phase_progress(phase)
        checklist = f"{tc}/{tt} tasks" if tt > 0 else ""

        # Subtask rollup
        sub_done = sum(t.subtasks.done for t in phase.tasks)
        sub_total = sum(t.subtasks.total for t in phase.tasks)
        subtask_text = ""
        if sub_total > 0:
            pct = (sub_done / sub_total) * 100
            subtask_text = f'''
                <div class="checklist-bar"><span class="checklist-fill" style="width:{pct}%"></span></div>
                {sub_done}/{sub_total}'''

        deps_text = ", ".join(str(d) for d in phase.depends_on) if phase.depends_on else ""

        rows.append(f'''
            <tr>
                <td>{status_icon(phase.status)}</td>
                <td><a href="{phase.slug}.html">Phase {phase.id}: {html.escape(phase.title)}</a></td>
                <td>{badge_html(phase.status)}</td>
                <td>{checklist}</td>
                <td>{subtask_text}</td>
                <td style="color:var(--text-muted)">{html.escape(phase.deliverable)}</td>
            </tr>''')

    body = f'''
    <header>
        <div class="plan-detail-header">
            <h1>{html.escape(plan.title)}</h1>
            {badge_html(status)}
        </div>
        {f'<p class="subtitle">{html.escape(plan.overview)}</p>' if plan.overview else ''}
        {tags_html}
        <div style="margin-top:1rem">{progress_html}</div>
    </header>

    <section>
        <h2>Phases</h2>
        <div class="card" style="padding:0;overflow:hidden">
            <table class="task-table">
                <thead>
                    <tr>
                        <th style="width:40px"></th>
                        <th>Phase</th>
                        <th style="width:120px">Status</th>
                        <th style="width:100px">Tasks</th>
                        <th style="width:140px">Subtasks</th>
                        <th>Deliverable</th>
                    </tr>
                </thead>
                <tbody>{''.join(rows)}</tbody>
            </table>
        </div>
    </section>'''

    return page_html(plan.title, body, config,
                     [("Dashboard", "../index.html"), (plan.title, None)], depth=1)


def generate_phase_page(plan: PlanData, phase: PhaseData, config: dict) -> str:
    """Phase detail page with tasks and content."""
    tc, tip, tt = phase_progress(phase)

    # Task table
    rows = []
    for task in phase.tasks:
        sub_text = ""
        if task.subtasks.total > 0:
            pct = (task.subtasks.done / task.subtasks.total) * 100
            sub_text = f'''
                <div class="checklist-bar"><span class="checklist-fill" style="width:{pct}%"></span></div>
                {task.subtasks.done}/{task.subtasks.total}'''

        deps_text = ", ".join(task.depends_on) if task.depends_on else ""

        rows.append(f'''
            <tr>
                <td>{status_icon(task.status)}</td>
                <td>{html.escape(task.id)}</td>
                <td>{html.escape(task.title)}</td>
                <td>{badge_html(task.status)}</td>
                <td>{sub_text}</td>
                <td style="color:var(--text-muted)">{deps_text}</td>
            </tr>''')

    task_table = ""
    if rows:
        task_table = f'''
        <section>
            <h2>Tasks</h2>
            <div class="card" style="padding:0;overflow:hidden">
                <table class="task-table">
                    <thead>
                        <tr>
                            <th style="width:40px"></th>
                            <th style="width:60px">ID</th>
                            <th>Task</th>
                            <th style="width:120px">Status</th>
                            <th style="width:140px">Subtasks</th>
                            <th>Depends On</th>
                        </tr>
                    </thead>
                    <tbody>{''.join(rows)}</tbody>
                </table>
            </div>
        </section>'''

    # Content
    content_html = ""
    if phase.content:
        content_html = f'''
        <section>
            <h2>Details</h2>
            <div class="content">{md_to_html(phase.content)}</div>
        </section>'''

    # Meta cards
    meta = []
    meta.append(f'''
        <div class="meta-card">
            <h4>Status</h4>
            <div style="display:flex;align-items:center;gap:0.5rem">
                <span style="font-size:1.5rem">{status_icon(phase.status)}</span>
                {badge_html(phase.status)}
            </div>
        </div>''')

    if tt > 0:
        pct = (tc / tt) * 100
        meta.append(f'''
        <div class="meta-card">
            <h4>Task Progress</h4>
            <div class="progress-bar" style="height:8px;margin-bottom:0.5rem">
                <div class="progress-complete" style="width:{pct}%"></div>
            </div>
            <span>{tc}/{tt} tasks complete</span>
        </div>''')

    if phase.deliverable:
        meta.append(f'''
        <div class="meta-card">
            <h4>Deliverable</h4>
            <p>{html.escape(phase.deliverable)}</p>
        </div>''')

    body = f'''
    <header>
        <h1>Phase {phase.id}: {html.escape(phase.title)}</h1>
        <p class="subtitle">Part of <a href="index.html">{html.escape(plan.title)}</a></p>
    </header>

    <div class="meta-grid">{''.join(meta)}</div>

    {task_table}
    {content_html}'''

    return page_html(
        f"Phase {phase.id}: {phase.title} - {plan.title}", body, config,
        [("Dashboard", "../index.html"), (plan.title, "index.html"),
         (f"Phase {phase.id}", None)],
        depth=1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    script_dir = Path(__file__).parent
    plans_dir = script_dir / "Plans"
    output_dir = script_dir / "Dashboard"

    if not plans_dir.exists():
        print("No Plans/ directory found — creating empty dashboard.")
        plans_dir.mkdir(exist_ok=True)

    config = load_config(script_dir / "dashboard-config.json")

    # Clean and recreate output
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    # Write CSS
    (output_dir / "styles.css").write_text(CSS)

    # Parse all plans
    plans = []
    for plan_path in sorted(plans_dir.iterdir()):
        if plan_path.is_dir():
            plan = parse_plan(plan_path)
            if plan:
                plans.append(plan)

    print(f"Parsed {len(plans)} plans")

    # Generate index
    (output_dir / "index.html").write_text(generate_index(plans, config))

    # Generate plan + phase pages
    total_pages = 1
    for plan in plans:
        plan_out = output_dir / plan.slug
        plan_out.mkdir(parents=True, exist_ok=True)

        (plan_out / "index.html").write_text(generate_plan_page(plan, config))
        total_pages += 1

        for phase in plan.phases:
            (plan_out / f"{phase.slug}.html").write_text(
                generate_phase_page(plan, phase, config))
            total_pages += 1

        pc, _, pt = plan_progress(plan)
        status = overall_plan_status(plan)
        print(f"  {plan.name}: {status} ({pc}/{pt} phases)")

    print(f"\nGenerated {total_pages} pages in {output_dir}/")


if __name__ == "__main__":
    main()
