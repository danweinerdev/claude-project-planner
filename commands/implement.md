---
name: implement
description: "Execute a plan phase — implement tasks, track progress, update statuses. Triggers: /implement, implement this, start phase, execute plan, build this"
---

# /implement — Execute Plan Phase

## Path Resolution
**Artifacts** (Plans/, Research/, Specs/, etc.) are read from and written to the **planning root**.
Read `planning-config.json` (at repo root) to find the planning root:
- `planningRoot` of `"."` or absent → artifacts at repository root
- `planningRoot` of `"<dir>"` → artifacts under `<dir>/` from repo root
- `planningRoot` of `"/absolute/path"` → artifacts in an external directory (standalone planning repo)

**Templates and schema** (`Shared/`) are read from the **plugin directory** (the project-planner repo loaded via `--plugin-dir`), not from the planning root.

Run dashboard commands (`make dashboard`) from the planning root directory.

## When to Use
When a plan is approved and you're ready to implement a phase. This skill orchestrates the implementation: working through tasks in order, updating statuses, checking off subtasks, and recording progress. It bridges the gap between `/plan` (which defines *what* to build) and `/debrief` (which captures *what happened*).

## Process

### 1. Select Phase
- Ask which plan and phase to implement (or infer from context)
- Read the plan README to understand overall context and phase dependencies
- Read the target phase document to get the task list
- Verify prerequisites:
  - Plan status must be `approved` or `active`
  - Phase status must be `planned` or `in-progress` (not `complete`, `blocked`, or `deferred`)
  - Any phases in `depends_on` must be `complete`
- If plan status is `approved`, update it to `active`
- If phase status is `planned`, update it to `in-progress`

### 2. Locate Target Codebase
- Read `planning-config.json` for mode and repository mapping
- If standalone mode with `planMapping`, find the target repo for this plan
- If `planning-config.local.json` exists, read it for local filesystem paths
- Verify the target repo/directory exists and is accessible

### 3. Load Context
- Read related specs from `Specs/` (referenced in plan README `related` field)
- Read related designs from `Designs/`
- Review any previous phase debriefs in `Plans/<PlanName>/notes/` for context from prior phases
- Build a mental model of what this phase needs to deliver

### 4. Execute Tasks
Work through tasks in order (respecting `depends_on`). For each task:

**a. Start Task**
- Update the task's status to `in-progress` in the phase frontmatter
- Read the task section in the phase body for subtasks and notes

**b. Implement**
- Write the code, tests, and configuration needed
- Follow patterns established in the target codebase
- Follow any constraints from specs/designs
- Check off subtask checklists (`- [x]`) in the phase doc as each is completed
- Update the `updated` date in the phase frontmatter

**c. Validate**
- Run the project's test suite after each task
- If tests fail, fix the issue before moving to the next task
- If a test failure can't be resolved after 2 attempts, mark the task as `blocked` with a note explaining why, and move to the next unblocked task

**d. Complete Task**
- When all subtasks are checked off and tests pass, update the task status to `complete`
- Update the `updated` date

### 5. Phase Completion
Once all tasks are complete (or all remaining tasks are blocked):

**All tasks complete:**
- Update phase status to `complete` in both the phase doc and plan README
- Update `updated` dates
- Suggest running `/debrief` to capture what happened

**Some tasks blocked:**
- Keep phase status as `in-progress`
- Present the blocked tasks and their blockers to the user
- Ask how to proceed:
  - Resolve blockers and continue
  - Defer blocked tasks and mark phase as `complete`
  - Mark phase as `blocked`

### 6. Regenerate Dashboard
- Run `make dashboard` from the planning root to update the HTML dashboard

## Task Execution Details

### Working with Subtasks
Phase docs contain subtask checklists under each task heading:
```markdown
## 1.1: Task Title

### Subtasks
- [ ] Implement the data model
- [ ] Add validation logic
- [ ] Write unit tests
```

As you complete each subtask, check it off:
```markdown
- [x] Implement the data model
```

This gives real-time progress visibility in the dashboard.

### Handling Dependencies
Tasks may have `depends_on` in their frontmatter. Process tasks in dependency order:
1. Tasks with no dependencies first
2. Tasks whose dependencies are all `complete` next
3. Skip tasks whose dependencies are `blocked` or `in-progress`

### Resuming Interrupted Work
If a phase is already `in-progress` (from a previous session):
- Read the current state of all tasks
- Identify which tasks are `complete`, `in-progress`, or `planned`
- Resume from the first non-complete task
- Don't redo completed work

## Escalation Rules

These conditions require stopping and asking the user:

1. **Blocked task**: A task can't be completed after 2 attempts. Present the issue and ask for guidance.
2. **Spec ambiguity**: The spec or design doesn't cover a case you've encountered. Ask the user to clarify rather than guessing.
3. **Scope expansion**: Implementation reveals work not captured in the plan. Flag it — don't silently expand scope.
4. **Destructive action**: Any action that would delete data, modify production config, or affect shared systems needs explicit approval.

Everything else is autonomous. Don't ask for confirmation between tasks.

## Output
Updates existing plan artifacts in place:
- Phase doc: task statuses, subtask checklists, `updated` date
- Plan README: phase status, `updated` date

Code changes go to the target repository (not the planning root).

## Context
- Schema: `Shared/frontmatter-schema.md`
- Target plan: `Plans/<PlanName>/`
- Related specs: `Specs/`
- Related designs: `Designs/`
- Prior debriefs: `Plans/<PlanName>/notes/`
- Local repo paths: `planning-config.local.json`
