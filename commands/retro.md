---
name: retro
description: "Capture learnings and reflections in a retrospective. Triggers: /retro, retrospective, what did we learn, lessons learned"
---

# /retro — Capture Learnings

## Path Resolution
**Artifacts** (Plans/, Research/, Specs/, etc.) are read from and written to the **planning root**.
Read `planning-config.json` (at repo root) to find the planning root:
- `planningRoot` of `"."` or absent → artifacts at repository root
- `planningRoot` of `"<dir>"` → artifacts under `<dir>/` from repo root
- `planningRoot` of `"/absolute/path"` → artifacts in an external directory (standalone planning repo)

**Templates and schema** (`Shared/`) are read from the **plugin directory** (the project-planner repo loaded via `--plugin-dir`), not from the planning root.

Run dashboard commands (`make dashboard`) from the planning root directory.

## When to Use
After completing a significant piece of work (a plan, a sprint, a milestone) to capture what went well, what could be improved, and action items for the future.

## Process

1. **Determine Scope**
   - Ask what period or work to reflect on
   - Generate a slug for the filename

2. **Gather Input**
   - Ask the user about:
     - What went well
     - What could be improved
     - Any key metrics or outcomes
   - Optionally review recent debriefs from `Plans/*/notes/` for context

3. **Write Retrospective**
   - Create `Retro/YYYY-MM-DD-<slug>.md` using `Shared/templates/retro.md`
   - Date is today's date
   - Fill in: What Went Well, What Could Be Improved, Action Items, Key Metrics, Takeaways
   - Set status to `draft` (user can mark `complete` after review)

4. **Link**
   - Add references to related plans or debriefs in `related` frontmatter

## Output
```
Retro/YYYY-MM-DD-<slug>.md
```

## Document Structure
See `Shared/templates/retro.md`:
- **What Went Well**: Things to continue doing
- **What Could Be Improved**: Things to change
- **Action Items**: Specific, actionable improvements (checklist)
- **Key Metrics**: Quantitative outcomes
- **Takeaways**: Summary of key lessons

## Context
- Template: `Shared/templates/retro.md`
- Schema: `Shared/frontmatter-schema.md`
- Retro directory: `Retro/`
