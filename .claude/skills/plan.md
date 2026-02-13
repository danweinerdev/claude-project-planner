---
name: plan
description: "Create a structured implementation plan with phases, tasks, and subtasks. Triggers: /plan, create a plan, plan this, implementation plan"
---

# /plan — Create Implementation Plan

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
   - Identify dependencies between phases
   - Present the structure to the user for feedback before writing files

3. **Create Plan Files**
   - Create `Plans/<PlanName>/README.md` using `shared/templates/plan-readme.md`
   - Create numbered phase docs using `shared/templates/plan-phase.md`
   - Create `Plans/<PlanName>/notes/` directory for future debriefs
   - Populate frontmatter with all phase/task metadata
   - Write body content with task details, subtask checklists, and acceptance criteria

4. **Review**
   - Invoke the `plan-reviewer` agent to review the complete plan
   - Address any issues raised by the reviewer
   - Update plan status to `approved` once review passes

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
See `shared/frontmatter-schema.md` for the plan frontmatter schema. Body contains:
- **Overview**: What the plan delivers and why
- **Architecture**: High-level technical approach
- **Key Decisions**: Major choices and rationale
- **Dependencies**: External prerequisites

### Phase Docs
See `shared/frontmatter-schema.md` for the phase frontmatter schema. Body contains:
- **Overview**: What the phase delivers
- **Task sections**: Headed by task ID (e.g., `## 1.1: Task Title`) with subtask checklists
- **Acceptance Criteria**: Phase-level completion criteria

## Context
- Templates: `shared/templates/plan-readme.md`, `shared/templates/plan-phase.md`
- Schema: `shared/frontmatter-schema.md`
- Existing plans: `Plans/`
- Related specs: `Specs/`
- Related designs: `Designs/`
