---
name: breakdown
description: "Add detail to existing plan phases — expand tasks, add subtasks, refine estimates. Triggers: /breakdown, break down, expand phase, add detail"
---

# /breakdown — Expand Plan Phase Detail

## Path Resolution
**Artifacts** (Plans/, Research/, Specs/, etc.) are read from and written to the **planning root**.
Read `planning-config.json` (at repo root) to find the planning root:
- `planningRoot` of `"."` or absent → artifacts at repository root
- `planningRoot` of `"<dir>"` → artifacts under `<dir>/` from repo root
- `planningRoot` of `"/absolute/path"` → artifacts in an external directory (standalone planning repo)

**Templates and schema** (`Shared/`) are read from the **plugin directory** (the project-planner repo loaded via `--plugin-dir`), not from the planning root.

Run dashboard commands (`make dashboard`) from the planning root directory.

## When to Use
When a plan phase needs more detail: additional tasks, subtask checklists, implementation notes, or refined acceptance criteria.

## Process

1. **Identify Target**
   - Ask which plan and phase to expand (or infer from context)
   - Read the current phase document
   - Read the plan README for overall context

2. **Analyze Current State**
   - Review existing tasks and subtasks
   - Identify gaps: missing tasks, vague subtasks, unclear criteria
   - Check related specs/designs for requirements that should be reflected

3. **Expand Detail**
   - Add new tasks to the phase frontmatter `tasks[]` array
   - Add subtask checklists (`- [ ]`) under each task section in the body
   - Add implementation notes where helpful
   - Refine acceptance criteria
   - Update the `updated` date in frontmatter

4. **Update Plan README**
   - If new phases were identified during breakdown, add them to the plan README frontmatter
   - Update the `updated` date

5. **Regenerate Dashboard**
   - Run `make dashboard` from the planning root to update the HTML dashboard

## Output
Updates existing phase document(s) in place. No new files created unless new phases are needed.

## Document Structure
Follows the same structure as phase docs — see `Shared/frontmatter-schema.md`.

Task sections in the body:
```markdown
## 1.1: Task Title

### Subtasks
- [ ] Specific implementation step
- [ ] Another step

### Notes
Implementation guidance, edge cases, etc.
```

## Context
- Schema: `Shared/frontmatter-schema.md`
- Target plan: `Plans/<PlanName>/`
