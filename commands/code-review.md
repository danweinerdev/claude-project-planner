---
name: code-review
description: "Review implementation code against the plan for drift, gaps, and blind spots. Triggers: /code-review, review code, check implementation, compare to plan, code vs plan"
---

# /code-review — Implementation Code Review

## ⚠️ CONTRACT — READ FIRST

This skill's entire value comes from dispatching four intent-isolated sub-agents in parallel and synthesizing their independent reports. You are the orchestrator.

**You MUST:**
1. Dispatch all four sub-agents via the Task tool, using their **plugin-namespaced** names: `sdd-planner:drift-detector`, `sdd-planner:quality-scanner`, `sdd-planner:spec-compliance`, `sdd-planner:blind-spot-finder`.
2. Dispatch them **in parallel** — a single message containing four Task tool calls.
3. Give each sub-agent only the inputs for its lane. See Step 3 below for the exact input map. Passing extra context destroys the intent isolation that makes the review worthwhile.
4. Wait for all four to return, then synthesize.

**You MUST NOT:**
1. Read the full diff, the phase doc contents, spec contents, or design contents in the primary context and write findings yourself. That is a single-pass review cosplaying as a four-lane review. It is the bug this contract exists to prevent.
2. Skip the Task dispatch because "you already know the answer" after loading context. The answer you'd produce is exactly the single-pass review this skill exists to replace.
3. Fall back to self-synthesis if a Task dispatch fails. If dispatch fails, **STOP** and return a loud error to the user describing which sub-agent failed and why. Do not silently continue.
4. Use bare sub-agent names (`drift-detector`, `quality-scanner`, etc.) in Task calls — plugin agents require the `sdd-planner:` prefix or they will not resolve.

If you find yourself reading a spec file or running `git diff` against the full patch in the primary context, stop. That work belongs in the sub-agents, not here.

## Path Resolution
**Artifacts** (Plans/, Research/, Specs/, etc.) are read from and written to the **planning root**.
Read `planning-config.json` (at repo root) to find the planning root:
- `planningRoot` of `"."` or absent → artifacts at repository root
- `planningRoot` of `"<dir>"` → artifacts under `<dir>/` from repo root
- `planningRoot` of `"/absolute/path"` → artifacts in an external directory (standalone planning repo)

**Templates and schema** (`shared/`) are read from the **plugin directory**, not from the planning root. The plugin directory contains `commands/`, `agents/`, and `shared/` as siblings — find it by globbing for `**/commands/research.md` in both the current directory and `~/.claude/plugins/cache/`. If multiple matches are found (e.g., multiple cached plugin versions), sort by version number and use the highest. Then go one level up.

## When to Use
During or after implementation of a plan phase, when you want to verify that the actual code matches what was planned. This skill dispatches four intent-isolated sub-reviewers against the diff and synthesizes their reports into a single review.

Use this:
- Mid-phase: to course-correct before implementation drifts further
- End-of-phase: before running `/debrief`, to have a clear picture of what happened vs. what was planned
- After resuming work: to re-orient on where things stand
- Before merging: to ensure the branch delivers what the plan promised

## Why four sub-agents

A single reviewer juggling plan, specs, designs, code, and adversarial perspective inevitably forgives code for one reason while missing flaws visible from another angle. Four intent-restricted reviewers preserve the perspective each lane needs:

| Agent | Sees | Doesn't see | Role |
|---|---|---|---|
| `sdd-planner:drift-detector` | Diff + plan + phase doc + prior debriefs | Specs, designs, code-quality heuristics | Missing work, scope creep, approach drift |
| `sdd-planner:quality-scanner` | Diff + code | Plan, specs, designs | Correctness, safety, maintainability, testing, over-engineering — intent-blind |
| `sdd-planner:spec-compliance` | Diff + specs + designs | Plan, phase doc | Requirements coverage, contract violations |
| `sdd-planner:blind-spot-finder` | Diff only | Everything else | Adversarial fresh eyes — scenarios the author didn't consider |

Each runs in its own fresh context. The whole point is that one reviewer's framing cannot contaminate another's.

**`blind-spot-finder`'s diff-only guarantee is the sharpest and most fragile of these.** If you, as the primary orchestrator, read the plan before you dispatch it, your synthesis of its output will inevitably carry plan-aware framing back into the "blind-spot" conclusions. Keep your own reads shallow — file paths only, not contents — until after the sub-agents return.

## Process

### 1. Identify the Review Target

Your goal in this step is to produce four strings: plan path, phase doc path, target repo path, and diff scope. Do NOT read the contents of the plan or phase doc — just their paths.

- **Plan and phase**: ask the user, or infer from context. If inferring, use `Glob` on `Plans/Active/*/README.md` (filenames only — do **not** `Read` them). If there is a single active plan, pick it; if there are multiple, ask. Capture:
  - Plan path (e.g., `Plans/Active/<PlanName>/README.md`)
  - Phase doc path (e.g., `Plans/Active/<PlanName>/<NN>-<Phase-Name>.md`)
- **Target repo path**: read `planning-config.json` for `planMapping` to find the repo key for this plan, then read `planning-config.local.json` for `repositories.<key>.path` to get the absolute local path. If that doesn't resolve, ask the user where the code lives.
- **Diff scope**: if the user specified a branch, commit range, or "working + staged", record that verbatim. Otherwise, record "determine from phase created date" — the sub-agents can resolve it.

### 2. Gather Only What Dispatch Needs

To dispatch the sub-agents with the right inputs, you need a little bit of information from the planning artifacts and the target repo. Keep this step as narrow as possible — read frontmatter, not bodies.

**a. Plan README frontmatter only.** Use `Read` on the plan README, but stop after the frontmatter. Extract the `related` field to get the list of spec paths (under `Specs/`) and design paths (under `Designs/`). **Do not** read the body of the README — the sub-agents will do that.

**b. Prior debrief paths.** Use `Glob` on `Plans/Active/<PlanName>/notes/*.md` to get the list of prior debrief paths. Do not read their contents — `drift-detector` will do that.

**c. Resolve the diff scope.** In the target repo, run `git status` and `git log --oneline -20` to orient. If the user gave an explicit range, use it. If the user said "determine from phase created date", read only the frontmatter of the phase doc to get the `created` date, then find the earliest commit on or after that date. If you still can't resolve, ask the user for a base commit. Capture the scope as a concrete `git diff <base>..<head>` command (plus any `--staged`/working coverage the user requested). **Do not** run `git diff` and read the patch content — the sub-agents will.

**d. Language-verification note (optional).** If `shared/language-verification.md` exists and the project language warrants structural checks, pass a one-line note to `drift-detector` and `quality-scanner` so they can flag missing sanitizers/static-analysis/type-checking work. You do not need to read the full language-verification doc — just detect the project language from a quick file-extension glance at the target repo and include it as context.

At the end of Step 2, you should have:
- Plan path, phase doc path
- Spec paths (list), design paths (list)
- Prior debrief paths (list)
- Target repo path
- Resolved diff scope as a concrete git command/range
- Optional language-verification note

You should NOT have read any spec contents, design contents, diff hunks, or the body of the phase doc.

### 3. Dispatch All Four Sub-Agents in Parallel

**This is the step the contract at the top of this file is about.** Send a single message containing four Task tool calls. Each uses the plugin-namespaced name. Each receives only the inputs for its lane.

**Task call 1 — `sdd-planner:drift-detector`**
- Plan path, phase doc path
- Prior debrief paths
- Target repo path
- Resolved diff scope
- Language-verification note (if applicable)
- ❌ Do NOT pass spec paths, design paths, or any diff content.

**Task call 2 — `sdd-planner:quality-scanner`**
- Target repo path
- Resolved diff scope
- `mode: review`
- Language-verification note (if applicable)
- ❌ Do NOT pass plan path, phase path, spec paths, or design paths. Intent-blindness is the point.

**Task call 3 — `sdd-planner:spec-compliance`**
- Spec paths, design paths
- Target repo path
- Resolved diff scope
- ❌ Do NOT pass plan path or phase path.

**Task call 4 — `sdd-planner:blind-spot-finder`**
- Target repo path
- Resolved diff scope
- ❌ Do NOT pass anything else. Not the plan, not the specs, not the designs, not the phase doc, not even the language-verification note. The diff-only guarantee is this reviewer's entire contribution.

Wait for all four to return before continuing.

**If any Task call fails or returns an error** (e.g., "unknown subagent_type"), stop immediately and return a loud error to the user:

```
ERROR: /code-review could not dispatch sub-agent `sdd-planner:<name>`.
Reason: <the exact error from Task>
The four-lane review cannot proceed. Fix the dispatch issue and re-run.
```

**Do NOT** fall back to self-synthesis. A single-pass review pretending to be a four-lane review is worse than no review at all — it gives the user false confidence in an un-triangulated report.

### 4. Synthesize the Four Reports

Once all four reports are in hand, produce a single unified review. Synthesis is the whole value-add of this step — it is not concatenation.

**a. Build a findings table.** Enumerate every finding from all four reports. For each, record: source agent, severity, location, one-line summary.

**b. Detect agreements.** Findings that multiple reviewers hit independently are high-confidence. Flag them as **Confirmed by N reviewers**. When `drift-detector` says a task is missing and `spec-compliance` says the requirement is uncovered, that's the same hole seen from two angles — strong signal.

**c. Detect disagreements.** When reviewers contradict each other, the disagreement is itself a finding:
- `drift-detector` says the task was completed; `spec-compliance` says the requirement is uncovered. → Plan and spec are out of sync. Surface this.
- `quality-scanner` says the code is fine; `blind-spot-finder` flags a concurrency scenario. → The code is locally correct but globally fragile. Surface both perspectives.
- `drift-detector` says the code is unplanned scope creep; `spec-compliance` says it satisfies a spec requirement. → The plan missed a requirement. Surface as a planning gap.

Disagreements get their own section in the output. Never quietly reconcile them by picking a winner.

**d. Highlight unique blind-spot findings.** Any `blind-spot-finder` finding that **no other reviewer caught** gets promoted into a dedicated "Blind Spots Only `blind-spot-finder` Caught" section. This is explicit recognition of the value the adversarial reviewer adds. If `blind-spot-finder` had zero unique findings, say so — it's a signal the other reviewers were thorough, not a reason to omit the section.

**e. Cross-validate questionable findings.** If a reviewer flagged something as a **Question** (unverified suspicion), check whether any other reviewer's findings corroborate or rule it out. Promote corroborated questions to findings; drop the ones that other reviewers ruled out.

**f. Deduplicate.** When multiple reviewers report the same issue from the same angle, collapse them into one entry and list the sources. Don't double-count in severity tallies.

**Do NOT introduce new findings of your own during synthesis.** Your job is to synthesize what the four sub-agents returned, not to add findings based on your own reading. If you notice something none of the four agents caught, it means one of the agents needs to be improved — note it in an "Orchestrator Observations" addendum rather than silently inserting it as a finding.

### 5. Present the Unified Review to the User

Render the synthesis in the output format below. Include the raw sub-reports verbatim in `<details>` blocks so the user can drill in. Do not re-summarize the sub-reports — the synthesis is the summary, the raw reports are the evidence.

## Output Format

```markdown
## Code Review: [Plan Name] — Phase [N]: [Phase Title]

### Overall Verdict
**Alignment:** Strong | Moderate | Weak
**Critical issues:** [count]
**Top items to address:** [prioritized list of 3–7]

### Diff Scope
- Commits reviewed: [range, count]
- Files changed: [count]
- Reviewers dispatched: sdd-planner:drift-detector, sdd-planner:quality-scanner, sdd-planner:spec-compliance, sdd-planner:blind-spot-finder

### Confirmed Findings (agreed by 2+ reviewers)
These findings were caught independently by multiple lanes — high confidence.

#### [Severity] — [one-line summary]
**Caught by:** drift-detector, spec-compliance
**Location:** `path/to/file.ext:line`
**Detail:** Synthesized description drawing from each reviewer's angle.
**Recommendation:** …

[Repeat]

### Disagreements (reviewers contradict each other)
When reviewers see the same code differently, the disagreement is itself a finding.

#### [one-line summary of the disagreement]
- **drift-detector says:** …
- **spec-compliance says:** …
- **What this means:** e.g., "The plan and the spec are out of sync — one of them needs to be updated to reflect reality."
- **Recommendation:** …

[Repeat]

### Blind Spots Only `blind-spot-finder` Caught
Findings from the adversarial reviewer that no other lane surfaced. Pay these special attention — they exist precisely because intent-aware reviewers forgave them.

#### [Severity] — [one-line summary]
**Location:** `path/to/file.ext:line`
**Scenario:** …
**Recommendation:** …

[Repeat. If there are none, say: "None — the other reviewers covered everything blind-spot-finder surfaced. Either the code is in very good shape or the adversarial reviewer should push harder next time."]

### Drift (from drift-detector)
[Unique findings from drift-detector that weren't confirmed or disagreed elsewhere]

### Quality (from quality-scanner)
[Unique findings from quality-scanner]

### Spec Compliance (from spec-compliance)
[Unique findings from spec-compliance]

### Open Questions
Findings raised as unverified suspicions by one or more reviewers that couldn't be cross-validated. Surface so the user can decide.

- [Question, source agent, context]

### Raw Reports
<details>
<summary>drift-detector report</summary>

[paste the full drift-detector report]
</details>

<details>
<summary>quality-scanner report</summary>

[paste the full quality-scanner report]
</details>

<details>
<summary>spec-compliance report</summary>

[paste the full spec-compliance report]
</details>

<details>
<summary>blind-spot-finder report</summary>

[paste the full blind-spot-finder report]
</details>
```

### 6. Offer Next Steps
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

Never use "pre-existing" to justify deferring or hiding a finding. "Pre-existing" describes origin, not impact. Present findings by what they do to the user, not when they were introduced. The user decides what is worth fixing.

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
- Sub-agents (dispatched via Task from the primary context): `sdd-planner:drift-detector`, `sdd-planner:quality-scanner`, `sdd-planner:spec-compliance`, `sdd-planner:blind-spot-finder`
