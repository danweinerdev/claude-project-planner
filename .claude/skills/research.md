---
name: research
description: "Investigate a topic and produce a structured research document. Triggers: /research, research this, investigate, look into"
---

# /research — Investigate a Topic

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
   - Create `Research/<topic-slug>.md` using `shared/templates/research.md`
   - Organize findings into Context, Key Insights, Sources, Analysis
   - Highlight implications and recommendations
   - List open questions that remain

4. **Link**
   - Add cross-references to related artifacts in the `related` frontmatter field

## Output
```
Research/<topic-slug>.md
```

## Document Structure
See `shared/templates/research.md`:
- **Context**: Why this research is needed
- **Findings**: Key insights and sources
- **Analysis**: Implications and recommendations
- **Open Questions**: What remains unknown

## Context
- Template: `shared/templates/research.md`
- Schema: `shared/frontmatter-schema.md`
- Agent: `researcher`
