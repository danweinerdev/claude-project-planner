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

**Templates and schema** (`Shared/`) are read from the **plugin directory**, not from the planning root. The plugin directory contains `commands/`, `agents/`, and `Shared/` as siblings — find it by globbing for `**/commands/research.md` and going one level up.

Run dashboard commands (`make dashboard`) from the planning root directory.

## When to Use
When a plan is approved and you're ready to implement a phase. This skill **coordinates** implementation: it delegates actual code work to `code-implementer` agents, runs them in parallel where dependencies allow, triggers `code-reviewer` agents after each task, and manages the review-fix cycle. It bridges the gap between `/plan` (which defines *what* to build) and `/debrief` (which captures *what happened*).

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

### 4. Build Dependency Graph & Execute in Waves

Analyze the phase's task list and `depends_on` fields to identify **waves** — groups of tasks that can run concurrently:

```
Wave 1: Tasks with no dependencies (e.g., 1.1, 1.2, 1.3)
Wave 2: Tasks depending only on Wave 1 tasks (e.g., 1.4 depends on 1.1)
Wave 3: Tasks depending on Wave 2 tasks
...
```

#### Advisory Overlap Analysis

Before launching each wave, check whether two or more tasks in the same wave might touch the same files (based on their subtask descriptions and the target codebase structure). If overlap is likely, warn the user and offer to serialize those tasks instead of running them in parallel.

#### For Each Wave

**a. Launch implementer agents (parallel)**
- For each task in the wave, launch a `code-implementer` agent via the Task tool
- Each agent receives: task ID, title, subtasks, relevant spec/design context, target codebase path, any notes from prior task debriefs
- Launch all tasks in the wave as concurrent Task tool calls
- Update each task's status to `in-progress` in the phase frontmatter

**b. Collect results**
- As each agent completes, collect: files changed, test results, commit hash, issues
- If an agent reports failure/blockers → mark task `blocked`, record the reason
- If an agent reports success → proceed to review

**c. Review completed tasks**
- For each successfully completed task, invoke the `code-reviewer` agent
- Scope the review to that task's changes (pass the file list and commit from the implementer's report)
- The reviewer evaluates against the plan/specs/designs

**d. Process review findings**
- **Critical findings** → resume the `code-implementer` agent to address the issue, then re-review
- **Non-critical findings** (Major/Minor/Question) → collect and present to user after the wave completes
- Maximum 2 review-fix cycles per task. If critical issues remain after 2 cycles, mark the task as `needs-attention` and move on.

**e. Finalize wave**
- Update completed task statuses to `complete`
- Check off subtask checklists (`- [x]`) in the phase doc
- Update the `updated` date in the phase frontmatter
- Present non-critical findings summary to user
- Ask user for decisions on any findings requiring human judgment
- Proceed to next wave

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

As agents complete each subtask, the coordinator checks them off:
```markdown
- [x] Implement the data model
```

This gives real-time progress visibility in the dashboard.

### Handling Dependencies
Tasks may have `depends_on` in their frontmatter. The coordinator builds waves from these:
1. Wave 1: Tasks with no dependencies
2. Wave 2: Tasks whose dependencies are all in Wave 1 (and will be complete)
3. Wave 3: Tasks whose dependencies are all in Waves 1-2
4. Skip tasks whose dependencies are `blocked` or `deferred`

### Resuming Interrupted Work
If a phase is already `in-progress` (from a previous session):
- Read the current state of all tasks
- Skip `complete` tasks
- Resume `in-progress` tasks (re-launch their agents)
- Continue with `planned` tasks in dependency order

## Escalation Rules

These conditions require stopping and asking the user:

1. **Blocked task**: An agent can't complete a task after 2 attempts. Present the issue and ask for guidance.
2. **Spec ambiguity**: The spec or design doesn't cover a case encountered during implementation. Ask the user to clarify rather than guessing.
3. **Scope expansion**: Implementation reveals work not captured in the plan. Flag it — don't silently expand scope.
4. **Destructive action**: Any action that would delete data, modify production config, or affect shared systems needs explicit approval.
5. **Unresolvable review findings**: A `code-reviewer` flags critical issues that the implementer can't resolve after 2 review-fix cycles. Escalate to user.
6. **File conflicts**: If parallel tasks in a wave produce conflicting changes to the same files, present the conflict to the user before proceeding.

Everything else is autonomous. Don't ask for confirmation between waves.

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
