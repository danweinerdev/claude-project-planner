---
name: plan
description: "Create a structured implementation plan with phases, tasks, and subtasks. Triggers: /plan, create a plan, plan this, implementation plan"
---

# /plan — Create Implementation Plan

## Path Resolution
**Artifacts** (Plans/, Research/, Specs/, etc.) are read from and written to the **planning root**.
Read `planning-config.json` (at repo root) to find the planning root:
- `planningRoot` of `"."` or absent → artifacts at repository root
- `planningRoot` of `"<dir>"` → artifacts under `<dir>/` from repo root
- `planningRoot` of `"/absolute/path"` → artifacts in an external directory (standalone planning repo)

**Templates and schema** (`Shared/`) are read from the **plugin directory**, not from the planning root. The plugin directory contains `commands/`, `agents/`, and `Shared/` as siblings — find it by globbing for `**/commands/research.md` and going one level up.

Run dashboard commands (`make dashboard`) from the planning root directory.

## When to Use
When you need to break down a feature, project, or initiative into an actionable implementation plan with phases, tasks, and subtasks.

## Process

1. **Gather Context**
   - Ask the user what they want to plan (feature name, scope, goals)
   - Invoke the `researcher` agent to gather context from existing artifacts:
     - Check `Specs/` for related specifications
     - Check `Designs/` for related architecture docs
     - Check `Research/` and `Brainstorm/` for background
     - Check `Plans/` for related or dependent plans
   - Review the codebase for relevant existing code

2. **Draft Plan Structure**
   - Determine the plan name (PascalCase, no spaces)
   - Break work into 3-7 phases, each with a clear deliverable
   - Each phase gets 2-6 tasks
   - **Every task must have a `verification` field** — a specific answer to "how do we know this work is good and complete?" (e.g., "tests pass for X", "endpoint returns Y", "config validated by Z"). Vague criteria like "works correctly" are not acceptable.
   - Identify dependencies between phases
   - Present the structure to the user for feedback before writing files

3. **Create Plan Files**
   - Create `Plans/<PlanName>/README.md` using `Shared/templates/plan-readme.md`
   - Create numbered phase docs using `Shared/templates/plan-phase.md`
   - Create `Plans/<PlanName>/notes/` directory for future debriefs
   - Populate frontmatter with all phase/task metadata
   - Write body content with task details, subtask checklists, verification criteria, and acceptance criteria

4. **Review**
   - Invoke the `plan-reviewer` agent to review the complete plan
   - Address any issues raised by the reviewer
   - Update plan status to `approved` once review passes

5. **Regenerate Dashboard**
   - Run `make dashboard` from the planning root to update the HTML dashboard

## Output
```
Plans/<PlanName>/
├── README.md              # Plan overview with phases in frontmatter
├── 01-Phase-Name.md       # Phase 1 with tasks in frontmatter
├── 02-Phase-Name.md       # Phase 2
├── ...
└── notes/                 # Empty, ready for debriefs
```

## Document Structure

### README.md
See `Shared/frontmatter-schema.md` for the plan frontmatter schema. Body contains:
- **Overview**: What the plan delivers and why
- **Architecture**: High-level technical approach
- **Key Decisions**: Major choices and rationale
- **Dependencies**: External prerequisites

### Phase Docs
See `Shared/frontmatter-schema.md` for the phase frontmatter schema. Body contains:
- **Overview**: What the phase delivers
- **Task sections**: Headed by task ID (e.g., `## 1.1: Task Title`) with subtask checklists
- **Acceptance Criteria**: Phase-level completion criteria

## Context
- Templates: `Shared/templates/plan-readme.md`, `Shared/templates/plan-phase.md`
- Schema: `Shared/frontmatter-schema.md`
- Existing plans: `Plans/`
- Related specs: `Specs/`
- Related designs: `Designs/`
