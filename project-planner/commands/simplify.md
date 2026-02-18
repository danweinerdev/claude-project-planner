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
- `planningRoot` of `"/absolute/path"` → artifacts in an external directory (standalone planning repo)

**Templates and schema** (`Shared/`) are read from the **plugin directory**, not from the planning root. The plugin directory contains `commands/`, `agents/`, and `Shared/` as siblings — find it by globbing for `**/commands/research.md` and going one level up.

## When to Use
After implementation is complete and tests pass. The goal is reducing complexity without changing behavior — making code easier to read, maintain, and extend.

This is distinct from `/implement` (which builds features) and from a regular code review (which catches bugs). Simplification assumes the code works correctly and asks "can this be clearer?"

## Process

1. **Identify Target**
   - Ask what to simplify: specific files, a module, or the output of a recent plan phase
   - If linked to a plan, read the phase doc and debrief to understand what was built
   - If a `planning-config.local.json` exists, read it to find local repo paths

2. **Analyze Complexity**
   Read the target code and identify simplification opportunities:

   **Structural**
   - Functions that do too many things (candidates for splitting)
   - Deep nesting that could be flattened (early returns, guard clauses)
   - Repeated patterns that could be extracted (only if 3+ occurrences)
   - Unnecessary abstractions (wrappers that add no value)

   **Naming**
   - Variables/functions whose names don't match their purpose
   - Abbreviations that hurt readability
   - Inconsistent naming conventions within a module

   **Dead Code**
   - Unused imports, variables, functions
   - Commented-out code
   - Unreachable branches

   **Over-Engineering**
   - Premature abstractions (interfaces with one implementation)
   - Configuration for things that never change
   - Layers that just pass through

3. **Present Findings**
   Show the user what you found, grouped by file. For each finding:
   - What the issue is
   - Why it matters (readability, maintainability, or correctness risk)
   - What the simplification would look like
   - Risk level (safe refactor vs. behavior-affecting change)

4. **Apply Changes**
   With user approval:
   - Make changes one file at a time
   - After each file, run the project's test suite to verify behavior is preserved
   - If tests fail, revert the change and report the failure
   - If no test suite exists, flag this as a risk and ask the user to verify manually

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
