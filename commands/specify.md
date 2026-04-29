---
name: specify
description: "Write a requirements specification for a feature. Do NOT enter plan mode — this skill produces a spec artifact directly. Triggers: /specify, write spec, specify requirements, requirements for"
---

# /specify — Write Requirements Specification

## Path Resolution
**Artifacts** (Plans/, Research/, Specs/, etc.) are read from and written to the **planning root**.
Read `planning-config.json` (at repo root) to find the planning root:
- `planningRoot` of `"."` or absent → artifacts at repository root
- `planningRoot` of `"<dir>"` → artifacts under `<dir>/` from repo root
- `planningRoot` of `"/absolute/path"` → artifacts in an external directory

**Templates and schema** (`shared/`) are read from the **plugin directory**, not from the planning root. The plugin directory contains `commands/`, `agents/`, and `shared/` as siblings — find it by globbing for `**/commands/research.md` in both the current directory and `~/.claude/plugins/cache/`. If multiple matches are found (e.g., multiple cached plugin versions), sort by version number and use the highest. Then go one level up.

## When to Use
When you need to define the requirements for a feature before designing or implementing it. Produces a testable, reviewable specification.

## Process

1. **Gather Context**
   - Ask what feature to specify
   - Invoke the `sdd-planner:researcher` agent to gather context from existing artifacts and codebase
   - Review any related research or brainstorm documents

2. **Draft Specification**
   - Create `Specs/<FeatureName>/README.md` using `shared/templates/spec.md`
   - Write: overview, goals, non-goals, requirements (functional + non-functional), user stories, acceptance criteria, constraints, dependencies
   - Set status to `draft`

3. **Review**
   - Invoke the `sdd-planner:spec-reviewer` agent to review the specification
   - Address critical and major issues
   - Update status to `review` once addressed

4. **Present for Approval**
   - Show the user the review results and final spec
   - If approved, set status to `approved`

## Output
```
Specs/<FeatureName>/README.md
```

## Document Structure
See `shared/templates/spec.md`:
- **Overview**: Feature purpose
- **Goals / Non-Goals**: Scope boundaries
- **Requirements**: Functional and non-functional
- **User Stories**: As a [user], I want to...
- **Acceptance Criteria**: Testable pass/fail criteria
- **Constraints / Dependencies / Open Questions**

## Context
- Orchestration: `shared/orchestration.md`
- Template: `shared/templates/spec.md`
- Schema: `shared/frontmatter-schema.md`
- Agents: `sdd-planner:researcher`, `sdd-planner:spec-reviewer`
