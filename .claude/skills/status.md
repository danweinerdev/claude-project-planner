---
name: status
description: "Show a quick status summary of all plans and in-progress work. Triggers: /status, show status, what's in progress, project status"
---

# /status — Quick Status Summary

## When to Use
When you want a quick overview of project status without regenerating the dashboard.

## Process

1. **Scan Plans**
   - Read all `Plans/*/README.md` files
   - Extract plan title, status, and phases from frontmatter
   - For each in-progress phase, read the phase doc to get task status

2. **Format Summary**
   Present a concise summary:

   ```
   ## Project Status

   ### In Progress
   - **PlanName** > Phase 2: API Layer (3/5 tasks complete)
   - **OtherPlan** > Phase 1: Setup (1/3 tasks complete)

   ### Plans Overview
   | Plan | Status | Progress |
   |------|--------|----------|
   | PlanName | active | 1/3 phases complete |
   | OtherPlan | active | 0/2 phases complete |
   | DonePlan | complete | 4/4 phases complete |
   ```

3. **Include Recent Activity** (optional)
   - Check git log for recently modified plan files
   - Mention any recently completed phases or debriefs

## Output
Text summary displayed directly — no files created or modified. This is a read-only skill.

## Context
- Plans directory: `Plans/`
- Schema: `shared/frontmatter-schema.md`
