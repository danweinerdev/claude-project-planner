---
name: code-review
description: "Review implementation code against the plan for drift, gaps, and blind spots. Triggers: /code-review, review code, check implementation, compare to plan, code vs plan"
---

# /code-review — Implementation Code Review

## Path Resolution
**Artifacts** (Plans/, Research/, Specs/, etc.) are read from and written to the **planning root**.
Read `planning-config.json` (at repo root) to find the planning root:
- `planningRoot` of `"."` or absent → artifacts at repository root
- `planningRoot` of `"<dir>"` → artifacts under `<dir>/` from repo root
- `planningRoot` of `"/absolute/path"` → artifacts in an external directory (standalone planning repo)

**Templates and schema** (`Shared/`) are read from the **plugin directory**, not from the planning root. The plugin directory contains `commands/`, `agents/`, and `Shared/` as siblings — find it by globbing for `**/commands/research.md` in both the current directory and `~/.claude/plugins/cache/`, then go one level up.

Run dashboard commands (`make dashboard`) from the planning root directory.

## When to Use
During or after implementation of a plan phase, when you want to verify that the actual code matches what was planned. This skill bridges the gap between planning artifacts and real code — it reads git diffs and compares them against the plan, specs, and designs to surface drift, missing work, unplanned additions, unchecked assumptions, and things the planning stages didn't anticipate.

Use this:
- Mid-phase: to course-correct before implementation drifts further
- End-of-phase: before running `/debrief`, to have a clear picture of what happened vs. what was planned
- After resuming work: to re-orient on where things stand
- Before merging: to ensure the branch delivers what the plan promised

## Process

### 1. Identify Target
- Ask which plan and phase to review (or infer from context — look for plans with status `active` and phases with status `in-progress`)
- If not specified, scan `Plans/*/README.md` for the active plan and find the in-progress phase
- Read the plan README to understand overall context, architecture, and key decisions
- Read the target phase document for task list, subtasks, acceptance criteria, and deliverable

### 2. Locate Target Codebase
- Read `planning-config.json` for mode and repository mapping
- If standalone mode with `planMapping`, find the target repo for this plan
- If `planning-config.local.json` exists, read it for local filesystem paths
- Verify the target repo/directory exists and is accessible

### 3. Gather the Diff
Collect the full picture of code changes for this phase:

**a. Working changes**
- Run `git status` in the target repo to see uncommitted changes
- Run `git diff` for unstaged changes and `git diff --cached` for staged changes

**b. Committed changes**
- Determine the commit range for this phase's work. Strategies (try in order):
  1. If the user specifies a branch or commit range, use that
  2. If the phase doc has a `created` date, find the earliest commit on or after that date that touches relevant files
  3. If the plan has a tracking branch, diff against the base branch
  4. Ask the user for the base commit or branch to compare against
- Run `git log --oneline` for the commit range to understand the progression
- Run `git diff <base>..<head>` for the cumulative diff

**c. Scope summary**
- Report how many files changed, lines added/removed, commits included
- List the files changed so the user can verify the scope is correct before proceeding

### 4. Load Planning Context
Read all relevant planning artifacts:
- **Plan README**: `Plans/<PlanName>/README.md` — architecture, key decisions, phase list
- **Phase doc**: `Plans/<PlanName>/<NN>-<Phase-Name>.md` — tasks, subtasks, deliverable, acceptance criteria
- **Related specs**: from the plan's `related` frontmatter — requirements, user stories, acceptance criteria
- **Related designs**: from the plan's `related` frontmatter — architecture, components, interfaces, error handling
- **Prior debriefs**: `Plans/<PlanName>/notes/` — lessons from earlier phases, known issues carried forward

### 5. Invoke Code Reviewer Agent
Pass the planning context and diff information to the `code-reviewer` agent for analysis. The agent evaluates the code through five lenses:

1. **Plan Accuracy** — Does the code implement what the plan describes?
2. **Drift Detection** — What's in the code but not in the plan (and vice versa)?
3. **Quality & Improvement Opportunities** — Missing error handling, edge cases, new or changed behaviors without corresponding tests
4. **Structural Verification** — Read `Shared/language-verification.md` and check whether the language-appropriate structural checks (sanitizers, static analysis, type checking) were included in task verification and actually run. Flag if the plan specified them but they weren't executed, or if the project language warrants them but they were never planned.
5. **Assumption Verification** — Hardcoded values, implicit dependencies, unvalidated assumptions
6. **Planning Blind Spots** — Things the code had to handle that the plan didn't anticipate

### 6. Present Findings
Show the review results to the user, organized by lens and severity:
- **Critical**: Blocks the phase — must fix before considering the phase complete
- **Major**: Significant gap between plan and code — should address
- **Minor**: Worth noting but not blocking
- **Question**: Needs clarification from the user or team

### 7. Offer Next Steps
Based on findings, suggest appropriate actions:

**If alignment is strong:**
- Proceed to `/debrief` to capture the phase outcome
- Note any minor items for the debrief

**If drift is detected:**
- Fix the code to match the plan, OR
- Update the plan to reflect intentional changes (scope was wrong)
- Document the deviation rationale

**If planning blind spots are found:**
- Update specs/designs to account for discovered complexity
- Add tasks to the current or a future phase
- Create a research document for unknowns that need investigation

**If assumptions need checking:**
- Present the assumption checklist for the user to verify
- Flag any that could cause issues if wrong

## Output
No new artifact is created. This skill produces an inline review presented to the user. If the user wants to record findings:
- Significant drift or blind spots should be captured in the phase debrief (via `/debrief`)
- Planning gaps should be addressed by updating the relevant spec, design, or plan
- Unresolved questions can be added as open questions in the relevant artifact

## What This Is NOT
- Not a general code review (style, formatting, best practices) — focuses specifically on plan alignment
- Not `/poke-holes` (which analyzes planning artifacts, not code)
- Not `/simplify` (which improves code clarity, not plan compliance)
- Not a substitute for tests — assumes the test suite validates correctness independently

## Context
- Orchestration: `Shared/orchestration.md`
- Schema: `Shared/frontmatter-schema.md`
- Target plan: `Plans/<PlanName>/`
- Related specs: `Specs/`
- Related designs: `Designs/`
- Prior debriefs: `Plans/<PlanName>/notes/`
- Local repo paths: `planning-config.local.json`
- Agent: `code-reviewer`
