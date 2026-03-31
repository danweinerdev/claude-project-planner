# Frontmatter Schema

Single source of truth for all artifact metadata in this project.

## Common Fields

Every artifact includes these fields:

```yaml
title: "Human-readable title"
type: research | brainstorm | spec | design | plan | phase | debrief | retro
status: <type-specific, see below>
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tag1, tag2]
related: [path/to/related/artifact]
```

## Status Values by Type

| Type | Statuses |
|------|----------|
| research | `draft`, `active`, `archived` |
| brainstorm | `draft`, `active`, `archived` |
| spec | `draft`, `review`, `approved`, `implemented`, `superseded` |
| design | `draft`, `review`, `approved`, `implemented`, `superseded` |
| plan | `draft`, `approved`, `active`, `complete`, `archived` |
| phase | `planned`, `in-progress`, `complete`, `blocked`, `deferred` |
| task | `planned`, `in-progress`, `complete`, `blocked`, `deferred` |
| debrief | `draft`, `complete` |
| retro | `draft`, `complete` |

## Plan Schema

### Plan README.md

```yaml
---
title: "Plan Title"
type: plan
status: active
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tag1, tag2]
related: [Specs/FeatureName, Designs/ComponentName]
phases:
  - id: 1
    title: "Phase Title"
    status: planned
    doc: "01-Phase-Title.md"
  - id: 2
    title: "Phase Title"
    status: planned
    doc: "02-Phase-Title.md"
    depends_on: [1]
---
```

Body contains: Overview, Architecture, Key Decisions, Dependencies.
No status tables in the body — the dashboard reads phases from frontmatter.

### Phase Doc (01-Phase-Title.md)

```yaml
---
title: "Phase Title"
type: phase
plan: PlanName
phase: 1
status: in-progress
created: YYYY-MM-DD
updated: YYYY-MM-DD
deliverable: "What this phase delivers"
tasks:
  - id: "1.1"
    title: "Task title"
    status: planned
    verification: "How we know this task is good and complete"
  - id: "1.2"
    title: "Task title"
    status: planned
    depends_on: ["1.1"]
    verification: "Specific criteria to confirm correctness"
---
```

#### Task Fields

| Field | Required | Description |
|-------|----------|-------------|
| `id` | yes | Task identifier (e.g., "1.1") |
| `title` | yes | Human-readable task title |
| `status` | yes | Task status (see status values above) |
| `depends_on` | no | List of task IDs this task depends on |
| `verification` | yes | How we know the work is good and complete — name each new or changed behavior to cover, not test counts |

Body contains task detail sections keyed by task ID as headings:

```markdown
## 1.1: Task Title

### Subtasks
- [ ] Subtask one
- [ ] Subtask two

### Notes
Implementation notes...
```

## Dashboard Color Mapping

- `complete` / `approved` / `implemented` -> green
- `in-progress` / `active` / `review` -> amber
- `planned` / `draft` -> gray
- `blocked` -> red
- `deferred` / `archived` / `superseded` -> muted
