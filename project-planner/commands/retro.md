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

**Templates and schema** (`shared/`) are read from the **plugin directory**, not from the planning root. The plugin directory contains `commands/`, `agents/`, and `shared/` as siblings — find it by globbing for `**/commands/research.md` in both the current directory and `~/.claude/plugins/cache/`. If multiple matches are found (e.g., multiple cached plugin versions), sort by version number and use the highest. Then go one level up.

If `dashboard` is `true` in `planning-config.json`, run dashboard commands (`make dashboard`) from the planning root directory.

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
   - Create `Retro/YYYY-MM-DD-<slug>.md` using `shared/templates/retro.md`
   - Date is today's date
   - Fill in: What Went Well, What Could Be Improved, Action Items, Key Metrics, Takeaways
   - Set status to `draft` (user can mark `complete` after review)

4. **Link**
   - Add references to related plans or debriefs in `related` frontmatter

5. **Regenerate Dashboard** (only if `dashboard` is `true` in `planning-config.json`)
   - Run `make dashboard` from the planning root to update the HTML dashboard

## Output
```
Retro/YYYY-MM-DD-<slug>.md
```

## Document Structure
See `shared/templates/retro.md`:
- **What Went Well**: Things to continue doing
- **What Could Be Improved**: Things to change
- **Action Items**: Specific, actionable improvements (checklist)
- **Key Metrics**: Quantitative outcomes
- **Takeaways**: Summary of key lessons

## Context
- Template: `shared/templates/retro.md`
- Schema: `shared/frontmatter-schema.md`
- Retro directory: `Retro/`
