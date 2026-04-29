---
name: simplify
description: "Post-implementation code cleanup and simplification. Triggers: /simplify, simplify, clean up code, reduce complexity, refactor for clarity"
---

# /simplify — Code Simplification

## Path Resolution
**Artifacts** (Plans/, Research/, Specs/, etc.) are read from and written to the **planning root**.
Read `planning-config.json` (at repo root) to find the planning root:
- `planningRoot` of `"."` or absent → artifacts at repository root
- `planningRoot` of `"<dir>"` → artifacts under `<dir>/` from repo root
- `planningRoot` of `"/absolute/path"` → artifacts in an external directory

**Templates and schema** (`shared/`) are read from the **plugin directory**, not from the planning root. The plugin directory contains `commands/`, `agents/`, and `shared/` as siblings — find it by globbing for `**/commands/research.md` in both the current directory and `~/.claude/plugins/cache/`. If multiple matches are found (e.g., multiple cached plugin versions), sort by version number and use the highest. Then go one level up.

## When to Use
After implementation is complete and tests pass. The goal is reducing complexity without changing behavior — making code easier to read, maintain, and extend.

This is distinct from `/implement` (which builds features) and from a regular code review (which catches bugs). Simplification assumes the code works correctly and asks "can this be clearer?"

## Process

1. **Identify Target**
   - Ask what to simplify: specific files, a module, or the output of a recent plan phase
   - If linked to a plan, read the phase doc and debrief to understand what was built
   - If a `planning-config.local.json` exists, read it to find local repo paths

2. **Analyze Complexity**
   Dispatch `sdd-planner:quality-scanner` in `simplify` mode via the Task tool (use the plugin-namespaced name — bare `quality-scanner` will not resolve). Pass it the target repo path and the target file paths or module. The scanner is intent-blind by design — do not pass plan, spec, or design context. It returns findings grouped by file, each with: what the issue is, why it matters, what the simplification would look like, and the risk level.

   `quality-scanner` already covers the simplification lenses you want here — structural issues, naming, dead code, and over-engineering — under its Maintainability and Over-Engineering lenses. In `simplify` mode it puts extra weight on the Over-Engineering lens.

   Expect the scanner to validate every finding against the full file and the calling context, not just the hunk, so the risk level it reports is grounded in actual usage.

3. **Present Findings**
   Present the `quality-scanner` agent's findings to the user, grouped by file. For each finding:
   - What the issue is
   - Why it matters (readability, maintainability, or correctness risk)
   - What the simplification would look like
   - Risk level (safe refactor vs. behavior-affecting change)

   Never use "pre-existing" to justify deferring or hiding a finding. "Pre-existing" describes origin, not impact. Present findings by what they do to the user, not when they were introduced. The user decides what is worth fixing.

4. **Apply Changes**
   With user approval, dispatch `sdd-planner:code-implementer` agent(s) via the Task tool (use the plugin-namespaced name) to apply the approved changes:
   - For each file (or group of independent files), launch a `sdd-planner:code-implementer` agent with the approved simplifications and the target file path
   - The agent makes the change, then runs the project's test suite to verify behavior is preserved
   - If tests fail, the agent reverts the change and reports the failure
   - If no test suite exists, flag this as a risk and ask the user to verify manually
   - Changes to independent files can be parallelized across multiple `code-implementer` agents; changes that affect shared interfaces must be serialized

5. **Record**
   If this simplification was part of a plan phase:
   - Note what was simplified in the phase debrief (via `/debrief`)
   - Update the phase's task statuses if simplification was a tracked task

## Escalation Rules

Two conditions require stopping and asking the user:

1. **Test failure after change**: The simplification broke something. Present the failure and ask whether to revert or fix.
2. **Behavior change detected**: The simplification would change observable behavior (not just internal structure). Present the change and ask whether to proceed.

Everything else is autonomous — don't ask for confirmation between individual file changes.

## Output
Modifies code files in the target repository. No planning artifacts are created unless the user requests a record of changes.

## What This Is NOT
- Not a feature implementation (use `/implement`)
- Not a bug fix (fix bugs directly)
- Not an optimization (this is about clarity, not performance)
- Not a rewrite (preserve existing structure, just clean it up)

## Context
- Orchestration: `shared/orchestration.md`
- Schema: `shared/frontmatter-schema.md`
- Local repo paths: `planning-config.local.json`
- Agents: `quality-scanner`, `code-implementer`
