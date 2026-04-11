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

**Templates and schema** (`shared/`) are read from the **plugin directory**, not from the planning root. The plugin directory contains `commands/`, `agents/`, and `shared/` as siblings — find it by globbing for `**/commands/research.md` in both the current directory and `~/.claude/plugins/cache/`. If multiple matches are found (e.g., multiple cached plugin versions), sort by version number and use the highest. Then go one level up.

If `dashboard` is `true` in `planning-config.json`, run dashboard commands (`make dashboard`) from the planning root directory.

## When to Use
During or after implementation of a plan phase, when you want to verify that the actual code matches what was planned. This skill bridges the gap between planning artifacts and real code — it reads git diffs and compares them against the plan, specs, and designs to surface drift, missing work, unplanned additions, unchecked assumptions, and things the planning stages didn't anticipate.

Use this:
- Mid-phase: to course-correct before implementation drifts further
- End-of-phase: before running `/debrief`, to have a clear picture of what happened vs. what was planned
- After resuming work: to re-orient on where things stand
- Before merging: to ensure the branch delivers what the plan promised

## Process

The primary context does as little as possible here. Its job is to identify the **review target** — just enough references for the `code-reviewer` orchestrator to do the heavy lifting in its own fresh context. Primary does **not** load diffs, read planning artifacts, or walk directories. All of that happens inside the orchestrator.

### 1. Identify the Review Target
Collect exactly these pieces of information:

- **Plan and phase**: ask the user, or infer from context. If inferring, list `Plans/Active/*/README.md` (filenames only — do **not** read them) and pick the single active plan if there is one. If ambiguous, ask. Capture:
  - Plan path (e.g., `Plans/Active/<PlanName>/README.md`)
  - Phase doc path (e.g., `Plans/Active/<PlanName>/<NN>-<Phase-Name>.md`)
- **Target repo path**: look up `planning-config.json` → `planMapping` for this plan, then `planning-config.local.json` → `repositories.<key>.path` for the absolute path. If the local config doesn't exist or doesn't have an entry, ask the user where the code lives.
- **Diff scope**: if the user specified a branch, commit range, or "working + staged", record that verbatim. If they didn't, record "orchestrator to determine" — the orchestrator will figure it out from the phase's `created` date or by asking.

Do not read the plan README, phase doc, specs, or designs in the primary context. Do not run `git diff`, `git log`, or `git status` in the primary context. The orchestrator handles all of this.

### 2. Dispatch the `code-reviewer` Orchestrator
Launch the `code-reviewer` agent via the Task tool with a minimal prompt containing only:

- The plan path
- The phase doc path
- The target repo path
- The diff scope (or "determine from phase created date")
- A note if the user wants the review limited to a specific subset (e.g., "only files matching X")

The orchestrator runs in a fresh context. Inside that context it will:
1. Read the plan README and phase doc to find `related` specs, designs, and prior debriefs
2. Resolve the diff scope and load the actual diffs via `git`
3. Read `shared/language-verification.md` if structural verification is relevant
4. Dispatch the **four specialized reviewers in parallel**, each receiving only the inputs for its lane:

   | Agent | Sees | Role |
   |---|---|---|
   | `drift-detector` | Diff + plan + phase doc + prior debriefs | Missing work, scope creep, approach drift |
   | `quality-scanner` | Diff + code only (intent-blind) | Correctness, safety, maintainability, testing, over-engineering |
   | `spec-compliance` | Diff + specs + designs | Requirements coverage, contract violations |
   | `blind-spot-finder` | Diff only | Adversarial fresh-eyes, scenarios no one anticipated |

5. Synthesize the four reports into a unified review that:
   - **Confirms** findings multiple reviewers caught independently
   - **Surfaces disagreements** between reviewers
   - **Highlights unique blind-spot findings** no other reviewer caught
   - Deduplicates overlapping findings and promotes cross-validated Questions to full findings

6. Return the complete synthesized report — including the raw sub-reports verbatim — back to the primary context.

The primary context never sees the raw diffs, the full plan/spec/design content, or the individual reviewer outputs in its own window. That stays inside the orchestrator's context. Primary only receives the final report.

### 3. Present Findings
The `code-reviewer` orchestrator returns a complete self-contained report — synthesis plus the raw reports from all four sub-reviewers. Show that full report to the user; do **not** re-summarize it. The synthesis is already the summary, and the raw reports are the evidence the user may want to drill into. Your job here is to render, not to condense.

The report is structured to lead with:
1. **Overall verdict** and top items to address
2. **Confirmed findings** (caught by 2+ reviewers — high confidence)
3. **Disagreements** between reviewers — these often reveal that planning artifacts are out of sync with each other or with reality
4. **Blind spots only `blind-spot-finder` caught** — explicitly call these out; they exist precisely because intent-aware reviewers forgave them
5. Per-lane findings (drift / quality / spec compliance) not already covered above
6. Open questions that need human judgment

Severity levels:
- **Critical**: Blocks the phase — must fix before considering the phase complete
- **Major**: Significant gap — should address
- **Minor**: Worth noting but not blocking
- **Question**: Needs clarification from the user or team

Never use "pre-existing" to justify deferring or hiding a finding. "Pre-existing" describes origin, not impact. Present findings by what they do to the user, not when they were introduced. The user decides what is worth fixing.

### 4. Offer Next Steps
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
- Orchestration: `shared/orchestration.md`
- Schema: `shared/frontmatter-schema.md`
- Target plan: `Plans/Active/<PlanName>/`
- Related specs: `Specs/`
- Related designs: `Designs/`
- Prior debriefs: `Plans/Active/<PlanName>/notes/`
- Local repo paths: `planning-config.local.json`
- Orchestrator agent: `code-reviewer`
- Specialized reviewers: `drift-detector`, `quality-scanner`, `spec-compliance`, `blind-spot-finder`
