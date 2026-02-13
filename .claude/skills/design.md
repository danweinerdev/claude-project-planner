---
name: design
description: "Create a technical architecture and design document. Triggers: /design, design this, architecture for, technical design"
---

# /design — Technical Architecture Document

## When to Use
When you need to define the technical architecture for a component or system before implementation. Produces a reviewable design document with architecture decisions.

## Process

1. **Gather Context**
   - Ask what component to design
   - Invoke the `researcher` agent to gather context:
     - Related specifications from `Specs/`
     - Existing architecture from `Designs/`
     - Current codebase patterns
   - Review any related research documents

2. **Draft Design**
   - Create `Designs/<ComponentName>/README.md` using `shared/templates/design.md`
   - Document: overview, architecture (components, data flow, interfaces), design decisions (with alternatives considered), error handling, testing strategy, migration plan
   - Set status to `draft`

3. **Review**
   - Invoke the `plan-reviewer` agent to review the design
   - Address critical and major issues
   - Update status to `review` once addressed

4. **Present for Approval**
   - Show the user the review results and final design
   - If approved, set status to `approved`

## Output
```
Designs/<ComponentName>/README.md
```

## Document Structure
See `shared/templates/design.md`:
- **Overview**: Component role in the system
- **Architecture**: Components, data flow, interfaces
- **Design Decisions**: Each with context, options, decision, rationale
- **Error Handling**: Detection, reporting, recovery
- **Testing Strategy**: How to validate
- **Migration / Rollout**: Transition plan

## Context
- Template: `shared/templates/design.md`
- Schema: `shared/frontmatter-schema.md`
- Agents: `researcher`, `plan-reviewer`
