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

**Templates and schema** (`shared/`) are read from the **plugin directory**, not from the planning root. The plugin directory contains `commands/`, `agents/`, and `shared/` as siblings — find it by globbing for `**/commands/research.md` in both the current directory and `~/.claude/plugins/cache/`. If multiple matches are found (e.g., multiple cached plugin versions), sort by version number and use the highest. Then go one level up.

## When to Use
When you need an **adversarial** critical review of a planning artifact before committing to it. Good for stress-testing plans before approval, finding gaps in specs, and challenging design assumptions. This is not a structural review (`sdd-planner:plan-reviewer` and `sdd-planner:spec-reviewer` handle that). This skill actively tries to break the thinking.

Think of it as the planning-artifact counterpart to `sdd-planner:blind-spot-finder` (which does the same thing against code diffs): fresh eyes, hostile framing, deliberately looking for what the author *didn't* think about.

## Process

1. **Identify Target**
   - Ask which artifact to analyze (plan, spec, design, or brainstorm)
   - Confirm the artifact path before proceeding

2. **Gather Context**
   Invoke the `sdd-planner:researcher` agent with these instructions:
   - Read the full target artifact
   - Read all documents referenced in its `related` frontmatter
   - Search for any specs, designs, or plans that reference this artifact (by filename or title)
   - Return a structured summary containing:
     - The artifact's content, structure, and key claims
     - Related context that informs analysis (from `related` docs and reverse references)
     - Cross-references, dependencies, and any conflicts between documents

3. **Adversarial Analysis**
   Apply the lenses below to the researcher's summary. The posture is adversarial — you are not checking whether the artifact is well-structured, you are trying to find the thing that will blow up in six weeks. For every finding, produce a **concrete scenario**: a sequence of events, inputs, or conditions that exposes the flaw. "This is risky" is not a finding. "If the downstream service returns a 503 during step 3, the transaction is orphaned and the plan has no cleanup story" is a finding.

   **The Hostile Reader Lens**
   - Read the artifact assuming the author is wrong. Where does the argument crack first?
   - Which claims are asserted without evidence? What happens if each one turns out to be false?
   - What load-bearing assumption is so obvious the author didn't even write it down?

   **The Missing Scenarios Lens**
   - What concrete error cases aren't handled? (Name them: "what if the DB is unreachable at step 2?")
   - What edge cases are dismissed or ignored?
   - What happens under load, at scale, over time, at the boundary, with pathological input?
   - What happens when each external dependency fails independently? When two fail at once?
   - What happens during deploy, rollback, partial rollout, or while the previous version is still running?

   **The Scope Trap Lens**
   - Which tasks look trivial but actually touch many files, systems, or teams?
   - Where is the integration work hidden that no phase accounts for?
   - What dependencies between tasks are implicit?
   - What has to happen in a specific order but isn't marked as ordered?

   **The Alternatives Lens**
   - Is there a dramatically simpler approach the author didn't consider?
   - What would a cynical senior engineer suggest instead?
   - Is this over-engineered for the actual problem? Under-engineered?
   - Is there prior art (internal or external) that the artifact ignores?

   **The Operational Reality Lens**
   - How does this fail in production at 3 AM?
   - What does the on-call runbook look like? Does one exist? Can it?
   - What's the rollback story — is it real, or "revert the deploy and pray"?
   - What monitoring, alerting, or observability is missing?
   - Who maintains this six months from now, with none of the current context?
   - What happens to in-flight data during migration or cutover?

   **The Contradiction Lens**
   - Does anything in the artifact contradict anything in a related doc the researcher surfaced?
   - Does the plan assume something the spec doesn't guarantee?
   - Does the design promise something the plan doesn't schedule work for?

4. **Validate Each Finding**
   Before including a finding, sanity-check it against the researcher's summary:
   - Is the scenario you described actually reachable given what the artifact says?
   - Is the gap you found already addressed in a related document the researcher surfaced?
   - Would the finding hold up if the author pushed back?

   Drop findings you can't defend. A sharp, defensible critique is worth more than a long list of handwaved concerns.

5. **Rate Findings**
   Categorize each finding:
   - **Critical**: Could cause project failure or major rework
   - **Major**: Significant risk that should be addressed before proceeding
   - **Minor**: Worth noting but won't block progress
   - **Question**: Ambiguity that needs clarification, not necessarily a problem

6. **Present Results**
   Show findings grouped by severity, with specific references to the artifact sections they apply to. Each finding should include: the concrete scenario that exposes the flaw, why it matters, and a concrete mitigation or question to resolve it.

7. **Offer to Update**
   Ask the user if they want to:
   - Update the artifact to address critical/major findings
   - Add findings as open questions in the artifact
   - Create a research document to investigate unknowns
   - Proceed as-is with findings acknowledged

## Output
No new artifact is created. This skill produces an inline analysis presented to the user. If the user chooses to update the artifact, modify it in place. If a research document is needed, use the `/research` workflow.

## Context
- Orchestration: `shared/orchestration.md`
- Agent: `sdd-planner:researcher`

## What This Is NOT
- Not a structural review (that's what `sdd-planner:plan-reviewer` and `sdd-planner:spec-reviewer` agents do)
- Not a code review (this operates on planning artifacts, not code — use `/code-review` for code, which dispatches `sdd-planner:blind-spot-finder` for the code equivalent of this skill's lens)
- Not a blocker — findings are advisory, the user decides what to act on
