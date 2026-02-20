---
name: dashboard
description: "Regenerate the HTML dashboard from plan artifacts. Triggers: /dashboard, update dashboard, generate dashboard, refresh dashboard"
---

# /dashboard — Regenerate Dashboard

## Path Resolution
**Artifacts** (Plans/, Research/, Specs/, etc.) are read from and written to the **planning root**.
Read `planning-config.json` (at repo root) to find the planning root:
- `planningRoot` of `"."` or absent → artifacts at repository root
- `planningRoot` of `"<dir>"` → artifacts under `<dir>/` from repo root
- `planningRoot` of `"/absolute/path"` → artifacts in an external directory (standalone planning repo)

**Templates and schema** (`Shared/`) are read from the **plugin directory**, not from the planning root. The plugin directory contains `commands/`, `agents/`, and `Shared/` as siblings — find it by globbing for `**/commands/research.md` in both the current directory and `~/.claude/plugins/cache/`, then go one level up.

Run dashboard commands (`make dashboard`) from the planning root directory.

## When to Use
After making changes to plans, specs, designs, or other artifacts and you want the HTML dashboard to reflect current state.

## Process

1. **Pre-check**
   - Read `planning-config.json` to determine the planning root
   - Verify `generate-dashboard.py` exists in the planning root
   - Optionally review any recently changed artifacts to confirm frontmatter is valid

2. **Generate**
   - If `planningRoot` is `"."` or absent: run `make dashboard`
   - If `planningRoot` is a subdirectory: run `make -C <planningRoot> dashboard`
   - Report the output (number of plans processed, any errors)

3. **Open (optional)**
   - If the user wants to view it, run `make open` (or `make -C <planningRoot> open`)
   - Or inform them they can open `<planningRoot>/Dashboard/index.html` directly

## Output
Regenerated HTML files in `Dashboard/`:
- `index.html` — main overview with stats, in-progress items, plan cards
- `<plan-slug>/index.html` — plan detail with phase/task tables
- `<plan-slug>/<task-slug>.html` — phase detail with checklists and content

## Context
- Generator: `generate-dashboard.py`
- Config: `planning-config.json`
- Output: `Dashboard/`
