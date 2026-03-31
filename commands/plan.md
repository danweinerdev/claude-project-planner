---
name: plan
description: "Create a structured implementation plan with phases, tasks, and subtasks. Do NOT enter plan mode — this skill produces plan artifacts directly. Triggers: /plan, create a plan, plan this, implementation plan"
---

# /plan — Create Implementation Plan

## Path Resolution
**Artifacts** (Plans/, Research/, Specs/, etc.) are read from and written to the **planning root**.
Read `planning-config.json` (at repo root) to find the planning root:
- `planningRoot` of `"."` or absent → artifacts at repository root
- `planningRoot` of `"<dir>"` → artifacts under `<dir>/` from repo root
- `planningRoot` of `"/absolute/path"` → artifacts in an external directory (standalone planning repo)

**Templates and schema** (`shared/`) are read from the **plugin directory**, not from the planning root. The plugin directory contains `commands/`, `agents/`, and `shared/` as siblings — find it by globbing for `**/commands/research.md` in both the current directory and `~/.claude/plugins/cache/`. If multiple matches are found (e.g., multiple cached plugin versions), sort by version number and use the highest. Then go one level up.

If `dashboard` is `true` in `planning-config.json`, run dashboard commands (`make dashboard`) from the planning root directory.

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
   - **Every task must have a `verification` field** — a specific answer to "how do we know this work is good and complete?" that names specific behaviors to cover (e.g., "parser handles valid, malformed, and empty input", "endpoint returns 200 with valid payload and 400 with missing fields"). Vague criteria like "works correctly" or test counts are not acceptable — verification means each new or changed behavior has a corresponding check.
   - **Include structural verification:** Read `shared/language-verification.md` and detect the target project language. Include the language-appropriate structural checks (sanitizers, static analysis, type checking) in verification fields where relevant — either per-task or as a dedicated verification task in each phase.
   - Identify dependencies between phases
   - Present the structure to the user for feedback before writing files

3. **Create Plan Files**
   - Create `Plans/New/<PlanName>/README.md` using `shared/templates/plan-readme.md`
   - Create numbered phase docs using `shared/templates/plan-phase.md`
   - Create `Plans/New/<PlanName>/notes/` directory for future debriefs
   - Populate frontmatter with all phase/task metadata
   - Write body content with task details, subtask checklists, verification criteria, and acceptance criteria
   - **Use Mermaid diagrams** in the Architecture section and anywhere visual structure helps — prefer `graph TD` for phase dependencies, `flowchart LR` for data flow, etc. over ASCII art

4. **Review**
   - Invoke the `plan-reviewer` agent to review the complete plan
   - Address any issues raised by the reviewer
   - Update plan status to `approved` once review passes
   - Move the plan folder from `Plans/New/` to `Plans/Ready/` (`git mv Plans/New/<PlanName> Plans/Ready/<PlanName>`)

5. **Regenerate Dashboard** (only if `dashboard` is `true` in `planning-config.json`)
   - Run `make dashboard` from the planning root to update the HTML dashboard

## Output
```
Plans/New/<PlanName>/
├── README.md              # Plan overview with phases in frontmatter
├── 01-Phase-Name.md       # Phase 1 with tasks in frontmatter
├── 02-Phase-Name.md       # Phase 2
├── ...
└── notes/                 # Empty, ready for debriefs
```
On approval, the plan moves to `Plans/Ready/<PlanName>/`.

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
- Orchestration: `shared/orchestration.md`
- Templates: `shared/templates/plan-readme.md`, `shared/templates/plan-phase.md`
- Schema: `shared/frontmatter-schema.md`
- Existing plans: `Plans/New/`, `Plans/Ready/`, `Plans/Active/`, `Plans/Complete/`
- Related specs: `Specs/`
- Related designs: `Designs/`
