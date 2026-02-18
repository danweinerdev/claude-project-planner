---
name: research
description: "Investigate a topic and produce a structured research document. Triggers: /research, research this, investigate, look into"
---

# /research — Investigate a Topic

## Path Resolution
**Artifacts** (Plans/, Research/, Specs/, etc.) are read from and written to the **planning root**.
Read `planning-config.json` (at repo root) to find the planning root:
- `planningRoot` of `"."` or absent → artifacts at repository root
- `planningRoot` of `"<dir>"` → artifacts under `<dir>/` from repo root
- `planningRoot` of `"/absolute/path"` → artifacts in an external directory (standalone planning repo)

**Templates and schema** (`Shared/`) are read from the **plugin directory**, not from the planning root. The plugin directory contains `commands/`, `agents/`, and `Shared/` as siblings — find it by globbing for `**/commands/research.md` and going one level up.

Run dashboard commands (`make dashboard`) from the planning root directory.

## When to Use
When you need to gather and synthesize information about a topic before making decisions. Good for technology evaluations, understanding existing systems, or exploring unknowns.

## Process

1. **Define Scope**
   - Ask what topic to research and what questions need answering
   - Determine if this is codebase research, external research, or both

2. **Gather Information**
   - Invoke the `researcher` agent with the topic and questions
   - The agent will scan existing artifacts, codebase, and web as needed

3. **Synthesize**
   - Create `Research/<topic-slug>.md` using `Shared/templates/research.md`
   - Organize findings into Context, Key Insights, Sources, Analysis
   - Highlight implications and recommendations
   - List open questions that remain

4. **Link**
   - Add cross-references to related artifacts in the `related` frontmatter field

5. **Regenerate Dashboard**
   - Run `make dashboard` from the planning root to update the HTML dashboard

## Output
```
Research/<topic-slug>.md
```

## Document Structure
See `Shared/templates/research.md`:
- **Context**: Why this research is needed
- **Findings**: Key insights and sources
- **Analysis**: Implications and recommendations
- **Open Questions**: What remains unknown

## Context
- Template: `Shared/templates/research.md`
- Schema: `Shared/frontmatter-schema.md`
- Agent: `researcher`
