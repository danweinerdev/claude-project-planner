---
name: brainstorm
description: "Explore possibilities for a problem or opportunity with structured evaluation. Triggers: /brainstorm, brainstorm, explore options, what are our options"
---

# /brainstorm — Explore Possibilities

## When to Use
When you need to generate and evaluate multiple approaches to a problem before committing to one. Good for architecture decisions, feature approaches, or tool selection.

## Process

1. **Define Problem**
   - Ask what problem or opportunity to explore
   - Clarify constraints and evaluation criteria

2. **Generate Ideas**
   - Brainstorm multiple approaches (aim for 3-5)
   - For each idea, document: description, pros, cons, effort level
   - Consider both conventional and creative approaches

3. **Evaluate**
   - Create `Brainstorm/<topic-slug>.md` using `shared/templates/brainstorm.md`
   - Build a comparison matrix against the criteria
   - Make a recommendation with rationale

4. **Link**
   - Add cross-references to related research or specs in `related` frontmatter

## Output
```
Brainstorm/<topic-slug>.md
```

## Document Structure
See `shared/templates/brainstorm.md`:
- **Problem Statement**: What we're solving
- **Ideas**: Each with description, pros, cons, effort
- **Evaluation**: Comparison matrix
- **Recommendation**: Which approach and why
- **Next Steps**: What to do with the decision

## Context
- Template: `shared/templates/brainstorm.md`
- Schema: `shared/frontmatter-schema.md`
