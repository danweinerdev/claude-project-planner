---
name: poke-holes
description: "Adversarial critical analysis of plans, specs, or designs. Triggers: /poke-holes, poke holes, find gaps, challenge this, what could go wrong, devil's advocate"
---

# /poke-holes — Adversarial Critical Analysis

## Path Resolution
**Artifacts** (Plans/, Research/, Specs/, etc.) are read from and written to the **planning root**.
Read `planning-config.json` (at repo root) to find the planning root:
- `planningRoot` of `"."` or absent → artifacts at repository root
- `planningRoot` of `"<dir>"` → artifacts under `<dir>/` from repo root
- `planningRoot` of `"/absolute/path"` → artifacts in an external directory (standalone planning repo)

**Templates and schema** (`Shared/`) are read from the **plugin directory**, not from the planning root. The plugin directory contains `commands/`, `agents/`, and `Shared/` as siblings — find it by globbing for `**/commands/research.md` in both the current directory and `~/.claude/plugins/cache/`, then go one level up.

## When to Use
When you need a critical review of an artifact before committing to it. Good for stress-testing plans before approval, finding gaps in specs, or challenging design assumptions. Unlike reviewers (which check for structural quality), this skill actively tries to break the thinking.

## Process

1. **Identify Target**
   - Ask which artifact to analyze (plan, spec, design, or brainstorm)
   - Read the full artifact and any related documents referenced in its `related` frontmatter

2. **Analyze Through Lenses**
   Apply each of these critical lenses to the artifact:

   **Assumptions**
   - What unstated assumptions does this rely on?
   - Which assumptions are most likely to be wrong?
   - What happens if each assumption fails?

   **Missing Scenarios**
   - What error cases aren't handled?
   - What edge cases are ignored?
   - What happens under load, at scale, or over time?
   - What happens when dependencies fail?

   **Scope Risks**
   - Where could scope creep in?
   - What looks simple but is actually complex?
   - What's under-estimated?
   - Are there hidden dependencies between tasks?

   **Alternatives Not Considered**
   - Are there simpler approaches that were overlooked?
   - What would a different team choose and why?
   - Is this over-engineered for the actual problem?

   **Operational Gaps**
   - How does this fail in production?
   - What's the rollback story?
   - What monitoring/observability is missing?
   - What happens when someone unfamiliar needs to maintain this?

3. **Rate Findings**
   Categorize each finding:
   - **Critical**: Could cause project failure or major rework
   - **Major**: Significant risk that should be addressed before proceeding
   - **Minor**: Worth noting but won't block progress
   - **Question**: Ambiguity that needs clarification, not necessarily a problem

4. **Present Results**
   Show findings grouped by severity, with specific references to the artifact sections they apply to. For each finding, suggest a concrete mitigation or question to resolve it.

5. **Offer to Update**
   Ask the user if they want to:
   - Update the artifact to address critical/major findings
   - Add findings as open questions in the artifact
   - Create a research document to investigate unknowns
   - Proceed as-is with findings acknowledged

## Output
No new artifact is created. This skill produces an inline analysis presented to the user. If the user chooses to update the artifact, modify it in place. If a research document is needed, use the `/research` workflow.

## What This Is NOT
- Not a structural review (that's what `plan-reviewer` and `spec-reviewer` agents do)
- Not a code review (this operates on planning artifacts, not code)
- Not a blocker — findings are advisory, the user decides what to act on
