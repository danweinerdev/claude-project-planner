---
name: debrief
description: "Write after-action notes for a completed plan phase. Triggers: /debrief, debrief phase, after-action, phase complete"
---

# /debrief — After-Action Phase Notes

## When to Use
When a plan phase has been completed (or substantially completed) and you want to capture what happened: decisions made, deviations from plan, lessons learned, and impact on future phases.

## Process

1. **Identify Target**
   - Ask which plan and phase to debrief (or infer from context)
   - Read the phase document to understand what was planned
   - Read the plan README for overall context

2. **Gather Information**
   - Review the phase's tasks and subtasks for completion status
   - Ask the user about:
     - Key decisions made during implementation
     - What deviated from the original plan
     - Problems encountered and how they were resolved
     - Insights to carry forward

3. **Write Debrief**
   - Create `Plans/<PlanName>/notes/<NN>-<Phase-Name>.md` using `shared/templates/debrief.md`
   - Fill in all sections: Decisions Made, Requirements Assessment, Deviations, Risks & Issues, Lessons Learned, Impact on Subsequent Phases
   - The filename mirrors the phase doc number (e.g., `01-Core-Setup.md` -> `notes/01-Core-Setup.md`)

4. **Update Phase Status**
   - Set the phase status to `complete` in both:
     - The phase doc frontmatter
     - The plan README's `phases[]` array
   - Update `updated` dates

## Output
```
Plans/<PlanName>/notes/<NN>-<Phase-Name>.md
```

## Document Structure
See `shared/templates/debrief.md`:
- **Decisions Made**: Key choices with rationale
- **Requirements Assessment**: Acceptance criteria met/not met
- **Deviations**: What changed from plan and why
- **Risks & Issues Encountered**: Problems and resolutions
- **Lessons Learned**: Insights for the future
- **Impact on Subsequent Phases**: Downstream changes needed

## Context
- Template: `shared/templates/debrief.md`
- Schema: `shared/frontmatter-schema.md`
- Target plan: `Plans/<PlanName>/`
