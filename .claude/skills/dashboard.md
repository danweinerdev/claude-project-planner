---
name: dashboard
description: "Regenerate the HTML dashboard from plan artifacts. Triggers: /dashboard, update dashboard, generate dashboard, refresh dashboard"
---

# /dashboard — Regenerate Dashboard

## When to Use
After making changes to plans, specs, designs, or other artifacts and you want the HTML dashboard to reflect current state.

## Process

1. **Pre-check**
   - Verify `generate-dashboard.py` exists
   - Optionally review any recently changed artifacts to confirm frontmatter is valid

2. **Generate**
   - Run `make dashboard` to regenerate all HTML
   - Report the output (number of plans processed, any errors)

3. **Open (optional)**
   - If the user wants to view it, run `make open`
   - Or inform them they can open `Dashboard/index.html` directly

## Output
Regenerated HTML files in `Dashboard/`:
- `index.html` — main overview with stats, in-progress items, plan cards
- `<plan-slug>/index.html` — plan detail with phase/task tables
- `<plan-slug>/<task-slug>.html` — phase detail with checklists and content

## Context
- Generator: `generate-dashboard.py`
- Config: `dashboard-config.json`
- Output: `Dashboard/`
