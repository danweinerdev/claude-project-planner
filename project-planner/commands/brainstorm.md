---
name: brainstorm
description: "Explore possibilities for a problem or opportunity with structured evaluation. Do NOT enter plan mode — this skill produces a brainstorm artifact directly. Triggers: /brainstorm, brainstorm, explore options, what are our options"
---

# /brainstorm — Explore Possibilities

## Path Resolution
**Artifacts** (Plans/, Research/, Specs/, etc.) are read from and written to the **planning root**.
Read `planning-config.json` (at repo root) to find the planning root:
- `planningRoot` of `"."` or absent → artifacts at repository root
- `planningRoot` of `"<dir>"` → artifacts under `<dir>/` from repo root
- `planningRoot` of `"/absolute/path"` → artifacts in an external directory (standalone planning repo)

**Templates and schema** (`Shared/`) are read from the **plugin directory**, not from the planning root. The plugin directory contains `commands/`, `agents/`, and `Shared/` as siblings — find it by globbing for `**/commands/research.md` in both the current directory and `~/.claude/plugins/cache/`, then go one level up.

Run dashboard commands (`make dashboard`) from the planning root directory.

## When to Use
When you need to generate and evaluate multiple approaches to a problem before committing to one. Good for architecture decisions, feature approaches, or tool selection.

## Process

1. **Define Problem**
   - Ask what problem or opportunity to explore
   - Clarify constraints and evaluation criteria

2. **Gather Context**
   - Invoke the `researcher` agent to gather context on the problem space:
     - Check `Research/` and `Brainstorm/` for prior work on related topics
     - Check `Specs/` for related specifications
     - Check `Designs/` for related architecture docs
     - Review the codebase for relevant existing code
   - The agent returns a structured summary of relevant context

3. **Generate Ideas**
   - Build on the context gathered by the researcher
   - Brainstorm multiple approaches (aim for 3-5)
   - For each idea, document: description, pros, cons, effort level
   - Consider both conventional and creative approaches

4. **Evaluate**
   - Create `Brainstorm/<topic-slug>.md` using `Shared/templates/brainstorm.md`
   - Build a comparison matrix against the criteria
   - Make a recommendation with rationale

5. **Link**
   - Add cross-references to related research or specs in `related` frontmatter

6. **Regenerate Dashboard**
   - Run `make dashboard` from the planning root to update the HTML dashboard

## Output
```
Brainstorm/<topic-slug>.md
```

## Document Structure
See `Shared/templates/brainstorm.md`:
- **Problem Statement**: What we're solving
- **Ideas**: Each with description, pros, cons, effort
- **Evaluation**: Comparison matrix
- **Recommendation**: Which approach and why
- **Next Steps**: What to do with the decision

## Context
- Orchestration: `Shared/orchestration.md`
- Template: `Shared/templates/brainstorm.md`
- Schema: `Shared/frontmatter-schema.md`
- Agent: `researcher`
