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

**Templates and schema** (`Shared/`) are read from the **plugin directory**, not from the planning root. The plugin directory contains `commands/`, `agents/`, and `Shared/` as siblings — find it by globbing for `**/commands/research.md` in both the current directory and `~/.claude/plugins/cache/`, then go one level up.

Run dashboard commands (`make dashboard`) from the planning root directory.

## When to Use
When a plan phase needs more detail: additional tasks, subtask checklists, implementation notes, or refined acceptance criteria.

## Process

1. **Identify Target**
   - Ask which plan and phase to expand (or infer from context)
   - Read the current phase document
   - Read the plan README for overall context

2. **Load Context**
   - Read related specs from `Specs/` for requirements that should be reflected
   - Read related designs from `Designs/` for architectural constraints, component boundaries, and interfaces
   - Review existing tasks and subtasks
   - Identify gaps: missing tasks, vague subtasks, unclear criteria

3. **Expand Detail**
   - Add new tasks to the phase frontmatter `tasks[]` array
   - **Every task must have a `verification` field** — a specific answer to "how do we know this work is good and complete?" (e.g., "unit tests pass for parser module", "API returns 200 with valid payload", "migration runs idempotently"). Audit existing tasks and add `verification` to any that lack it.
   - **Structural verification:** Read `Shared/language-verification.md` and detect the project language. Include the appropriate structural checks (sanitizers, static analysis, type checking) in task verification fields — either per-task or as a dedicated final verification task. These run during implementation, not as deferred acceptance criteria.
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
- Related specs: `Specs/`
- Related designs: `Designs/`
